"""Azure Speech pronunciation provider.

Phoneme-level scoring: accuracy, fluency, completeness, prosody. Strongest
provider (has prosody + miscue detection) — tried first when configured.
"""
import os
import subprocess
import tempfile

try:
    import azure.cognitiveservices.speech as speechsdk
    _HAS_SDK = True
except ImportError:
    _HAS_SDK = False


def available() -> bool:
    return _HAS_SDK and bool(os.getenv("AZURE_SPEECH_KEY", ""))


def _speech_config():
    key = os.getenv("AZURE_SPEECH_KEY", "")
    region = os.getenv("AZURE_SPEECH_REGION", "eastasia")
    if not key:
        return None
    return speechsdk.SpeechConfig(subscription=key, region=region)


def _ensure_wav(audio_path: str) -> str:
    """Convert non-WAV audio to 16kHz mono WAV for Azure Speech SDK."""
    if audio_path.endswith(".wav"):
        return audio_path
    wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_tmp.close()
    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1",
         "-sample_fmt", "s16", wav_tmp.name],
        capture_output=True, check=True,
    )
    return wav_tmp.name


async def assess(audio_path: str, reference_text: str) -> dict | None:
    if not available():
        return None
    config = _speech_config()
    if not config:
        return None

    # Azure SDK only accepts WAV; convert webm/mp3/ogg on the fly.
    wav_path = _ensure_wav(audio_path)

    pron_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True,
    )
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config, audio_config=audio_config, language="en-US",
    )
    pron_config.enable_prosody_assessment()
    pron_config.apply_to(recognizer)

    import asyncio
    try:
        return await asyncio.to_thread(_recognize_sync, recognizer)
    finally:
        # Clean up temp WAV if we created one
        if wav_path != audio_path:
            try:
                os.remove(wav_path)
            except OSError:
                pass


def _recognize_sync(recognizer) -> dict | None:
    result = recognizer.recognize_once()
    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return None
    r = speechsdk.PronunciationAssessmentResult(result)
    words = [
        {"word": w.word, "accuracy_score": w.accuracy_score, "error_type": w.error_type}
        for w in r.words
    ]
    return {
        "accuracy_score": r.accuracy_score,
        "fluency_score": r.fluency_score,
        "completeness_score": r.completeness_score,
        "pronunciation_score": r.pronunciation_score,
        "prosody_score": getattr(r, "prosody_score", None),
        "words": words,
        "provider": "azure",
    }
