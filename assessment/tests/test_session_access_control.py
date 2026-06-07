"""Access-control tests for session playback, recording, and review routes.

These three routes previously returned session data without an owner check
(arch_security review 2026-06-07). Each test asserts a non-owner gets 404 while
the owner succeeds.
"""
import uuid

from fastapi.testclient import TestClient

import assessment.app as app_module
from assessment.app import app
from assessment.feedback import SessionStore


def _register(client, suffix):
    email = f"{suffix}-{uuid.uuid4().hex}@example.com"
    res = client.post("/api/auth/register", data={"email": email, "password": "abcdef"})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['token']}"}


def test_turns_full_requires_owner(tmp_path, monkeypatch):
    test_store = SessionStore(data_dir=tmp_path)
    monkeypatch.setattr(app_module, "store", test_store)
    client = TestClient(app)
    owner = _register(client, "owner")
    other = _register(client, "other")

    session_id = client.post(
        "/api/sessions", headers=owner, data={"scenario": "smalltalk"}
    ).json()["session_id"]

    # Non-owner and anonymous both get 404 (existence is not leaked).
    assert client.get(f"/api/sessions/{session_id}/turns-full", headers=other).status_code == 404
    assert client.get(f"/api/sessions/{session_id}/turns-full").status_code == 404
    # Owner succeeds.
    assert client.get(f"/api/sessions/{session_id}/turns-full", headers=owner).status_code == 200


def test_recording_requires_owner_and_rejects_traversal(tmp_path, monkeypatch):
    test_store = SessionStore(data_dir=tmp_path)
    monkeypatch.setattr(app_module, "store", test_store)
    client = TestClient(app)
    owner = _register(client, "owner")
    other = _register(client, "other")

    session_id = client.post(
        "/api/sessions", headers=owner, data={"scenario": "smalltalk"}
    ).json()["session_id"]

    # Non-owner blocked (404, not the recording).
    assert client.get(f"/api/sessions/{session_id}/recording/0", headers=other).status_code == 404
    # Owner with no recording on disk gets 404 (not a 500), proving the path
    # check runs after a successful owner check.
    assert client.get(f"/api/sessions/{session_id}/recording/0", headers=owner).status_code == 404


def test_review_requires_owner(tmp_path, monkeypatch):
    test_store = SessionStore(data_dir=tmp_path)
    monkeypatch.setattr(app_module, "store", test_store)
    client = TestClient(app)
    owner = _register(client, "owner")
    other = _register(client, "other")

    session_id = client.post(
        "/api/sessions", headers=owner, data={"scenario": "smalltalk"}
    ).json()["session_id"]

    # Non-owner cannot trigger a review (which would leak transcript + burn LLM).
    assert client.post(f"/api/sessions/{session_id}/review", headers=other).status_code == 404
    assert client.post(f"/api/sessions/{session_id}/review").status_code == 404
