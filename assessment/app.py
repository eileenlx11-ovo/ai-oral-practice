"""
Assessment backend - AI English Oral Practice
FastAPI server providing chat, ASR proxy, pronunciation scoring, and session tracking.
Enhanced with: hint system, level assessment, character memory, talent-agent integration.
"""
import os
import json
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from openai import AsyncOpenAI
from .auth import (
    create_user, create_user_by_phone, get_user_by_email, get_user_by_id,
    update_user, verify_password, issue_jwt, get_current_user, get_optional_user,
    PHONE_RE,
)
from .sms import send_verification_code, verify_code
from .scenarios import SCENARIOS, CATEGORIES, VOICES, get_system_prompt, get_voice_for_scenario, get_practice_sentences, get_practice_sentences_full, build_custom_interview_prompt, build_custom_topic_prompt, get_voice_for_custom_partner, SPEED_PRESETS
from .characters import CHARACTERS, get_character, list_characters
from .correction import extract_corrections
from .scoring import assess_pronunciation, active_provider
from .feedback import store
from .streaming import SentenceSplitter, synthesize_sentence
from .hints import build_hint_messages
from .grading import grade_session
from .level_test import LEVEL_TEST_QUESTIONS, build_assessment_messages
from .user_profile import DEFAULT_USER_ID, profile_store
from .integrations.talent_agent import get_talent_agent
from .stories import (
    ADVANCE_MARKER,
    build_story_prompt,
    get_story,
    list_stories as list_story_cards,
    next_scene_index,
    strip_scene_advance_marker,
)

load_dotenv()

# Audio output directory
AUDIO_DIR = Path(__file__).parent / "audio_cache"
AUDIO_DIR.mkdir(exist_ok=True)

# Recordings directory for session playback
RECORDINGS_DIR = Path(__file__).parent / "data" / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def _save_recording(session_id: str, turn_index: int, audio_path: str):
    """Copy the temp audio file to recordings directory for later playback."""
    import shutil
    dest_dir = RECORDINGS_DIR / session_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"{turn_index}.webm"
    try:
        shutil.copy2(audio_path, str(dest_file))
    except Exception:
        pass  # Recording save is non-critical


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Route our logger through uvicorn's handlers so errors (e.g. ASR failures)
    # actually surface in `docker compose logs`.
    uvicorn_logger = logging.getLogger("uvicorn.error")
    if uvicorn_logger.handlers:
        logger.handlers = uvicorn_logger.handlers
        logger.setLevel(logging.INFO)
    yield


app = FastAPI(title="AI Oral Practice API", lifespan=lifespan)

_cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve cached TTS audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

logger = logging.getLogger("assessment")

