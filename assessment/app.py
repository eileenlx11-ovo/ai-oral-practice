"""
Assessment backend - AI English Oral Practice
FastAPI server providing chat, ASR proxy, pronunciation scoring, and session tracking.
"""
import os
import json
import tempfile
import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI

from .scenarios import SCENARIOS, get_system_prompt
from .correction import extract_corrections

load_dotenv()

# Audio output directory
AUDIO_DIR = Path(__file__).parent / "audio_cache"
AUDIO_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="AI Oral Practice API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve cached TTS audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# LLM client
llm = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY", ""),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# --- Routes ---

@app.get("/api/scenarios")
async def list_scenarios():
    return SCENARIOS


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise HTTPException(404, f"Scenario '{scenario_id}' not found")


@app.post("/api/chat")
async def chat(
    audio: UploadFile = File(...),
    scenario: str = Form("smalltalk"),
    history: str = Form("[]"),
):
    """
    Main conversation endpoint:
    1. ASR: transcribe user audio via Whisper API
    2. LLM: generate contextual reply with grammar corrections
    3. TTS: synthesize reply audio
    Returns user_text, reply_text, corrections, reply_audio_url
    """
    # 1. Save uploaded audio to temp file
    audio_bytes = await audio.read()
    suffix = ".webm" if "webm" in (audio.content_type or "") else ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(audio_bytes)
    tmp.close()

    try:
        # 2. ASR via Whisper
        user_text = await _transcribe(tmp.name)
        if not user_text.strip():
            raise HTTPException(400, "No speech detected")

        # 3. LLM conversation + correction
        chat_history = json.loads(history)
        reply_text, corrections = await _chat_with_correction(
            scenario, user_text, chat_history
        )

        # 4. TTS synthesis
        audio_url = await _synthesize_tts(reply_text)

        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "reply_audio_url": audio_url,
            "corrections": corrections,
            "pronunciation": None,  # filled by /api/assess later
        }
    finally:
        os.unlink(tmp.name)


@app.post("/api/asr")
async def asr_only(audio: UploadFile = File(...)):
    """Transcribe audio without triggering LLM dialogue."""
    audio_bytes = await audio.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
    tmp.write(audio_bytes)
    tmp.close()
    try:
        text = await _transcribe(tmp.name)
        return {"text": text}
    finally:
        os.unlink(tmp.name)


# --- Internal helpers ---

async def _transcribe(filepath: str) -> str:
    """Transcribe audio file using OpenAI Whisper API."""
    with open(filepath, "rb") as f:
        resp = await llm.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="en",
        )
    return resp.text


async def _chat_with_correction(
    scenario: str, user_text: str, history: list[dict]
) -> tuple[str, list[dict]]:
    """
    Send user message to LLM with scenario system prompt.
    The LLM is instructed to reply naturally AND flag grammar errors.
    Returns (reply_text, corrections_list).
    """
    system_prompt = get_system_prompt(scenario)
    messages = [{"role": "system", "content": system_prompt}]

    # Append history (keep last 10 turns to stay within context)
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_text})

    resp = await llm.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )

    raw_reply = resp.choices[0].message.content or ""
    reply_text, corrections = extract_corrections(raw_reply)
    return reply_text, corrections


async def _synthesize_tts(text: str) -> str | None:
    """Generate TTS audio via OpenAI TTS API. Returns URL path or None."""
    try:
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = AUDIO_DIR / filename

        resp = await llm.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
        )
        resp.stream_to_file(str(filepath))
        return f"/audio/{filename}"
    except Exception:
        # TTS failure is non-critical; frontend falls back to text-only
        return None
