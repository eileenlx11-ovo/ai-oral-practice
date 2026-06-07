"""
Assessment backend - AI English Oral Practice
FastAPI server providing chat, ASR proxy, pronunciation scoring, and session tracking.
Enhanced with: hint system, level assessment, character memory, talent-agent integration.
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
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from .scenarios import SCENARIOS, CATEGORIES, VOICES, get_system_prompt, get_voice_for_scenario, get_practice_sentences, build_custom_interview_prompt
from .characters import get_character
from .correction import extract_corrections
from .scoring import assess_pronunciation, active_provider
from .feedback import store
from .streaming import SentenceSplitter, synthesize_sentence
from .hints import build_hint_messages
from .grading import grade_session
from .level_test import LEVEL_TEST_QUESTIONS, build_assessment_messages
from .user_profile import profile_store, DEFAULT_USER_ID
from .integrations.talent_agent import get_talent_agent

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


async def _read_audio(audio: UploadFile) -> bytes:
    """Read and validate uploaded audio size."""
    data = await audio.read()
    if len(data) > _MAX_AUDIO_BYTES:
        raise HTTPException(413, "Audio file too large (max 10MB)")
    if len(data) < 100:
        raise HTTPException(400, "Audio file too small or empty")
    return data


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
        session = store.create_session(scenario)
        session_id = session["id"]

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
        reply_text, corrections = await _chat_with_correction(
            scenario, user_text, chat_history
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
        session = store.create_session(scenario)
        session_id = session["id"]

    # Resolve system prompt: session-level custom prompt overrides scenario prompt.
    existing = store.get_session(session_id)
    if existing and existing.get("custom_prompt"):
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
            user_text = await _transcribe(tmp.name)
            if not user_text.strip():
                yield _sse("error", {"message": "No speech detected"})
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
                        audio_url = await synthesize_sentence(clean, voice=tts_voice)
                        yield _sse("sentence", {
                            "index": sent["index"],
                            "text": clean,
                            "audio_url": audio_url,
                        })

            # Flush remaining buffer
            remaining = splitter.flush()
            if remaining and "[CORRECTIONS]" not in remaining["text"] and "[END]" not in remaining["text"]:
                clean = _clean_sentence(remaining["text"])
                if clean:
                    audio_url = await synthesize_sentence(clean, voice=tts_voice)
                    yield _sse("sentence", {
                        "index": remaining["index"],
                        "text": clean,
                        "audio_url": audio_url,
                    })

            # 3. Parse corrections and feedback from full reply
            from .correction import extract_feedback
            reply_text, corrections = extract_corrections(full_reply)
            feedback = extract_feedback(full_reply)

            if corrections:
                yield _sse("corrections", corrections)

            if feedback:
                yield _sse("feedback", {"text": feedback})

            # 4. Save to session & update affinity
            try:
                store.add_turn(session_id, user_text, reply_text, corrections)
                profile_store.increment_affinity(DEFAULT_USER_ID, scenario)
            except ValueError:
                pass

            yield _sse("done", {
                "session_id": session_id,
                "full_reply": reply_text,
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


# --- Internal helpers ---

# ASR client — configurable provider (Groq Whisper / SiliconFlow / custom)
_asr_base_url = os.getenv("ASR_BASE_URL", "https://api.groq.com/openai/v1")
_asr_api_key = os.getenv("ASR_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("SILICONFLOW_API_KEY") or "sk-placeholder"

# Groq needs proxy in China; httpx picks up standard env vars (HTTPS_PROXY / ALL_PROXY)
import httpx as _httpx
_asr_http_client = None
_proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("ALL_PROXY") or os.getenv("HTTP_PROXY")
if _proxy_url and "groq" in _asr_base_url:
    _asr_http_client = _httpx.AsyncClient(proxy=_proxy_url)

_asr_client = AsyncOpenAI(
    api_key=_asr_api_key,
    base_url=_asr_base_url,
    http_client=_asr_http_client,
)


async def _transcribe(filepath: str) -> str:
    """Transcribe audio file via configured ASR provider (default: Groq Whisper)."""
    model = os.getenv("ASR_MODEL", "whisper-large-v3-turbo")
    with open(filepath, "rb") as f:
        resp = await _asr_client.audio.transcriptions.create(
            model=model,
            file=f,
            language="en",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    # Store word-level timestamps if available (for fluency analysis)
    if hasattr(resp, 'words') and resp.words:
        _transcribe._last_words = resp.words
    else:
        _transcribe._last_words = None

    # Return text — handle both object and dict response formats
    if hasattr(resp, 'text'):
        return resp.text
    if isinstance(resp, dict):
        return resp.get('text', '')
    return str(resp)

_transcribe._last_words = None


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
    }


# --- Session & Progress APIs ---

@app.post("/api/sessions")
async def create_session(scenario: str = Form("smalltalk")):
    """Start a new practice session."""
    session = store.create_session(scenario)
    return {"session_id": session["id"]}


@app.post("/api/sessions/custom")
async def create_custom_session(
    jd_text: str = Form(""),
    resume_text: str = Form(""),
    project_context: str = Form(""),
):
    """Start a customized interview session.

    Builds an interviewer prompt from a job description, candidate background,
    and/or project context. Designed to be called by external tools (e.g.
    talent-agent). The resulting session_id is used with /api/stream as usual;
    the stream endpoint will pick up this session's custom prompt automatically.
    """
    if not (jd_text.strip() or resume_text.strip() or project_context.strip()):
        raise HTTPException(400, "At least one of jd_text, resume_text, or project_context is required")
    prompt = build_custom_interview_prompt(jd_text, resume_text, project_context)
    session = store.create_session("interview", custom_prompt=prompt)
    return {
        "session_id": session["id"],
        "greeting": "Hello! Thanks for coming in today. I've reviewed the role and your background. To start, could you walk me through your experience and why this position interests you?",
    }


@app.post("/api/sessions/{session_id}/turns")
async def add_session_turn(
    session_id: str,
    user_text: str = Form(...),
    reply_text: str = Form(...),
    corrections: str = Form("[]"),
    pronunciation: str = Form("null"),
):
    """Record a conversation turn to the session."""
    try:
        corr_list = json.loads(corrections)
        pron_data = json.loads(pronunciation)
        turn = store.add_turn(session_id, user_text, reply_text, corr_list, pron_data)
        return turn
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.post("/api/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End session and get summary report with LLM-generated narrative + grading."""
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
async def list_sessions(limit: int = 20, offset: int = 0):
    """List past practice sessions."""
    return store.list_sessions(limit=limit, offset=offset)


