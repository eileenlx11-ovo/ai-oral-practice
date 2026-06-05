"""
Azure Speech Pronunciation Assessment integration.
Provides phoneme-level scoring: accuracy, fluency, completeness, prosody.
"""
import os
import json
import tempfile
import wave
import struct
from pathlib import Path

try:
    import azure.cognitiveservices.speech as speechsdk
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False


def get_speech_config():
    """Create Azure Speech config from environment variables."""
    key = os.getenv("AZURE_SPEECH_KEY", "")
    region = os.getenv("AZURE_SPEECH_REGION", "eastasia")
    if not key:
        return None
    return speechsdk.SpeechConfig(subscription=key, region=region)


async def assess_pronunciation(audio_path: str, reference_text: str) -> dict | None:
    """
    Run pronunciation assessment on audio file against reference text.

    Returns:
        {
            "accuracy_score": float,
            "fluency_score": float,
            "completeness_score": float,
            "pronunciation_score": float,  # overall weighted
            "words": [{"word": str, "accuracy_score": float, "error_type": str}]
        }
        or None if Azure is unavailable.
    """
    if not HAS_AZURE:
        return None

    config = get_speech_config()
    if not config:
        return None

    # Configure pronunciation assessment
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True,
    )

    # Use audio file as input
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config,
        audio_config=audio_config,
        language="en-US",
    )
    pronunciation_config.apply_to(recognizer)

    # Run recognition (synchronous — wrapped in async via thread)
    import asyncio
    result = await asyncio.to_thread(_recognize_sync, recognizer)

    if result is None:
        return None

    return result


def _recognize_sync(recognizer) -> dict | None:
    """Synchronous recognition call for thread execution."""
    result = recognizer.recognize_once()

    if result.reason != speechsdk.ResultReason.RecognizedSpeech:
        return None

    # Extract pronunciation assessment result
    assessment_result = speechsdk.PronunciationAssessmentResult(result)

    words = []
    for word in assessment_result.words:
        words.append({
            "word": word.word,
            "accuracy_score": word.accuracy_score,
            "error_type": word.error_type,
        })

    return {
        "accuracy_score": assessment_result.accuracy_score,
        "fluency_score": assessment_result.fluency_score,
        "completeness_score": assessment_result.completeness_score,
        "pronunciation_score": assessment_result.pronunciation_score,
        "words": words,
    }
