"""
Streaming helpers for real-time chat:
- Sentence splitter for LLM stream output
- Parallel TTS synthesis per sentence
"""
import re
import uuid
import asyncio
from pathlib import Path

import edge_tts

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

        # Look for sentence boundaries
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


async def synthesize_sentence(text: str, voice: str = "en-US-JennyNeural") -> str:
    """
    Synthesize a single sentence to MP3 via edge-tts.
    Returns the URL path (e.g. /audio/xxx.mp3).
    ~200-400ms per sentence.
    """
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = AUDIO_DIR / filename

    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(filepath))
    return f"/audio/{filename}"