@app.get("/api/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get detailed summary for a specific session."""
    try:
        return store.get_summary(session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/progress")
async def get_progress():
    """Get aggregated progress metrics across all sessions."""
    return store.get_progress()


@app.get("/api/analytics")
async def get_analytics(days: int = 30):
    """Get learning analytics (vocabulary trend, pronunciation curve, etc.)."""
    from .analytics import get_analytics as _get_analytics
    return _get_analytics(days)


# --- Hint System ---

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
        profile = profile_store.update_level(DEFAULT_USER_ID, assessment)

        return {"assessment": assessment, "profile": profile}
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(500, f"Assessment failed: {str(e)}")


# --- User Profile ---

@app.get("/api/profile")
async def get_profile():
    """Get current user profile (level, strengths, weaknesses, affinity)."""
    return profile_store.get_or_create(DEFAULT_USER_ID)


@app.get("/api/profile/memory/{scenario_id}")
async def get_character_memory(scenario_id: str):
    """Get conversation memories for a specific character."""
    memories = profile_store.get_memory(DEFAULT_USER_ID, scenario_id)
    affinity = profile_store.get_affinity_level(DEFAULT_USER_ID, scenario_id)
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


@app.post("/api/integrations/talent-agent/sync")
async def talent_agent_sync(session_id: str = Form(...)):
    """Sync a completed practice session to talent-agent."""
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(404, "Session not found")

    summary = store.get_summary(session_id)
    client = get_talent_agent()
    result = await client.sync_practice_result(summary)
    return result
