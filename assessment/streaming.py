"""
Streaming helpers for real-time chat:
- Sentence splitter for LLM stream output
- Parallel TTS synthesis per sentence (Azure Speech SDK primary, edge-tts fallback)
"""
import re
import os
import uuid
import asyncio
from pathlib import Path

# Sentence boundary pattern: split on . ! ? followed by space or end
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+|(?<=[.!?])$')

AUDIO_DIR = Path(__file__).parent / "audio_cache"
AUDIO_DIR.mkdir(exist_ok=True)


class SentenceSplitter:
    """
    Accumulates streaming LLM tokens and yields complete sentences.
    Buffers partial text until a sentence boundary is detected.
    """

    def __init__(self):
        self._buffer = ""
        self._index = 0

    def feed(self, token: str) -> list[dict]:
        """
        Feed a token from LLM stream. Returns list of complete sentences
        (may be empty if still buffering, or multiple if token completes several).
        """
        self._buffer += token
        sentences = []

        while True:
            match = _SENTENCE_END.search(self._buffer)
            if not match:
                break

            end_pos = match.end()
            sentence_text = self._buffer[:end_pos].strip()

            if sentence_text and len(sentence_text) > 3:
                sentences.append({
                    "index": self._index,
                    "text": sentence_text,
                })
                self._index += 1

            self._buffer = self._buffer[end_pos:]

        return sentences

    def flush(self) -> dict | None:
        """Flush remaining buffer as final sentence."""
        remaining = self._buffer.strip()
        if remaining and len(remaining) > 3:
            result = {"index": self._index, "text": remaining}
            self._buffer = ""
            self._index += 1
            return result
        self._buffer = ""
        return None


def _azure_tts_available() -> bool:
    try:
        import azure.cognitiveservices.speech  # noqa: F401
        return bool(os.getenv("AZURE_SPEECH_KEY", ""))
    except ImportError:
        return False


async def _synthesize_azure(text: str, voice: str) -> str | None:
    """Synthesize with Azure Speech SDK."""
    import azure.cognitiveservices.speech as speechsdk

    key = os.getenv("AZURE_SPEECH_KEY", "")
    region = os.getenv("AZURE_SPEECH_REGION", "eastasia")
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_synthesis_voice_name = voice
    config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filepath))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=audio_config
    )

    def _do():
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return f"/audio/{filename}"
        return None

    return await asyncio.to_thread(_do)


async def _synthesize_edge(text: str, voice: str) -> str | None:
    """Fallback: edge-tts (free but may be blocked by Microsoft)."""
    try:
        import edge_tts
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = AUDIO_DIR / filename
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(str(filepath))
        return f"/audio/{filename}"
    except Exception:
        return None


async def synthesize_sentence(text: str, voice: str = "en-US-JennyNeural") -> str:
    """
    Synthesize a single sentence to MP3.
    Azure Speech SDK first, edge-tts fallback.
    Returns URL path (e.g. /audio/xxx.mp3) or empty string on total failure.
    """
    if _azure_tts_available():
        url = await _synthesize_azure(text, voice)
        if url:
            return url

    url = await _synthesize_edge(text, voice)
    if url:
        return url

    return ""