# LLM client (lazy — allows server to start without key for dev/testing)
_api_key = os.getenv("LLM_API_KEY", "") or "sk-placeholder"
llm = AsyncOpenAI(
    api_key=_api_key,
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Audio upload size limit (10MB ≈ 5 min webm)
_MAX_AUDIO_BYTES = 10 * 1024 * 1024
_MAX_TTS_TEXT_CHARS = 500


def _user_id(user: dict | None) -> str:
    return user["id"] if user else DEFAULT_USER_ID


def _require_session_owner(session_id: str, user: dict | None) -> dict:
    session = store.get_session(session_id)
    if session is None or session.get("user_id", DEFAULT_USER_ID) != _user_id(user):
        raise HTTPException(404, "Session not found")
    return session


async def _read_audio(audio: UploadFile) -> bytes:
    """Read and validate uploaded audio size."""
    data = await audio.read()
    if len(data) > _MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio file too large (max 10MB)")
    if len(data) < 100:
        raise HTTPException(400, "Audio file too small or empty")
    return data


# --- Auth Routes ---

@app.post("/api/auth/register")
async def register(email: str = Form(...), password: str = Form(...), nickname: str = Form("")):
    """Register a new user account."""
    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if "@" not in email or "." not in email:
        raise HTTPException(400, "Invalid email format")
    try:
        user = create_user(email, password, nickname)
    except ValueError as e:
        if "email_taken" in str(e):
            raise HTTPException(409, "Email already registered")
        raise HTTPException(400, str(e))
    token = issue_jwt(user["id"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "nickname": user["nickname"]}}


@app.post("/api/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Login with email and password."""
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    token = issue_jwt(user["id"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "nickname": user["nickname"]}}


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": user["id"],
        "email": user.get("email"),
        "phone": user.get("phone"),
        "nickname": user["nickname"],
    }


@app.post("/api/auth/send-code")
async def send_code(phone: str = Form(...)):
    """Send SMS verification code to a phone number."""
    if not PHONE_RE.match(phone):
        raise HTTPException(400, "请输入有效的手机号")
    result = await send_verification_code(phone)
    if not result["success"]:
        raise HTTPException(429, result["error"])
    # In dev mode, return the code for testing
    resp = {"success": True}
    if "_dev_code" in result:
        resp["_dev_code"] = result["_dev_code"]
    return resp


@app.post("/api/auth/phone-login")
async def phone_login(phone: str = Form(...), code: str = Form(...)):
    """Login or register via phone + SMS verification code."""
    if not PHONE_RE.match(phone):
        raise HTTPException(400, "请输入有效的手机号")
    if not verify_code(phone, code):
        raise HTTPException(401, "验证码错误或已过期")
    user = create_user_by_phone(phone)
    token = issue_jwt(user["id"])
    return {"token": token, "user": {"id": user["id"], "phone": user.get("phone"), "nickname": user["nickname"]}}


# --- Settings Routes ---

@app.get("/api/settings")
async def get_settings(user: dict = Depends(get_current_user)):
    """Get user settings."""
    settings = user.get("settings", {})
    return {
        "nickname": user.get("nickname", ""),
        "voice": settings.get("voice", "american_female"),
        "locale": settings.get("locale", "zh"),
        "theme": settings.get("theme", "system"),
    }


@app.put("/api/settings")
async def update_settings(
    user: dict = Depends(get_current_user),
    nickname: str = Form(None),
    voice: str = Form(None),
    locale: str = Form(None),
    theme: str = Form(None),
):
    """Update user settings."""
    changed = False
    if nickname is not None and nickname.strip():
        user["nickname"] = nickname.strip()
        changed = True

    settings = user.get("settings", {})
    if voice is not None and voice in VOICES:
        settings["voice"] = voice
        changed = True
    if locale is not None and locale in ("zh", "en"):
        settings["locale"] = locale
        changed = True
    if theme is not None and theme in ("light", "dark", "system"):
        settings["theme"] = theme
        changed = True

    if changed:
        user["settings"] = settings
        update_user(user)

    return {"success": True, "nickname": user["nickname"], "voice": settings.get("voice", "american_female"), "locale": settings.get("locale", "zh"), "theme": settings.get("theme", "system")}


# --- Routes ---

@app.get("/api/scenarios")
async def list_scenarios(category: str = "all"):
    if category == "all":
        return SCENARIOS
    return [s for s in SCENARIOS if s.get("category") == category]


@app.get("/api/categories")
async def list_categories():
    return CATEGORIES


@app.get("/api/voices")
async def list_voices():
    return VOICES


@app.get("/api/characters")
async def characters():
    """List available roleplay characters for scenario/role switching."""
    return list_characters()


@app.get("/api/stories")
async def list_stories():
    """List available story-mode scripts."""
    return list_story_cards()


@app.get("/api/stories/{story_id}")
async def get_story_detail(story_id: str):
    """Return a full story script for the story-mode UI."""
    story = get_story(story_id)
    if story is None:
        raise HTTPException(404, f"Story '{story_id}' not found")
    return story


@app.post("/api/stories/{story_id}/start")
async def start_story(
    story_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Create a story-mode practice session."""
    story = get_story(story_id)
    if story is None:
        raise HTTPException(404, f"Story '{story_id}' not found")

    session = store.create_session(story_id, user_id=_user_id(user))
    opening = story["scenes"][0]["ai_opening"]
    store.update_session_fields(
        session["id"],
        story_id=story_id,
        story_scene_index=0,
        story_completed=False,
        greeting=opening,
    )
    return {
        "session_id": session["id"],
        "story_id": story_id,
        "scene_index": 0,
        "ai_opening": opening,
    }


@app.get("/api/tts-preview")
async def tts_preview(voice: str = "american_female", text: str = "Hello! This is how I sound."):
    """Generate a TTS preview for the given voice and text."""
    voice_id = VOICES.get(voice, VOICES["american_female"])["id"]
    try:
        audio_id = uuid.uuid4().hex
        out_path = AUDIO_DIR / f"{audio_id}.mp3"
        await synthesize_sentence(text, str(out_path), voice_id)
        return FileResponse(str(out_path), media_type="audio/mpeg")
    except Exception:
        raise HTTPException(500, "TTS preview failed")


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            # Enrich with character info
            character = get_character(scenario_id)
            return {**s, "character": character}
    raise HTTPException(404, f"Scenario '{scenario_id}' not found")


@app.get("/api/scenarios/{scenario_id}/sentences")
async def get_sentences(scenario_id: str):
    """Pronunciation practice sentences for a scenario.

    `sentences` stays a plain string list (backward compatible; also what the
    scoring reference_text needs). `sentences_full` adds per-word en-US IPA
    [{text, words:[{word, ipa_us}]}] for the dictionary-phonetics UI.
    """
    full = get_practice_sentences_full(scenario_id)
    return {
        "scenario_id": scenario_id,
        "sentences": [s["text"] for s in full],
        "sentences_full": full,
    }


@app.get("/api/scenarios/{scenario_id}/guide")
async def get_scenario_guide(scenario_id: str):
    """Get learning guide (vocabulary, expressions, tips, dialogue) for a scenario."""
    from .learning_guide import get_guide, generate_guide
    guide = get_guide(scenario_id)
    if guide:
        return guide
    # Try to generate via LLM
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    guide = await generate_guide(scenario_id, scenario["name"], llm, LLM_MODEL)
    if guide:
        return guide
    raise HTTPException(503, "Guide generation unavailable")


@app.post("/api/chat")
async def chat(
    audio: UploadFile = File(...),
    scenario: str = Form("smalltalk"),
    history: str = Form("[]"),
    session_id: str = Form(""),
    user: dict | None = Depends(get_optional_user),
):
    """
    Main conversation endpoint:
    1. ASR: transcribe user audio via Whisper API
    2. LLM: generate contextual reply with grammar corrections
    3. TTS: synthesize reply audio
    4. Auto-save turn to session (if session_id provided)
    Returns user_text, reply_text, corrections, reply_audio_url, session_id
    """
    # Auto-create session if not provided
    if not session_id:
        session = store.create_session(scenario, user_id=_user_id(user))
        session_id = session["id"]
    else:
        session = _require_session_owner(session_id, user)
        scenario = session.get("scenario", scenario)

    # 1. Save uploaded audio to temp file
    audio_bytes = await _read_audio(audio)
    suffix = ".webm" if "webm" in (audio.content_type or "") else ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(audio_bytes)
    tmp.close()

    try:
        # 2. ASR via Whisper
        current_session = store.get_session(session_id)
        user_text = await _transcribe(tmp.name, (current_session or {}).get("language", "en"))
        if not user_text.strip():
            raise HTTPException(400, "No speech detected")

        # 3. LLM conversation + correction
        chat_history = json.loads(history)
        reply_text, corrections, scene_marker_seen = await _chat_with_correction(
            scenario, user_text, chat_history, session=store.get_session(session_id)
        )

        scene_advanced = False
        story_completed = False
        if current_session and current_session.get("story_id"):
            current_scene = int(current_session.get("story_scene_index", 0))
            if scene_marker_seen:
                next_index, scene_advanced, story_completed = next_scene_index(
                    current_session["story_id"], current_scene
                )
                store.update_session_fields(
                    session_id,
                    story_scene_index=next_index,
                    story_completed=story_completed,
                )

        # 4. TTS synthesis
        audio_url = await _synthesize_tts(reply_text)

        # 5. Auto-save turn to session
        try:
            store.add_turn(session_id, user_text, reply_text, corrections)
        except ValueError:
            pass  # session not found, non-critical

        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "reply_audio_url": audio_url,
            "corrections": corrections,
            "pronunciation": None,  # filled by /api/assess later
            "session_id": session_id,
            "scene_advanced": scene_advanced,
            "story_completed": story_completed,
        }
    finally:
        os.unlink(tmp.name)


@app.post("/api/stream")
async def chat_stream(
    audio: UploadFile = File(...),
    scenario: str = Form("smalltalk"),
    history: str = Form("[]"),
    session_id: str = Form(""),
    voice: str = Form("american_female"),
    user: dict | None = Depends(get_optional_user),
):
    """
    Streaming chat endpoint (SSE).
    Same logic as /api/chat but streams results as they become available:
    - event: asr → user transcription (immediate after ASR)
    - event: sentence → each AI sentence + audio URL (as generated)
    - event: corrections → grammar corrections (after full reply)
    - event: done → final metadata
    """
    # Auto-create session
    if not session_id:
        session = store.create_session(scenario, user_id=_user_id(user))
        session_id = session["id"]
    else:
        session = _require_session_owner(session_id, user)
        scenario = session.get("scenario", scenario)
        voice = session.get("voice", voice)

    # Resolve system prompt: session-level custom prompt overrides scenario prompt.
    existing = store.get_session(session_id)
    session_language = (existing or {}).get("language", "en")
    is_story_session = bool(existing and existing.get("story_id"))
    story_id = existing.get("story_id") if existing else None
    story_scene_index = int(existing.get("story_scene_index", 0)) if existing else 0
    if is_story_session:
        system_prompt = build_story_prompt(story_id, story_scene_index)
    elif existing and existing.get("custom_prompt"):
        system_prompt = existing["custom_prompt"]
    else:
        system_prompt = get_system_prompt(scenario)

    # Read audio
    audio_bytes = await _read_audio(audio)
    suffix = ".webm" if "webm" in (audio.content_type or "") else ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(audio_bytes)
    tmp.close()

    chat_history = json.loads(history)
    # Use character-appropriate voice (fallback to form param)
    tts_voice = get_voice_for_scenario(scenario) if voice == "american_female" else VOICES.get(voice, VOICES["american_female"])["id"]

    async def event_generator():
        try:
            # 1. ASR
            try:
                user_text = await _transcribe(tmp.name, session_language)
            except Exception:
                yield _sse_error(
                    "asr",
                    "asr_failed",
                    "语音识别失败，请重试",
                    action="retry",
                )
                return
            if not user_text.strip():
                yield _sse_error(
                    "asr",
                    "no_speech",
                    "未检测到语音，请重试",
                    action="retry",
                )
                return

            yield _sse("asr", {"text": user_text})

            # 2. LLM streaming + sentence-by-sentence TTS
            # NOTE: reuse the outer system_prompt (respects session custom_prompt)
            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_text})

            splitter = SentenceSplitter()
            full_reply = ""

            try:
                stream = await llm.chat.completions.create(
                    model=LLM_MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=512,
                    stream=True,
                )

                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        token = delta.content
                        full_reply += token

                        # Check for complete sentences
                        sentences = splitter.feed(token)
                        for sent in sentences:
                            # Stop emitting once we hit corrections section
                            if "[CORRECTIONS]" in full_reply or "[END]" in full_reply:
                                break
                            # Strip LLM format markers and detect leaked corrections
                            clean = _clean_sentence(sent["text"])
                            if not clean:
                                continue
                            audio_url = await _safe_synthesize_sentence(clean, tts_voice)
                            yield _sse("sentence", {
                                "index": sent["index"],
                                "text": clean,
                                "audio_url": audio_url,
                            })
            except Exception:
                yield _sse_error(
                    "llm",
                    "llm_failed",
                    "AI 回复生成失败，请重试",
                    action="retry",
                )
                return

            # Flush remaining buffer
            remaining = splitter.flush()
            if remaining and "[CORRECTIONS]" not in remaining["text"] and "[END]" not in remaining["text"]:
                clean = _clean_sentence(remaining["text"])
                if clean:
                    audio_url = await _safe_synthesize_sentence(clean, tts_voice)
                    yield _sse("sentence", {
                        "index": remaining["index"],
                        "text": clean,
                        "audio_url": audio_url,
                    })

            # 3. Parse corrections and feedback from full reply
            try:
                from .correction import extract_feedback
                full_reply, scene_marker_seen = strip_scene_advance_marker(full_reply)
                reply_text, corrections = extract_corrections(full_reply)
                feedback = extract_feedback(full_reply)
            except Exception:
                reply_text, corrections, feedback = full_reply, [], ""
                scene_marker_seen = False

            if corrections:
                yield _sse("corrections", corrections)

            if feedback:
                yield _sse("feedback", {"text": feedback})

            # 4. Save to session & update affinity
            scene_advanced = False
            story_completed = False
            try:
                turn = store.add_turn(session_id, user_text, reply_text, corrections)
                turn_index = turn.get("index", 0) if isinstance(turn, dict) else 0
                _save_recording(session_id, turn_index, tmp.name)
                if is_story_session and scene_marker_seen:
                    current = store.get_session(session_id) or {}
                    next_index, scene_advanced, story_completed = next_scene_index(
                        story_id,
                        int(current.get("story_scene_index", story_scene_index)),
                    )
                    store.update_session_fields(
                        session_id,
                        story_scene_index=next_index,
                        story_completed=story_completed,
                    )
                profile_store.increment_affinity(_user_id(user), scenario)
            except ValueError:
                pass

            yield _sse("done", {
                "session_id": session_id,
                "full_reply": reply_text,
                "scene_advanced": scene_advanced,
                "story_completed": story_completed,
                "story_scene_index": (
                    store.get_session(session_id) or {}
                ).get("story_scene_index", story_scene_index) if is_story_session else None,
            })

        finally:
            os.unlink(tmp.name)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _clean_sentence(text: str) -> str:
    """Strip format markers and detect leaked correction content."""
    import re
    # Remove format tags
    text = text.replace("[REPLY]", "").replace("[END]", "").replace("[CORRECTIONS]", "")
    text = text.replace(ADVANCE_MARKER, "")
    # If it looks like a correction line (has → or starts with -"), skip it
    if "→" in text or text.strip().startswith('- "') or text.strip() == "NONE":
        return ""
    # If it contains pipe-separated correction patterns, strip from first |
    if " | " in text and ("→" in text or "mispronunciation" in text.lower()):
        text = text.split(" | ")[0]
    text = text.strip()
    # Skip very short fragments
    if len(text) < 4:
        return ""
    return text


def _sse(event: str, data) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _sse_error(phase: str, code: str, message: str, action: str = "retry") -> str:
    """Format a structured SSE error while preserving the message field."""
    return _sse("error", {
        "phase": phase,
        "code": code,
        "message": message,
        "action": action,
    })


async def _safe_synthesize_sentence(text: str, voice: str) -> str | None:
    """Synthesize TTS for a streamed sentence; text still streams if audio fails."""
    try:
        return await synthesize_sentence(text, voice=voice)
    except Exception:
        return None


@app.post("/api/asr")
async def asr_only(audio: UploadFile = File(...)):
    """Transcribe audio without triggering LLM dialogue."""
    audio_bytes = await _read_audio(audio)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
    tmp.write(audio_bytes)
    tmp.close()
    try:
        text = await _transcribe(tmp.name)
        return {"text": text}
    finally:
        os.unlink(tmp.name)


@app.post("/api/tts")
async def text_to_speech(text: str = Form(...)):
    """Generate TTS audio for reference text demo playback."""
    text = text.strip()
    if not text:
        raise HTTPException(400, "Text is required")
    if len(text) > _MAX_TTS_TEXT_CHARS:
        raise HTTPException(413, f"Text too long (max {_MAX_TTS_TEXT_CHARS} characters)")

    url = await synthesize_sentence(text)
    if not url:
        raise HTTPException(503, "TTS unavailable")

    filepath = AUDIO_DIR / url.split("/")[-1]
    if not filepath.exists():
        raise HTTPException(503, "TTS unavailable")
    return FileResponse(filepath, media_type="audio/mpeg")


# --- Internal helpers ---

# --- ASR providers (multi-provider with ordered fallback) ---
# Groq Whisper is fast and primary; SiliconFlow SenseVoice is the fallback.
# Each provider self-configures from env; only those with a key are activated.
import httpx as _httpx

_ASR_PROVIDER_SPECS = {
    "dashscope": {
        # Alibaba Model Studio (百炼). Qwen-ASR is NOT a Whisper-style
        # transcriptions endpoint — it runs through chat/completions with an
        # input_audio message, so it uses the "chat_audio" call style.
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_envs": ("DASHSCOPE_API_KEY",),
        "model_env": "DASHSCOPE_ASR_MODEL",
        "default_model": "qwen3-asr-flash",
        "word_timestamps": False,
        "needs_proxy": False,
        "call_style": "chat_audio",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_envs": ("GROQ_API_KEY", "ASR_API_KEY"),
        "model_env": "GROQ_ASR_MODEL",
        "default_model": "whisper-large-v3-turbo",
        "word_timestamps": True,  # Groq Whisper returns word-level timestamps
        "needs_proxy": True,      # may need HTTPS_PROXY in mainland China
        "call_style": "transcriptions",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "key_envs": ("SILICONFLOW_API_KEY",),
        "model_env": "SILICONFLOW_ASR_MODEL",
        "default_model": "FunAudioLLM/SenseVoiceSmall",
        "word_timestamps": False,  # SenseVoice does not support word timestamps
        "needs_proxy": False,
        "call_style": "transcriptions",
    },
    "dashscope": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_envs": ("DASHSCOPE_API_KEY",),
        "model_env": "DASHSCOPE_ASR_MODEL",
        "default_model": "qwen3-asr",
        "word_timestamps": True,   # Qwen3-ASR supports word-level timestamps
        "needs_proxy": False,      # China-direct, no proxy needed
    },
}

# Order is configurable; defaults to dashscope first, siliconflow fallback.
# Groq is omitted by default (account access pending) but stays available via
# ASR_PROVIDER_ORDER once a working key exists.
_ASR_ORDER = [
    p.strip() for p in os.getenv("ASR_PROVIDER_ORDER", "dashscope,siliconflow").split(",") if p.strip()
]

_proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("ALL_PROXY") or os.getenv("HTTP_PROXY")


def _build_asr_providers() -> list[dict]:
    """Instantiate ASR clients for each configured provider that has a key."""
    # Legacy override: ASR_BASE_URL forces the base_url of the first provider.
    legacy_base_override = os.getenv("ASR_BASE_URL")
    providers = []
    for idx, name in enumerate(_ASR_ORDER):
        spec = _ASR_PROVIDER_SPECS.get(name)
        if not spec:
            continue
        api_key = next((os.getenv(e) for e in spec["key_envs"] if os.getenv(e)), None)
        if not api_key:
            continue  # skip providers with no key configured
        base_url = spec["base_url"]
        if idx == 0 and legacy_base_override:
            base_url = legacy_base_override
        http_client = None
        if spec["needs_proxy"] and _proxy_url:
            http_client = _httpx.AsyncClient(proxy=_proxy_url)
        providers.append({
            "name": name,
            "client": AsyncOpenAI(api_key=api_key, base_url=base_url, http_client=http_client),
            "model": os.getenv(spec["model_env"]) or os.getenv("ASR_MODEL") or spec["default_model"],
            "base_url": base_url,
            "word_timestamps": spec["word_timestamps"],
            "call_style": spec.get("call_style", "transcriptions"),
        })
    return providers


_asr_providers = _build_asr_providers()


async def _transcribe(filepath: str, language: str = "en") -> str:
    """Transcribe audio via the configured ASR providers in order.

    Tries each provider until one succeeds. Word-level timestamps are requested
    only from providers that support them (stored in _transcribe._last_words for
    fluency analysis; None when unavailable).
    """
    if not _asr_providers:
        logger.error("ASR transcription failed: no provider configured (set GROQ_API_KEY or SILICONFLOW_API_KEY)")
        raise RuntimeError("No ASR provider configured")

    last_exc = None
    for provider in _asr_providers:
        try:
            if provider["call_style"] == "chat_audio":
                text = await _transcribe_chat_audio(provider, filepath, language)
                _transcribe._last_words = None  # chat-style ASR has no word timestamps
                return text

            kwargs = {"model": provider["model"], "language": language if language in {"en", "zh"} else "en"}
            if provider["word_timestamps"]:
                kwargs["response_format"] = "verbose_json"
                kwargs["timestamp_granularities"] = ["word"]
            with open(filepath, "rb") as f:
                resp = await provider["client"].audio.transcriptions.create(file=f, **kwargs)
        except Exception as exc:
            last_exc = exc
            logger.error(
                "ASR provider '%s' failed: %s (base_url=%s, model=%s)",
                provider["name"], exc, provider["base_url"], provider["model"],
            )
            continue  # fall back to next provider

        # Word-level timestamps (only some providers return them)
        if getattr(resp, "words", None):
            _transcribe._last_words = resp.words
        else:
            _transcribe._last_words = None

        if hasattr(resp, "text"):
            return resp.text
        if isinstance(resp, dict):
            return resp.get("text", "")
        return str(resp)

    # All providers failed
    raise last_exc if last_exc else RuntimeError("ASR transcription failed")

_transcribe._last_words = None


def _audio_mime(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower().lstrip(".")
    return {
        "wav": "audio/wav", "mp3": "audio/mpeg", "webm": "audio/webm",
        "ogg": "audio/ogg", "m4a": "audio/mp4", "flac": "audio/flac",
    }.get(ext, "audio/wav")


async def _transcribe_chat_audio(provider: dict, filepath: str, language: str = "en") -> str:
    """Transcribe via a chat/completions ASR model (Qwen-ASR on DashScope).

    Unlike Whisper-style providers, Qwen-ASR takes the audio as an input_audio
    message part. The local recording is sent as a base64 data URI; ITN is
    disabled to keep raw words for pronunciation scoring.
    """
    import base64

    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    data_uri = f"data:{_audio_mime(filepath)};base64,{b64}"

    language_name = "Chinese" if language == "zh" else "English"
    resp = await provider["client"].chat.completions.create(
        model=provider["model"],
        messages=[
            {
                "role": "system",
                "content": f"Transcribe the audio in {language_name}. Output only the transcript.",
            },
            {
                "role": "user",
                "content": [{"type": "input_audio", "input_audio": {"data": data_uri}}],
            },
        ],
        extra_body={"asr_options": {"enable_itn": False}},
    )
    return (resp.choices[0].message.content or "").strip()


async def _chat_with_correction(
    scenario: str, user_text: str, history: list[dict], session: dict | None = None
) -> tuple[str, list[dict], bool]:
    """
    Send user message to LLM with scenario system prompt.
    The LLM is instructed to reply naturally AND flag grammar errors.
    Returns (reply_text, corrections_list, scene_marker_seen).
    """
    if session and session.get("story_id"):
        system_prompt = build_story_prompt(
            session["story_id"],
            int(session.get("story_scene_index", 0)),
        )
    else:
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
    raw_reply, scene_marker_seen = strip_scene_advance_marker(raw_reply)
    reply_text, corrections = extract_corrections(raw_reply)
    return reply_text, corrections, scene_marker_seen


async def _synthesize_tts(text: str) -> str | None:
    """Generate TTS audio via edge-tts (free Microsoft voices). Returns URL path or None."""
    try:
        import edge_tts

        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = AUDIO_DIR / filename

        communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await communicate.save(str(filepath))
        return f"/audio/{filename}"
    except Exception:
        # TTS failure is non-critical; frontend falls back to text-only
        return None


async def _generate_session_report(summary: dict) -> str:
    """Generate a narrative session report using LLM."""
    try:
        if summary.get("scenario") == "interview":
            prompt = f"""Based on this oral mock interview session, write a role-focused speaking debrief in Chinese.

Session info:
- Total turns: {summary.get('total_turns', 0)}
- Total corrections: {summary.get('total_corrections', 0)}
- Common errors: {summary.get('common_errors', [])}
- Avg pronunciation: {summary.get('avg_pronunciation', 'N/A')}
- Avg fluency: {summary.get('avg_fluency', 'N/A')}
- Avg accuracy: {summary.get('avg_accuracy', 'N/A')}

Write 4 short sections in plain text:
1. Overall interview communication performance
2. Answer structure and clarity
3. Speaking/pronunciation risks that could affect interviews
4. Next 2 drills to practice before the next mock interview

Keep it specific, honest, and concise. Output Chinese only."""
        else:
            prompt = f"""Based on this English practice session data, write a brief coaching report in Chinese (3-5 sentences).

Session info:
- Scenario: {summary.get('scenario', 'unknown')}
- Total turns: {summary.get('total_turns', 0)}
- Total corrections: {summary.get('total_corrections', 0)}
- Common errors: {summary.get('common_errors', [])}
- Avg pronunciation: {summary.get('avg_pronunciation', 'N/A')}
- Avg fluency: {summary.get('avg_fluency', 'N/A')}

Write:
1. One sentence summarizing overall performance
2. One sentence about the main pattern of errors (if any)
3. One specific, actionable suggestion for improvement
Keep it encouraging but honest. Output only the report text, no headers."""

        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        # Fallback if LLM unavailable
        turns = summary.get('total_turns', 0)
        corrections = summary.get('total_corrections', 0)
        return f"本次练习共进行了 {turns} 轮对话，收到 {corrections} 条语法建议。继续保持练习节奏！"


@app.post("/api/assess")
async def assess(
    audio: UploadFile = File(...),
    reference_text: str = Form(...),
    advanced: str = Form("false"),
):
    """
    Pronunciation assessment endpoint.

    advanced=false (default): SOE priority, daily practice.
    advanced=true: Azure priority, prosody + miscue detailed diagnosis.
    """
    audio_bytes = await _read_audio(audio)
    suffix = ".wav" if "wav" in (audio.content_type or "") else ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(audio_bytes)
    tmp.close()

    use_advanced = advanced.lower() in ("true", "1", "yes")
    try:
        result = await assess_pronunciation(tmp.name, reference_text, advanced=use_advanced)
        if result is None:
            raise HTTPException(
                503,
                "Pronunciation assessment unavailable (no provider configured)",
            )
        return result
    finally:
        os.unlink(tmp.name)


@app.get("/api/assess/status")
async def assess_status():
    """Report which pronunciation providers are active for each tier.

    standard: daily practice (SOE priority).
    advanced: detailed diagnosis (Azure priority, has prosody/miscue).
    """
    std = active_provider(advanced=False)
    adv = active_provider(advanced=True)
    return {
        "available": std is not None,
        "provider": std,
        "is_mock": std == "mock",
        "advanced_available": adv is not None and adv != "mock",
        "advanced_provider": adv,
        "providers": {
            "tencent_configured": bool(
                (os.getenv("TENCENT_APP_ID") or os.getenv("TENCENT_APPID"))
                and os.getenv("TENCENT_SECRET_ID")
                and os.getenv("TENCENT_SECRET_KEY")
            ),
            "azure_configured": bool(os.getenv("AZURE_SPEECH_KEY")),
            "mock_enabled": os.getenv("PRONUNCIATION_ALLOW_MOCK", "1") != "0",
        },
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
    }


# --- Session & Progress APIs ---

@app.post("/api/sessions")
async def create_session(
    scenario: str = Form("smalltalk"),
    user: dict | None = Depends(get_optional_user),
):
    """Start a new practice session."""
    session = store.create_session(scenario, user_id=_user_id(user))
    return {"session_id": session["id"]}


@app.post("/api/sessions/custom")
async def create_custom_session(
    jd_text: str = Form(""),
    resume_text: str = Form(""),
    project_context: str = Form(""),
    language: str = Form("en"),
    user: dict | None = Depends(get_optional_user),
):
    """Start a customized interview session.

    Builds an interviewer prompt from a job description, candidate background,
    and/or project context. Designed to be called by external tools (e.g.
    talent-agent). The resulting session_id is used with /api/stream as usual;
    the stream endpoint will pick up this session's custom prompt automatically.
    """
    if not (jd_text.strip() or resume_text.strip() or project_context.strip()):
        raise HTTPException(400, "At least one of jd_text, resume_text, or project_context is required")
    prompt = build_custom_interview_prompt(jd_text, resume_text, project_context, language)
    session = store.create_session("interview", custom_prompt=prompt, user_id=_user_id(user))
    greeting = (
        "你好，欢迎参加这次模拟面试。我已经了解了岗位和你的背景。"
        "先请你简单介绍一下自己，并说明为什么对这个职位感兴趣。"
        if language == "zh"
        else "Hello! Thanks for coming in today. I've reviewed the role and your background. To start, could you walk me through your experience and why this position interests you?"
    )
    store.update_session_fields(session["id"], greeting=greeting, language=language)
    return {
        "session_id": session["id"],
        "greeting": greeting,
        "redirect_url": f"/chat/interview?session_id={session['id']}",
    }


@app.post("/api/sessions/topic")
async def create_topic_session(
    topic: str = Form(...),
    material: str = Form(""),
    partner_name: str = Form(""),
    partner_country: str = Form(""),
    partner_personality: str = Form(""),
    speed: str = Form("normal"),
    user: dict | None = Depends(get_optional_user),
):
    """Start a session with a user-defined free topic and customizable partner.

    topic: what the user wants to practice (required)
    material: optional supplementary text
    partner_name: name of the AI partner (e.g. "John")
    partner_country: country/accent (e.g. "UK", "Australia")
    partner_personality: traits (e.g. "humorous, patient, gentlemanly")
    speed: speaking pace — slowest/slow/normal/fast/fastest
    """
    if not topic.strip():
        raise HTTPException(400, "Topic is required")

    prompt = build_custom_topic_prompt(
        topic=topic,
        material=material,
        partner_name=partner_name,
        partner_country=partner_country,
        partner_personality=partner_personality,
        speed=speed,
    )
    # Determine voice based on country
    voice_id = get_voice_for_custom_partner(partner_country or "us", partner_name)

    name = partner_name.strip() or "Alex"
    session = store.create_session(
        "custom_topic",
        custom_prompt=prompt,
        user_id=_user_id(user),
        metadata={
            "partner_name": name,
            "partner_country": partner_country.strip() or "US",
            "partner_personality": partner_personality.strip() or "friendly and encouraging",
            "partner_speed": speed,
            "partner_voice_id": voice_id,
        },
    )

    greeting = f"Hi there! I'm {name}. Let's chat about {topic.strip()}. What's on your mind?"
    store.update_session_fields(session["id"], greeting=greeting)

    return {
        "session_id": session["id"],
        "topic": topic.strip(),
        "greeting": greeting,
        "partner": {
            "name": name,
            "country": partner_country.strip() or "US",
            "personality": partner_personality.strip() or "friendly and encouraging",
            "speed": speed,
            "voice_id": voice_id,
        },
    }


@app.get("/api/topics/trending")
async def get_trending_topics():
    """Get trending conversation topics via LLM."""
    try:
        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "Generate 6 trending and interesting topics for English conversation practice. Return ONLY a JSON array of objects with 'title' (English, 3-5 words) and 'description' (Chinese, one sentence explaining the topic). Topics should be current, engaging, and suitable for oral practice."},
                {"role": "user", "content": "Give me 6 trending topics for today."},
            ],
            temperature=0.9,
            max_tokens=400,
        )
        import json as _json
        text = resp.choices[0].message.content.strip()
        # Try to parse JSON from response
        if text.startswith("["):
            topics = _json.loads(text)
        else:
            # Extract JSON from markdown code block
            import re
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                topics = _json.loads(match.group())
            else:
                topics = []
        return {"topics": topics[:6]}
    except Exception:
        # Fallback static topics
        return {"topics": [
            {"title": "AI in Daily Life", "description": "讨论人工智能如何改变我们的日常生活"},
            {"title": "Remote Work Culture", "description": "聊聊远程工作的利弊和未来趋势"},
            {"title": "Sustainable Living", "description": "环保生活方式和可持续发展"},
            {"title": "Social Media Impact", "description": "社交媒体对人际关系的影响"},
            {"title": "Space Exploration", "description": "太空探索的最新进展和未来"},
            {"title": "Mental Health Awareness", "description": "心理健康意识和自我关怀"},
        ]}


@app.post("/api/sessions/{session_id}/turns")
async def add_session_turn(
    session_id: str,
    user_text: str = Form(...),
    reply_text: str = Form(...),
    corrections: str = Form("[]"),
    pronunciation: str = Form("null"),
    user: dict | None = Depends(get_optional_user),
):
    """Record a conversation turn to the session."""
    _require_session_owner(session_id, user)
    try:
        corr_list = json.loads(corrections)
        pron_data = json.loads(pronunciation)
        turn = store.add_turn(session_id, user_text, reply_text, corr_list, pron_data)
        return turn
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/sessions/{session_id}/handoff")
async def get_session_handoff(
    session_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Return initial chat metadata for a pre-created external handoff session."""
    session = _require_session_owner(session_id, user)
    scenario = session.get("scenario", "interview")

    # For custom_topic sessions, build character from stored partner metadata
    if scenario == "custom_topic" and session.get("partner_name"):
        character = {
            "name": session["partner_name"],
            "role": f"Practice partner from {session.get('partner_country', 'US')}",
            "personality": session.get("partner_personality", "friendly and encouraging"),
            "avatar": "🗣️",
            "voice_id": session.get("partner_voice_id", ""),
        }
    else:
        character = get_character(scenario)

    return {
        "session_id": session_id,
        "scenario": scenario,
        "greeting": session.get("greeting") or (
            "Hello! Thanks for coming in today. Could you start by introducing yourself?"
        ),
        "language": session.get("language", "en"),
        "character": character,
    }


@app.post("/api/sessions/{session_id}/character")
async def switch_session_character(
    session_id: str,
    scenario: str = Form(...),
    voice: str = Form(""),
    user: dict | None = Depends(get_optional_user),
):
    """Switch an existing session to another scenario character."""
    _require_session_owner(session_id, user)
    if scenario not in CHARACTERS:
        raise HTTPException(404, f"Character '{scenario}' not found")
    if voice and voice not in VOICES:
        raise HTTPException(400, f"Voice '{voice}' not found")

    update = {"scenario": scenario}
    if voice:
        update["voice"] = voice
    store.update_session_fields(session_id, **update)

    character = get_character(scenario)
    voice_key = voice or character.get("voice", "american_female")
    return {
        "session_id": session_id,
        "scenario": scenario,
        "character": character,
        "voice": voice_key,
        "voice_id": VOICES.get(voice_key, VOICES["american_female"])["id"],
    }


@app.post("/api/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """End session and get summary report with LLM-generated narrative + grading."""
    _require_session_owner(session_id, user)
    try:
        summary = store.end_session(session_id)

        # Generate narrative report via LLM
        report = await _generate_session_report(summary)
        summary["report"] = report

        # Generate 5-dimension grading
        session_data = store.get_session(session_id)
        if session_data:
            grading = await grade_session(session_data, llm, LLM_MODEL)
            summary["grading"] = grading
        else:
            summary["grading"] = None

        return summary
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/sessions")
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    user: dict | None = Depends(get_optional_user),
):
    """List past practice sessions."""
    return store.list_sessions(limit=limit, offset=offset, user_id=_user_id(user))


@app.get("/api/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Get detailed summary for a specific session."""
    _require_session_owner(session_id, user)
    try:
        return store.get_summary(session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/sessions/{session_id}/turns-full")
async def get_session_turns_full(
    session_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Get full session data including all turns for playback."""
    return _require_session_owner(session_id, user)


@app.get("/api/sessions/{session_id}/recording/{turn_index}")
async def get_session_recording(
    session_id: str,
    turn_index: int,
    user: dict | None = Depends(get_optional_user),
):
    """Serve the recorded audio file for a specific turn (owner only)."""
    # Ownership check also rejects any session_id with path separators, since
    # such an id can never match a stored session.
    _require_session_owner(session_id, user)
    # Defense in depth: resolve the path and confirm it stays under RECORDINGS_DIR.
    base = RECORDINGS_DIR.resolve()
    recording_path = (base / session_id / f"{turn_index}.webm").resolve()
    if base not in recording_path.parents or not recording_path.exists():
        raise HTTPException(404, "Recording not found")
    return FileResponse(str(recording_path), media_type="audio/webm")


@app.post("/api/sessions/{session_id}/review")
async def generate_session_review(
    session_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Generate an AI review of the full session conversation (owner only)."""
    session = _require_session_owner(session_id, user)

    # Build transcript from turns
    turns = session.get("turns", [])
    transcript_lines = []
    for t in turns:
        transcript_lines.append(f"User: {t.get('user_text', '')}")
        transcript_lines.append(f"AI: {t.get('reply_text', '')}")
    transcript = "\n".join(transcript_lines)

    prompt = f"""请根据以下英语口语练习对话记录，用中文给出详细的复盘评价。

对话记录：
{transcript}

请从以下三个方面进行评价：
1. 整体表现：总体评估学生的口语表达能力
2. 主要错误模式：归纳出现的语法、用词或表达问题
3. 改进建议：给出具体可操作的改进方向

请直接输出评价内容，不要加标题格式。"""

    try:
        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=600,
        )
        review_text = resp.choices[0].message.content or ""
        return {"review": review_text}
    except Exception:
        return {"review": "无法生成评价，请稍后重试。"}


@app.get("/api/progress")
async def get_progress(user: dict | None = Depends(get_optional_user)):
    """Get aggregated progress metrics across all sessions."""
    return store.get_progress(user_id=_user_id(user))


@app.post("/api/progress/grammar-analysis")
async def grammar_analysis(user: dict | None = Depends(get_optional_user)):
    """
    Turn the user's recurring grammar errors into a short, personalized Chinese
    analysis with actionable advice (instead of a bare error list). Computed
    on demand so the dashboard load stays cheap; returns empty when there is
    not enough data to say anything useful.
    """
    progress = store.get_progress(user_id=_user_id(user))
    errors = (progress.get("weakness") or {}).get("common_grammar_errors") or []
    if not errors:
        return {"analysis": "", "tips": []}

    # Compact the patterns for the prompt (cap to keep the call small)
    lines = "\n".join(f"- {e['pattern']} (×{e['count']})" for e in errors[:8])
    try:
        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位英语口语教练。根据学习者反复出现的语法错误，用简体中文写一段"
                        "针对性分析（2-3句，点明错误背后的共性规律，语气鼓励），再给出3条具体、"
                        "可操作的改进建议。只输出 JSON：{\"analysis\": \"...\", \"tips\": [\"...\", \"...\", \"...\"]}"
                    ),
                },
                {"role": "user", "content": f"学习者高频语法错误：\n{lines}"},
            ],
            temperature=0.5,
            max_tokens=400,
        )
        raw = (resp.choices[0].message.content or "{}").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return {
            "analysis": data.get("analysis", ""),
            "tips": data.get("tips", [])[:3],
        }
    except Exception:
        raise HTTPException(502, "Analysis failed")


