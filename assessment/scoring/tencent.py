"""Tencent Cloud SOE (Smart Oral Evaluation) pronunciation provider.

Domestic, China-accessible fallback for when Azure is unavailable. Scores
accuracy / fluency / completeness. Requires tencentcloud-sdk-python and
TENCENT_SECRET_ID / TENCENT_SECRET_KEY in the environment.

API ref: https://cloud.tencent.com/document/product/1774/56537
"""
import os
import base64
import uuid
import subprocess
import tempfile

try:
    from tencentcloud.common import credential
    from tencentcloud.soe.v20180724 import soe_client, models
    _HAS_SDK = True
except ImportError:
    _HAS_SDK = False

# SOE caps each transmitted packet; chunk the audio to stay under the limit.
_CHUNK_BYTES = 100 * 1024


def available() -> bool:
    return (
        _HAS_SDK
        and bool(os.getenv("TENCENT_SECRET_ID", ""))
        and bool(os.getenv("TENCENT_SECRET_KEY", ""))
    )


def _client():
    cred = credential.Credential(
        os.getenv("TENCENT_SECRET_ID", ""),
        os.getenv("TENCENT_SECRET_KEY", ""),
    )
    region = os.getenv("TENCENT_SOE_REGION", "ap-shanghai")
    return soe_client.SoeClient(cred, region)


def _ensure_mp3(audio_path: str) -> str:
    """Convert non-mp3 audio (webm/opus/wav) to mp3 for Tencent SOE."""
    if audio_path.endswith(".mp3"):
        return audio_path
    mp3_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    mp3_tmp.close()
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1",
             "-b:a", "64k", mp3_tmp.name],
            capture_output=True, check=True,
        )
        return mp3_tmp.name
    except (subprocess.CalledProcessError, FileNotFoundError):
        # ffmpeg not available — try raw (may fail with SOE)
        os.unlink(mp3_tmp.name)
        return audio_path


async def assess(audio_path: str, reference_text: str) -> dict | None:
    if not available():
        return None
    import asyncio
    return await asyncio.to_thread(_assess_sync, audio_path, reference_text)


def _assess_sync(audio_path: str, reference_text: str) -> dict | None:
    client = _client()

    # Convert webm/opus to mp3 for SOE compatibility
    mp3_path = _ensure_mp3(audio_path)

    try:
        with open(mp3_path, "rb") as f:
            audio = f.read()

        session_id = uuid.uuid4().hex[:16]
        # Split into ordered chunks; SOE assembles them by SeqId within one SessionId.
        chunks = [audio[i:i + _CHUNK_BYTES] for i in range(0, len(audio), _CHUNK_BYTES)] or [b""]

        last_resp = None
        for seq, chunk in enumerate(chunks):
            req = models.TransmitOralProcessWithInitRequest()
            req.SeqId = seq + 1
            req.IsEnd = 1 if seq == len(chunks) - 1 else 0
            req.VoiceFileType = 2          # 2 = mp3
            req.VoiceEncodeType = 1        # 1 = raw
            req.UserVoiceData = base64.b64encode(chunk).decode()
            req.SessionId = session_id
            req.RefText = reference_text
            req.WorkMode = 1               # 1 = streaming transmit
            req.EvalMode = 1               # 1 = sentence evaluation
            req.ScoreCoeff = 1.0
            req.ServerType = 0             # 0 = English
            last_resp = client.TransmitOralProcessWithInit(req)

        if last_resp is None:
            return None
        return _normalize(last_resp)
    finally:
        # Clean up temp mp3 if we created one
        if mp3_path != audio_path:
            try:
                os.unlink(mp3_path)
            except OSError:
                pass


def _normalize(resp) -> dict:
    """Map SOE response onto the shared schema (Azure-compatible)."""
    words = []
    for w in (resp.Words or []):
        words.append({
            "word": w.Word,
            "accuracy_score": w.PronAccuracy,
            # MatchTag 0 = matched; anything else flags a pronunciation issue.
            "error_type": "None" if getattr(w, "MatchTag", 0) == 0 else "Mispronunciation",
        })
    # SOE fluency/completion are 0-1 ratios; scale to 0-100 for a uniform schema.
    return {
        "accuracy_score": resp.PronAccuracy,
        "fluency_score": round((resp.PronFluency or 0) * 100, 1),
        "completeness_score": round((resp.PronCompletion or 0) * 100, 1),
        "pronunciation_score": resp.SuggestedScore,
        "words": words,
        "provider": "tencent",
    }
