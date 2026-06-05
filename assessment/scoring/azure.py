"""Azure Speech pronunciation provider.

Phoneme-level scoring: accuracy, fluency, completeness, prosody. Strongest
provider (has prosody + miscue detection) — tried first when configured.
"""
import os

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


async def assess(audio_path: str, reference_text: str) -> dict | None:
    if not available():
        return None
    config = _speech_config()
    if not config:
        return None

    pron_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True,
    )
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config, audio_config=audio_config, language="en-US",
    )
    pron_config.apply_to(recognizer)

    import asyncio
    return await asyncio.to_thread(_recognize_sync, recognizer)


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
        "words": words,
        "provider": "azure",
    }