@app.get("/api/analytics")
async def get_analytics(days: int = 30):
    """Get learning analytics (vocabulary trend, pronunciation curve, etc.)."""
    from .analytics import get_analytics as _get_analytics
    return _get_analytics(days)


# --- Hint System ---

@app.post("/api/translate")
async def translate(text: str = Form(...)):
    """Translate an English message to Simplified Chinese (on-demand, used by chat bubbles)."""
    text = (text or "").strip()
    if not text:
        return {"translation": ""}
    if len(text) > 2000:
        raise HTTPException(413, "Text too long")
    try:
        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a translator. Translate the user's English text into natural Simplified Chinese. Output only the translation, no quotes or explanation."},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return {"translation": resp.choices[0].message.content or ""}
    except Exception:
        raise HTTPException(502, "Translation failed")


@app.post("/api/hint")
async def get_hint(
    scenario: str = Form("smalltalk"),
    history: str = Form("[]"),
):
    """
    Generate response suggestions when user is stuck.
    Returns 2-3 contextual hint options.
    """
    chat_history = json.loads(history)
    messages = build_hint_messages(scenario, chat_history)

    try:
        resp = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=300,
        )
        raw = resp.choices[0].message.content or "[]"
        # Parse JSON from response (strip markdown if present)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        hints = json.loads(raw)
        return {"hints": hints}
    except (json.JSONDecodeError, Exception) as e:
        # Fallback hints
        return {"hints": [
            {"text": "Could you repeat that?", "hint": "能再说一遍吗？", "difficulty": "easy"},
            {"text": "That's interesting! Tell me more.", "hint": "有意思，多说说", "difficulty": "easy"},
        ]}


