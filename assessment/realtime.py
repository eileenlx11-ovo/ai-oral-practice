"""
Real-time pronunciation feedback via WebSocket.
Receives audio chunks, accumulates them, then runs ASR + pronunciation assessment
and pushes per-word scores back to the client.
"""
import os
import json
import tempfile
from fastapi import WebSocket, WebSocketDisconnect


class RealtimeSession:
    """Manages a single WebSocket real-time pronunciation session."""

    def __init__(self, ws: WebSocket, reference_text: str = ""):
        self.ws = ws
        self.reference_text = reference_text
        self.audio_buffer = bytearray()

    async def handle(self):
        """Main loop: receive audio frames, assess when enough data accumulates."""
        await self.ws.accept()
        try:
            # First message = config JSON
            config_msg = await self.ws.receive_text()
            config = json.loads(config_msg)
            self.reference_text = config.get("reference_text", "")
            await self.ws.send_json({"type": "ready", "message": "Listening..."})

            while True:
                data = await self.ws.receive_bytes()
                self.audio_buffer.extend(data)
                # ~8KB ≈ 2.5s of WebM/Opus at ~32kbps
                if len(self.audio_buffer) >= 8000:
                    await self._assess_chunk()
        except WebSocketDisconnect:
            pass
        except Exception as e:
            try:
                await self.ws.send_json({"type": "error", "message": str(e)})
            except Exception:
                pass

    async def _assess_chunk(self):
        """Save buffered audio, run ASR + pronunciation assessment, send results."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        tmp.write(bytes(self.audio_buffer))
        tmp.close()
        self.audio_buffer.clear()

        try:
            # ASR with fallback
            from openai import AsyncOpenAI
            asr_base_url = os.getenv("ASR_BASE_URL", "https://api.groq.com/openai/v1")
            asr_key = os.getenv("ASR_API_KEY") or os.getenv("GROQ_API_KEY") or "sk-placeholder"
            asr_model = os.getenv("ASR_MODEL", "whisper-large-v3-turbo")
            asr_client = AsyncOpenAI(api_key=asr_key, base_url=asr_base_url)

            text = None
            try:
                with open(tmp.name, "rb") as f:
                    resp = await asr_client.audio.transcriptions.create(
                        model=asr_model, file=f, language="en",
                    )
                text = resp.text.strip() if hasattr(resp, "text") else str(resp).strip()
            except Exception:
                # Fallback to Qwen3-ASR
                fallback_key = os.getenv("DASHSCOPE_API_KEY", "")
                if fallback_key:
                    fallback_client = AsyncOpenAI(
                        api_key=fallback_key,
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    )
                    fallback_model = os.getenv("ASR_FALLBACK_MODEL", "qwen3-asr")
                    with open(tmp.name, "rb") as f:
                        resp = await fallback_client.audio.transcriptions.create(
                            model=fallback_model, file=f, language="en",
                        )
                    text = resp.text.strip() if hasattr(resp, "text") else str(resp).strip()

            if not text:
                await self.ws.send_json({"type": "silence"})
                return

            await self.ws.send_json({"type": "transcription", "text": text})

            # Pronunciation assessment
            from .scoring import assess_pronunciation
            ref = self.reference_text or text
            try:
                result = await assess_pronunciation(tmp.name, ref, mode="standard")
                if result:
                    words = [{"word": w.get("word", ""), "score": w.get("accuracy_score", 0), "error_type": w.get("error_type", "None")} for w in result.get("words", [])]
                    await self.ws.send_json({
                        "type": "assessment", "text": text,
                        "overall_score": result.get("pronunciation_score", 0),
                        "accuracy_score": result.get("accuracy_score", 0),
                        "fluency_score": result.get("fluency_score", 0),
                        "words": words,
                    })
                else:
                    await self.ws.send_json({"type": "assessment", "text": text, "overall_score": None, "words": []})
            except Exception:
                await self.ws.send_json({"type": "assessment", "text": text, "overall_score": None, "words": []})
        finally:
            os.unlink(tmp.name)


async def realtime_pronunciation_endpoint(ws: WebSocket):
    """WebSocket endpoint handler."""
    session = RealtimeSession(ws)
    await session.handle()
