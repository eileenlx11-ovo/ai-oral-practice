"""Tests for the on-demand translation endpoint."""
from fastapi.testclient import TestClient

import assessment.app as app_module
from assessment.app import app


class _FakeMessage:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})


class _FakeCompletions:
    async def create(self, **kwargs):
        # Echo a deterministic translation so the test is LLM-independent
        return type("R", (), {"choices": [_FakeMessage("你好，世界")]})


class _FakeLLM:
    chat = type("C", (), {"completions": _FakeCompletions()})


def test_translate_returns_chinese(monkeypatch):
    monkeypatch.setattr(app_module, "llm", _FakeLLM())
    client = TestClient(app)
    resp = client.post("/api/translate", data={"text": "Hello, world"})
    assert resp.status_code == 200
    assert resp.json()["translation"] == "你好，世界"


def test_translate_empty_text_returns_empty():
    client = TestClient(app)
    resp = client.post("/api/translate", data={"text": "   "})
    assert resp.status_code == 200
    assert resp.json()["translation"] == ""
