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
    assert len(characters) == len(CHARACTERS) == 18
    assert set(characters[0]) == {"id", "name", "avatar", "role", "voice"}
    assert all("background" in character for character in CHARACTERS.values())


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
