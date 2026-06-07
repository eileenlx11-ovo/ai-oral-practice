"""Tencent Cloud SOE New Edition pronunciation provider.

Uses the WebSocket API for Smart Oral Evaluation New Edition. Required env:
TENCENT_APP_ID, TENCENT_SECRET_ID, TENCENT_SECRET_KEY.
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import subprocess
import tempfile
import threading
import time
import uuid
from urllib.parse import quote, urlencode

logger = logging.getLogger("assessment.tencent")

try:
    import websocket
    _HAS_WEBSOCKET = True
except ImportError:
    websocket = None
    _HAS_WEBSOCKET = False

_HOST = "soe.cloud.tencent.com"
_PATH = "/soe/api"
_ENGINE_MODEL_TYPE = "16k_en"
# This VPS → Tencent SOE path has slow, jittery TCP handshakes (2-9s observed),
# so the open timeout is generous. SOE also drops the session if no audio
# arrives within 15s of connect (error 4008), which is why we send the audio
# from inside on_open rather than after a main-thread round-trip.
_OPEN_TIMEOUT_SECONDS = 25
# Total connection attempts on network-class failures (see _is_retryable).
_MAX_ATTEMPTS = 3
# SOE is now only a fallback (Azure is primary). Fail fast instead of hanging:
# a real SOE response arrives in seconds, so a 60s wait just means a dead socket.
_DONE_TIMEOUT_SECONDS = 22


class TencentSOEError(RuntimeError):
    """Raised when Tencent SOE New Edition returns an error."""


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def available() -> bool:
    return (
        _HAS_WEBSOCKET
        and bool(_app_id())
        and bool(_env("TENCENT_SECRET_ID"))
        and bool(_env("TENCENT_SECRET_KEY"))
    )


def _app_id() -> str:
    return _env("TENCENT_APP_ID") or _env("TENCENT_APPID")


async def assess(audio_path: str, reference_text: str) -> dict | None:
    if not available():
        return None
    import asyncio
    return await asyncio.to_thread(_assess_sync, audio_path, reference_text)


def _assess_sync(audio_path: str, reference_text: str) -> dict:
    wav_path = _ensure_wav(audio_path)
    try:
        # The VPS↔SOE path is flaky (slow handshakes, error 4008). Retry the
        # connection a couple of times on network-class failures; the wav is
        # converted once and reused. Non-network errors (bad signature, audio
        # format) are not retried since a retry can't fix them.
        last_exc = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                response = _run_ws_assessment(wav_path, reference_text)
                return _normalize(response)
            except TencentSOEError as exc:
                last_exc = exc
                if not _is_retryable(exc) or attempt == _MAX_ATTEMPTS - 1:
                    raise
                continue
        raise last_exc  # unreachable, but keeps intent explicit
    finally:
        if wav_path != audio_path:
            try:
                os.unlink(wav_path)
            except OSError:
                pass


def _is_retryable(exc: TencentSOEError) -> bool:
    """Network-class SOE failures worth retrying: slow/failed handshake, the
    15s no-audio cutoff (4008), and generic socket timeouts."""
    msg = str(exc)
    return any(s in msg for s in ("4008", "did not open in time",
                                  "timed out", "closed before final"))


def _ensure_wav(audio_path: str) -> str:
    """Convert input audio to 16k mono PCM WAV for SOE New Edition."""
    if audio_path.lower().endswith(".wav"):
        # Already .wav: SOE gets it as-is, ffmpeg is skipped. If the upstream
        # suffix was guessed from a misleading content-type, this could forward
        # non-wav bytes — log the size so that case is visible in the diagnosis.
        logger.info("SOE _ensure_wav: passthrough .wav path=%s size=%dB",
                    audio_path, os.path.getsize(audio_path))
        return audio_path

    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_tmp.close()
    try:
        proc = subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", wav_tmp.name],
            capture_output=True,
            check=True,
        )
        out_size = os.path.getsize(wav_tmp.name)
        # 44-byte WAV header + samples. <100B means an empty/0-duration decode,
        # which SOE scores as completeness 0 (the silent-audio failure mode).
        dur_s = max(0.0, (out_size - 44) / (16000 * 2))
        logger.info("SOE ffmpeg: in=%s -> wav=%dB (~%.2fs) stderr_tail=%s",
                    audio_path, out_size, dur_s,
                    proc.stderr.decode("utf-8", "replace")[-200:])
        return wav_tmp.name
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        try:
            os.unlink(wav_tmp.name)
        except OSError:
            pass
        raise TencentSOEError(f"Audio conversion failed: {exc}") from exc


def _run_ws_assessment(audio_path: str, reference_text: str) -> dict:
    state = {
        "opened": threading.Event(),
        "done": threading.Event(),
        "final": None,
        "error": None,
    }

    # Pre-read so we can fire the audio the instant the socket opens — SOE
    # closes the session if no audio lands within 15s of connect (error 4008),
    # and this VPS's connect latency eats much of that window.
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    def on_open(ws):
        try:
            # websocket-client's WebSocketApp exposes send(data, opcode), not
            # send_binary (that's only on the lower-level WebSocket/ws.sock).
            ws.send(audio_bytes, websocket.ABNF.OPCODE_BINARY)
            ws.send(json.dumps({"type": "end"}), websocket.ABNF.OPCODE_TEXT)
        except Exception as exc:
            state["error"] = TencentSOEError(f"Failed to send audio: {exc}")
            state["done"].set()
            ws.close()
            return
        logger.info("SOE on_open: sent %dB audio + end frame", len(audio_bytes))
        state["opened"].set()

    def on_message(ws, message):
        # Log every frame SOE returns — this is the single most useful signal for
        # the "0 score" diagnosis (reveals code, message, and completeness).
        logger.info("SOE on_message: %s", message[:500])
        try:
            payload = json.loads(message)
        except json.JSONDecodeError as exc:
            state["error"] = TencentSOEError(f"Invalid SOE JSON response: {exc}")
            state["done"].set()
            ws.close()
            return

        if payload.get("code", 0) != 0:
            state["error"] = TencentSOEError(
                f"Tencent SOE error code={payload.get('code')} message={payload.get('message')}"
            )
            state["done"].set()
            ws.close()
            return

        if payload.get("final") == 1:
            state["final"] = payload
            state["done"].set()
            ws.close()

    def on_error(ws, error):
        state["error"] = TencentSOEError(str(error))
        state["done"].set()

    def on_close(ws, *args):
        if state["final"] is None and state["error"] is None:
            state["error"] = TencentSOEError("Tencent SOE websocket closed before final result")
            state["done"].set()

    ws = websocket.WebSocketApp(
        _signed_url(reference_text),
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()

    # Audio is sent inside on_open; this just confirms the socket opened and
    # the send succeeded before we wait for the final result.
    if not state["opened"].wait(_OPEN_TIMEOUT_SECONDS):
        ws.close()
        if state["error"] is not None:
            raise state["error"]
        raise TencentSOEError("Tencent SOE websocket did not open in time")

    if not state["done"].wait(_DONE_TIMEOUT_SECONDS):
        ws.close()
        raise TencentSOEError("Tencent SOE websocket timed out waiting for final result")

    if state["error"] is not None:
        raise state["error"]
    if state["final"] is None:
        raise TencentSOEError("Tencent SOE did not return a final result")
    return state["final"]


def _signed_url(reference_text: str) -> str:
    appid = _app_id()
    secret_id = _env("TENCENT_SECRET_ID")
    secret_key = _env("TENCENT_SECRET_KEY")

    # IPA mode makes PhoneInfos[].Phone an international phonetic symbol.
    # The {::cmd{...}} prefix must NOT affect eval_mode (word vs sentence),
    # so compute eval_mode from the original text. Once the prefix lands in
    # params["ref_text"], both signing (raw value) and URL (urlencoded) read
    # the same string, so encoding stays consistent.
    eval_mode = _eval_mode(reference_text)
    ref_text = reference_text
    if _ipa_enabled():
        ref_text = "{::cmd{F_IPA=true}}" + reference_text

    params = {
        "appid": appid,
        "server_engine_type": _ENGINE_MODEL_TYPE,
        "text_mode": 0,
        "rec_mode": 1,
        "ref_text": ref_text,
        "keyword": "",
        "eval_mode": eval_mode,
        "score_coeff": 1.0,
        "sentence_info_enabled": 0,
        "secretid": secret_id,
        "voice_format": 1,
        "voice_id": str(uuid.uuid1()),
        "timestamp": str(int(time.time())),
        "nonce": str(int(time.time())),
        "expired": int(time.time()) + 24 * 60 * 60,
    }
    token = _env("TENCENT_TOKEN")
    if token:
        params["token"] = token

    signed_items = sorted(params.items(), key=lambda item: item[0])
    sign_string = _format_sign_string(signed_items)
    signature = _sign(sign_string, secret_key)
    return (
        f"wss://{_HOST}{_PATH}/"
        f"{_query_path(params)}&signature={quote(signature)}"
    )


def _format_sign_string(items: list[tuple[str, object]]) -> str:
    appid = next(str(value) for key, value in items if key == "appid")
    pairs = [f"{key}={value}" for key, value in items if key != "appid"]
    return f"{_HOST}{_PATH}/{appid}?" + "&".join(pairs)


def _eval_mode(reference_text: str) -> int:
    """Tencent SOE uses word mode for one word and sentence mode for phrases."""
    return 0 if len(reference_text.split()) <= 1 else 1


def _ipa_enabled() -> bool:
    """IPA phoneme output is on by default. Set TENCENT_ENABLE_IPA=0 to drop
    back to plain scoring if the {::cmd{...}} prefix ever breaks signing."""
    return _env("TENCENT_ENABLE_IPA", "1") != "0"


def _query_path(params: dict) -> str:
    appid = params["appid"]
    query = urlencode({k: v for k, v in params.items() if k != "appid"})
    return f"{appid}?{query}"


def _sign(sign_string: str, secret_key: str) -> str:
    digest = hmac.new(
        secret_key.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def _normalize(response: dict) -> dict:
    result = response.get("result") or {}
    word_list = result.get("word_list") or result.get("Words") or []
    words = []
    for item in word_list:
        score = _first_number(item, "pron_accuracy", "PronAccuracy", "score", "Score")
        word = {
            "word": item.get("word") or item.get("Word") or "",
            "accuracy_score": score,
            "error_type": "None" if score is None or score >= 60 else "Mispronunciation",
        }
        phones = _extract_phones(item)
        if phones:
            word["phones"] = phones
            tip = _phone_tip(phones)
            if tip:
                word["tip"] = tip
        words.append(word)

    accuracy = _first_number(result, "pron_accuracy", "PronAccuracy", "accuracy_score", "AccuracyScore")
    fluency = _first_number(result, "pron_fluency", "PronFluency", "fluency_score", "FluencyScore")
    completeness = _first_number(result, "pron_completion", "PronCompletion", "completeness_score", "CompletenessScore")
    suggested = _first_number(result, "suggested_score", "SuggestedScore", "overall_score", "OverallScore", "score", "Score")

    # SuggestedScore = PronAccuracy x PronCompletion x (2 - PronCompletion), so a
    # 0 score means completeness collapsed — log the parsed scores + how many
    # words SOE matched to pinpoint whether the audio reached SOE intact.
    logger.info("SOE parsed: suggested=%s accuracy=%s fluency=%s completeness=%s words=%d",
                suggested, accuracy, fluency, completeness, len(words))

    return {
        "accuracy_score": accuracy,
        "fluency_score": fluency,
        "completeness_score": completeness,
        "pronunciation_score": suggested,
        "words": words,
        "provider": "tencent",
    }


def _first_number(data: dict, *keys: str) -> float | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, (int, float)):
            return round(float(value), 1)
    return None


def _extract_phones(word_item: dict) -> list[dict]:
    """Pull per-phoneme IPA + accuracy from a SOE word item.

    Requires IPA mode (F_IPA=true) for `Phone` to be the international phonetic
    symbol; without it SOE returns its internal phone set. Returns [] when the
    response carries no phoneme breakdown so the field is simply omitted.
    """
    phone_list = word_item.get("phone_list") or word_item.get("PhoneInfos") or []
    phones = []
    for p in phone_list:
        phones.append({
            "phone": p.get("phone") or p.get("Phone") or "",
            "ref_phone": p.get("ref_phone") or p.get("ReferencePhone") or "",
            "accuracy_score": _first_number(p, "pron_accuracy", "PronAccuracy"),
            "stress": p.get("detected_stress", p.get("DetectedStress")),
        })
    return phones


def _phone_tip(phones: list[dict]) -> str:
    """Name the weakest phoneme so the UI can give a positive, actionable hint
    instead of only flagging the word red."""
    scored = [p for p in phones if p.get("accuracy_score") is not None]
    if not scored:
        return ""
    worst = min(scored, key=lambda p: p["accuracy_score"])
    if worst["accuracy_score"] >= 60 or not worst["phone"]:
        return ""
    return worst["phone"]
