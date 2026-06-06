"""Tests for the personalized grammar-analysis endpoint."""
import json

from fastapi.testclient import TestClient

import assessment.app as app_module
from assessment.app import app


class _FakeMessage:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})


class _FakeCompletions:
    async def create(self, **kwargs):
        payload = json.dumps({
            "analysis": "你经常在时态和冠词上出错，说明对句子结构的整体把握还需加强。",
            "tips": ["朗读时刻意放慢，关注动词时态", "每天复述一句修改后的正确句", "多读简单英文短文培养语感"],
        })
        return type("R", (), {"choices": [_FakeMessage(payload)]})


class _FakeLLM:
    chat = type("C", (), {"completions": _FakeCompletions()})


def test_grammar_analysis_empty_when_no_errors(monkeypatch):
    # No grammar errors → returns empty without calling the LLM
    monkeypatch.setattr(
        app_module.store, "get_progress",
        lambda user_id=None: {"weakness": {"common_grammar_errors": []}},
    )
    client = TestClient(app)
    resp = client.post("/api/progress/grammar-analysis")
    assert resp.status_code == 200
    assert resp.json() == {"analysis": "", "tips": []}


def test_grammar_analysis_returns_advice(monkeypatch):
    monkeypatch.setattr(
        app_module.store, "get_progress",
        lambda user_id=None: {
            "weakness": {
                "common_grammar_errors": [
                    {"pattern": "missing article 'the'", "count": 5},
                    {"pattern": "past tense agreement", "count": 3},
                ]
            }
        },
    )
    monkeypatch.setattr(app_module, "llm", _FakeLLM())
    client = TestClient(app)
    resp = client.post("/api/progress/grammar-analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert "时态" in data["analysis"]
    assert len(data["tips"]) == 3
