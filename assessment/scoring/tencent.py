"""Tencent Cloud SOE New Edition pronunciation provider.

Uses the WebSocket API for Smart Oral Evaluation New Edition. Required env:
TENCENT_APP_ID, TENCENT_SECRET_ID, TENCENT_SECRET_KEY.
"""
import base64
import hashlib
import hmac
import json
import os
import subprocess
import tempfile
import threading
import time
import uuid
from urllib.parse import quote, urlencode

try:
    import websocket
    _HAS_WEBSOCKET = True
except ImportError:
    websocket = None
    _HAS_WEBSOCKET = False

_HOST = "soe.cloud.tencent.com"
_PATH = "/soe/api"
_ENGINE_MODEL_TYPE = "16k_en"
_OPEN_TIMEOUT_SECONDS = 10
_DONE_TIMEOUT_SECONDS = 60


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
        response = _run_ws_assessment(wav_path, reference_text)
        return _normalize(response)
    finally:
        if wav_path != audio_path:
            try:
                os.unlink(wav_path)
            except OSError:
                pass


def _ensure_wav(audio_path: str) -> str:
    """Convert input audio to 16k mono PCM WAV for SOE New Edition."""
    if audio_path.lower().endswith(".wav"):
        return audio_path

    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_tmp.close()
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", wav_tmp.name],
            capture_output=True,
            check=True,
        )
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

    def on_open(ws):
        state["opened"].set()

    def on_message(ws, message):
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

    if not state["opened"].wait(_OPEN_TIMEOUT_SECONDS):
        ws.close()
        raise TencentSOEError("Tencent SOE websocket did not open in time")

    with open(audio_path, "rb") as f:
        ws.sock.send_binary(f.read())

    ws.sock.send(json.dumps({"type": "end"}))

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

    params = {
        "appid": appid,
        "server_engine_type": _ENGINE_MODEL_TYPE,
        "text_mode": 0,
        "rec_mode": 1,
        "ref_text": reference_text,
        "keyword": "",
        "eval_mode": _eval_mode(reference_text),
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
    word_list = result.get("word_list") or []
    words = []
    for item in word_list:
        score = _first_number(item, "pron_accuracy", "PronAccuracy", "score", "Score")
        words.append({
            "word": item.get("word") or item.get("Word") or "",
            "accuracy_score": score,
            "error_type": "None" if score is None or score >= 60 else "Mispronunciation",
        })

    accuracy = _first_number(result, "pron_accuracy", "PronAccuracy", "accuracy_score", "AccuracyScore")
    fluency = _first_number(result, "pron_fluency", "PronFluency", "fluency_score", "FluencyScore")
    completeness = _first_number(result, "pron_completion", "PronCompletion", "completeness_score", "CompletenessScore")
    suggested = _first_number(result, "suggested_score", "SuggestedScore", "overall_score", "OverallScore", "score", "Score")

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
