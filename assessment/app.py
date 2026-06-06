"""
Assessment backend - AI English Oral Practice
FastAPI server providing chat, ASR proxy, pronunciation scoring, and session tracking.
Enhanced with: hint system, level assessment, character memory, talent-agent integration.
"""
import os
import json
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
from .scenarios import SCENARIOS, CATEGORIES, VOICES, get_system_prompt, get_voice_for_scenario, get_practice_sentences, build_custom_interview_prompt
from .characters import CHARACTERS, get_character, list_characters
from .correction import extract_corrections
from .scoring import assess_pronunciation, active_provider
from .feedback import store
from .streaming import SentenceSplitter, synthesize_sentence
from .hints import build_hint_messages
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


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    """Get pronunciation practice sentences for a scenario."""
    sentences = get_practice_sentences(scenario_id)
    return {"scenario_id": scenario_id, "sentences": sentences}


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
        user_text = await _transcribe(tmp.name)
        if not user_text.strip():
            raise HTTPException(400, "No speech detected")

        # 3. LLM conversation + correction
        chat_history = json.loads(history)
        reply_text, corrections, scene_marker_seen = await _chat_with_correction(
            scenario, user_text, chat_history, session=store.get_session(session_id)
        )

        scene_advanced = False
        story_completed = False
        current_session = store.get_session(session_id)
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
                user_text = await _transcribe(tmp.name)
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
                store.add_turn(session_id, user_text, reply_text, corrections)
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

# ASR client (SiliconFlow — OpenAI-compatible, domestic)
_asr_client = AsyncOpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY", "") or "sk-placeholder",
    base_url="https://api.siliconflow.cn/v1",
)


async def _transcribe(filepath: str) -> str:
    """Transcribe audio file via SiliconFlow ASR."""
    model = os.getenv("ASR_MODEL", "FunAudioLLM/SenseVoiceSmall")
    with open(filepath, "rb") as f:
        resp = await _asr_client.audio.transcriptions.create(
            model=model,
            file=f,
            language="en",
            prompt="English oral practice conversation.",
        )
    return resp.text


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
    """End session and get summary report with LLM-generated narrative."""
    _require_session_owner(session_id, user)
    try:
        summary = store.end_session(session_id)

        # Generate narrative report via LLM
        report = await _generate_session_report(summary)
        summary["report"] = report
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