# --- Level Assessment ---

@app.get("/api/level-test/questions")
async def get_level_test_questions():
    """Get all level test questions."""
    return LEVEL_TEST_QUESTIONS


@app.post("/api/level-test/assess")
async def assess_level(
    responses: str = Form(...),
    user: dict | None = Depends(get_optional_user),
):
    """
    Evaluate user's level based on their responses to test questions.
    Expects JSON array: [{"index": 0, "text": "transcribed response"}, ...]
    """
    try:
        resp_list = json.loads(responses)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid responses format")

    messages = build_assessment_messages(resp_list)

    try:
        result = await llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
        raw = result.choices[0].message.content or "{}"
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        assessment = json.loads(raw)

        # Save to user profile
        profile = profile_store.update_level(_user_id(user), assessment)

        return {"assessment": assessment, "profile": profile}
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(500, f"Assessment failed: {str(e)}")


# --- User Profile ---

@app.get("/api/profile")
async def get_profile(user: dict | None = Depends(get_optional_user)):
    """Get current user profile (level, strengths, weaknesses, affinity)."""
    return profile_store.get_or_create(_user_id(user))


@app.get("/api/profile/memory/{scenario_id}")
async def get_character_memory(
    scenario_id: str,
    user: dict | None = Depends(get_optional_user),
):
    """Get conversation memories for a specific character."""
    uid = _user_id(user)
    memories = profile_store.get_memory(uid, scenario_id)
    affinity = profile_store.get_affinity_level(uid, scenario_id)
    return {"memories": memories, "affinity_level": affinity}



