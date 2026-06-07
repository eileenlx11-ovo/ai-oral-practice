"""Tests for character metadata and session character switching."""
import uuid

from fastapi.testclient import TestClient

import assessment.app as app_module
from assessment.app import app
from assessment.characters import CHARACTERS, list_characters
from assessment.feedback import SessionStore
from assessment.scenarios import get_system_prompt


def test_list_characters_returns_lightweight_metadata():
    characters = list_characters()
    assert len(characters) == len(CHARACTERS)
    assert len(characters) >= 18
    assert set(characters[0]) == {"id", "name", "avatar", "role", "voice"}
    # background is an optional enrichment field; when present it must be non-empty
    assert all(character["background"] for character in CHARACTERS.values() if "background" in character)


def test_system_prompt_includes_background_without_recitation_instruction():
    prompt = get_system_prompt("coffee_shop")
    assert "Background:" in prompt
    assert CHARACTERS["coffee_shop"]["background"] in prompt
    assert "do not proactively recite the background" in prompt


def test_switch_session_character_updates_session_and_requires_owner(tmp_path, monkeypatch):
    test_store = SessionStore(data_dir=tmp_path)
    monkeypatch.setattr(app_module, "store", test_store)
    client = TestClient(app)
    email = f"character-switch-{uuid.uuid4().hex}@example.com"

    register = client.post(
        "/api/auth/register",
        data={"email": email, "password": "abcdef"},
    )
    assert register.status_code == 200
    headers = {"Authorization": f"Bearer {register.json()['token']}"}

    created = client.post("/api/sessions", headers=headers, data={"scenario": "smalltalk"})
    assert created.status_code == 200
    session_id = created.json()["session_id"]

    guest_switch = client.post(
        f"/api/sessions/{session_id}/character",
        data={"scenario": "coffee_shop"},
    )
    assert guest_switch.status_code == 404

    switched = client.post(
        f"/api/sessions/{session_id}/character",
        headers=headers,
        data={"scenario": "coffee_shop", "voice": "british_female"},
    )
    assert switched.status_code == 200
    body = switched.json()
    assert body["scenario"] == "coffee_shop"
    assert body["character"]["name"] == CHARACTERS["coffee_shop"]["name"]
    assert body["voice"] == "british_female"

    session = test_store.get_session(session_id)
    assert session["scenario"] == "coffee_shop"
    assert session["voice"] == "british_female"


def test_talent_agent_oral_interview_session_creates_custom_prompt(tmp_path, monkeypatch):
    class FakeTalentAgent:
        async def get_interview_context(self, jd_text, language):
            return {
                "key_skills": ["Python", "FastAPI"],
                "focus_areas": ["async design"],
                "difficulty_level": "intermediate",
            }

    test_store = SessionStore(data_dir=tmp_path)
    monkeypatch.setattr(app_module, "store", test_store)
    monkeypatch.setattr(app_module, "get_talent_agent", lambda: FakeTalentAgent())
    client = TestClient(app)

    response = client.post(
        "/api/integrations/talent-agent/oral-interview-session",
        data={
            "jd_text": "Backend intern role",
            "resume_text": "Built an oral practice app",
            "project_context": "SSE voice interview workflow",
            "language": "zh",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["redirect_url"] == f"/chat/interview?session_id={body['session_id']}"
    assert body["language"] == "zh"

    session = test_store.get_session(body["session_id"])
    assert session["scenario"] == "interview"
    assert session["language"] == "zh"
    assert session["greeting"].startswith("你好")
    assert "job interview in Chinese" in session["custom_prompt"]
    assert "Backend intern role" in session["custom_prompt"]
    assert "Talent-agent key skills: Python, FastAPI" in session["custom_prompt"]
    assert "Talent-agent focus areas: async design" in session["custom_prompt"]

    handoff = client.get(f"/api/sessions/{body['session_id']}/handoff")
    assert handoff.status_code == 200
    assert handoff.json()["greeting"].startswith("你好")
    assert handoff.json()["language"] == "zh"