# --- Real-time Pronunciation (WebSocket) ---

from fastapi import WebSocket as _WebSocket


@app.websocket("/ws/realtime-pronunciation")
async def ws_realtime_pronunciation(websocket: _WebSocket):
    """WebSocket endpoint for real-time pronunciation feedback."""
    from .realtime import realtime_pronunciation_endpoint
    await realtime_pronunciation_endpoint(websocket)

# --- Achievements & Check-in ---

@app.get("/api/achievements")
async def get_achievements():
    """Get all achievements with unlock status for current user."""
    progress = store.get_progress()
    all_sessions = []
    for f in sorted(store.data_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            all_sessions.append(data)
        except (json.JSONDecodeError, KeyError):
            continue

    all_pron = [sc for s in all_sessions for sc in s["scores"]["pronunciation"]]
    unique_scenarios = set(s["scenario"] for s in all_sessions)

    stats = {
        "sessions": progress["total_sessions"],
        "turns": progress["total_turns"],
        "max_pronunciation": max(all_pron) if all_pron else 0,
        "unique_scenarios": len(unique_scenarios),
    }

    from .achievements import achievement_store
    achievements = achievement_store.check_achievements(DEFAULT_USER_ID, stats)
    return {"achievements": achievements, "stats": stats}


@app.get("/api/streak")
async def get_streak():
    """Get current streak and check-in calendar."""
    from .achievements import achievement_store
    streak = achievement_store.get_streak(DEFAULT_USER_ID)
    calendar = achievement_store.get_checkin_calendar(DEFAULT_USER_ID)
    return {"streak": streak, "calendar": calendar}


@app.post("/api/checkin")
async def checkin():
    """Record daily check-in (called when a session ends)."""
    from .achievements import achievement_store
    return achievement_store.record_checkin(DEFAULT_USER_ID)


# --- Talent Agent Integration ---

@app.get("/api/integrations/talent-agent/status")
async def talent_agent_status():
    """Check if talent-agent service is reachable."""
    client = get_talent_agent()
    return await client.health_check()


@app.post("/api/integrations/talent-agent/interview-prep")
async def talent_agent_interview_prep(
    jd_text: str = Form(...),
    language: str = Form("en"),
):
    """
    Use talent-agent to analyze a JD and generate targeted interview context.
    Returns key skills and focus areas for interview practice.
    """
    client = get_talent_agent()
    result = await client.get_interview_context(jd_text, language)
    if "error" in result and not result.get("key_skills"):
        raise HTTPException(503, f"Talent agent unavailable: {result['error']}")
    return result


@app.post("/api/integrations/talent-agent/oral-interview-session")
async def talent_agent_oral_interview_session(
    jd_text: str = Form(""),
    resume_text: str = Form(""),
    project_context: str = Form(""),
    language: str = Form("en"),
    user: dict | None = Depends(get_optional_user),
):
    """Create an oral mock interview session from talent-agent context."""
    if language not in {"en", "zh"}:
        raise HTTPException(400, "language must be 'en' or 'zh'")
    if not (jd_text.strip() or resume_text.strip() or project_context.strip()):
        raise HTTPException(400, "At least one interview context field is required")

    prep = None
    if jd_text.strip():
        client = get_talent_agent()
        prep = await client.get_interview_context(jd_text, language)

    prompt_parts = [project_context.strip()]
    if prep and "error" not in prep:
        key_skills = ", ".join(prep.get("key_skills", [])[:8])
        focus_areas = ", ".join(prep.get("focus_areas", [])[:8])
        talent_context = "\n".join(
            part for part in [
                f"Talent-agent key skills: {key_skills}" if key_skills else "",
                f"Talent-agent focus areas: {focus_areas}" if focus_areas else "",
                f"Difficulty: {prep.get('difficulty_level')}" if prep.get("difficulty_level") else "",
            ] if part
        )
        if talent_context:
            prompt_parts.append(talent_context)

    prompt = build_custom_interview_prompt(
        jd_text=jd_text,
        resume_text=resume_text,
        project_context="\n\n".join(part for part in prompt_parts if part),
        language=language,
    )
    session = store.create_session("interview", custom_prompt=prompt, user_id=_user_id(user))
    greeting = (
        "你好，欢迎参加这次岗位口语模拟面试。我们会围绕 JD、你的背景和项目经历展开。请先用 1 分钟介绍你自己。"
        if language == "zh"
        else "Hello, welcome to your role-focused oral mock interview. We'll use the JD, your background, and your project context. Please start with a one-minute self-introduction."
    )
    store.update_session_fields(
        session["id"],
        greeting=greeting,
        language=language,
        talent_agent=prep,
    )
    return {
        "session_id": session["id"],
        "redirect_url": f"/chat/interview?session_id={session['id']}",
        "greeting": greeting,
        "language": language,
        "talent_agent": prep,
    }


@app.post("/api/integrations/talent-agent/sync")
async def talent_agent_sync(
    session_id: str = Form(...),
    user: dict | None = Depends(get_optional_user),
):
    """Sync a completed practice session to talent-agent."""
    _require_session_owner(session_id, user)

    summary = store.get_summary(session_id)
    client = get_talent_agent()
    result = await client.sync_practice_result(summary)
    return result


# --- Daily Tip ---

@app.get("/api/daily-tip")
async def get_daily_tip():
    """Return a random vocabulary/expression/tip from learning guides."""
    import random
    from .learning_guide import SCENARIO_GUIDES

    all_items = []
    for scenario_id, guide in SCENARIO_GUIDES.items():
        for v in guide.get("vocabulary", []):
            all_items.append({"type": "vocabulary", "scenario": guide["title"], **v})
        for e in guide.get("expressions", []):
            all_items.append({"type": "expression", "scenario": guide["title"], **e})
        for t in guide.get("tips", []):
            all_items.append({"type": "tip", "scenario": guide["title"], **t})

    if not all_items:
        return {"tip": None}

    # Use date as seed for daily consistency
    from datetime import date
    today = date.today()
    random.seed(today.isoformat())
    tip = random.choice(all_items)
    random.seed()  # Reset seed
    return {"date": today.isoformat(), "tip": tip}


# --- Scenario Difficulty Recommendation ---

@app.get("/api/recommend")
async def recommend_scenarios():
    """Recommend scenarios based on user's assessed level."""
    profile = profile_store.get_or_create(DEFAULT_USER_ID)
    level = profile.get("level")

    level_to_difficulty = {
        "A1": ["beginner"],
        "A2": ["beginner", "intermediate"],
        "B1": ["intermediate"],
        "B2": ["intermediate", "advanced"],
        "C1": ["advanced"],
        "C2": ["advanced"],
    }

    if not level:
        # No assessment yet — recommend beginner + one intermediate
        recommended = [s for s in SCENARIOS if s["difficulty"] == "beginner"][:4]
        recommended += [s for s in SCENARIOS if s["difficulty"] == "intermediate"][:2]
        return {
            "level": None,
            "message": "Take the level test for personalized recommendations!",
            "scenarios": recommended,
        }

    difficulties = level_to_difficulty.get(level, ["intermediate"])
    recommended = [s for s in SCENARIOS if s["difficulty"] in difficulties]

    # Deprioritize scenarios the user has already practiced a lot
    affinity = profile.get("character_affinity", {})
    recommended.sort(key=lambda s: affinity.get(s["id"], 0))

    return {
        "level": level,
        "difficulties": difficulties,
        "scenarios": recommended[:8],
    }
