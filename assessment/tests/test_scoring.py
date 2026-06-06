"""Unit tests for multi-provider pronunciation scoring."""
import asyncio
import pytest

from assessment import scoring
from assessment.scoring import mock as mock_provider


def test_mock_always_available():
    assert mock_provider.available() is True


def test_mock_assess_schema():
    result = asyncio.run(mock_provider.assess("fake.wav", "Hello world today"))
    assert set(result) >= {
        "accuracy_score", "fluency_score", "completeness_score",
        "pronunciation_score", "words", "provider",
    }
    assert result["provider"] == "mock"
    assert len(result["words"]) == 3
    assert all(0 <= w["accuracy_score"] <= 100 for w in result["words"])
    assert all(w["error_type"] in ("None", "Mispronunciation") for w in result["words"])


def test_mock_is_deterministic():
    a = asyncio.run(mock_provider.assess("x.wav", "the quick brown fox"))
    b = asyncio.run(mock_provider.assess("y.wav", "the quick brown fox"))
    assert a == b


def test_dispatch_falls_back_to_mock(monkeypatch):
    """With no real provider keys, dispatcher uses mock."""
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("TENCENT_APP_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_KEY", raising=False)
    monkeypatch.setenv("PRONUNCIATION_ALLOW_MOCK", "1")
    assert scoring.active_provider() == "mock"
    result = asyncio.run(scoring.assess_pronunciation("fake.wav", "hello world"))
    assert result is not None
    assert result["provider"] == "mock"


def test_dispatch_returns_none_when_mock_disabled(monkeypatch):
    """Mock disabled + no real keys → None (endpoint should 503)."""
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("TENCENT_APP_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_KEY", raising=False)
    monkeypatch.setenv("PRONUNCIATION_ALLOW_MOCK", "0")
    assert scoring.active_provider() is None
    result = asyncio.run(scoring.assess_pronunciation("fake.wav", "hello world"))
    assert result is None


def test_azure_unavailable_without_key(monkeypatch):
    from assessment.scoring import azure
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    assert azure.available() is False


def test_tencent_unavailable_without_keys(monkeypatch):
    from assessment.scoring import tencent
    monkeypatch.delenv("TENCENT_APP_ID", raising=False)
    monkeypatch.delenv("TENCENT_APPID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_ID", raising=False)
    monkeypatch.delenv("TENCENT_SECRET_KEY", raising=False)
    assert tencent.available() is False


def test_tencent_requires_app_id(monkeypatch):
    from assessment.scoring import tencent
    monkeypatch.setenv("TENCENT_SECRET_ID", "sid")
    monkeypatch.setenv("TENCENT_SECRET_KEY", "skey")
    monkeypatch.delenv("TENCENT_APP_ID", raising=False)
    monkeypatch.delenv("TENCENT_APPID", raising=False)
    assert tencent.available() is False


def test_tencent_available_with_new_edition_credentials(monkeypatch):
    from assessment.scoring import tencent
    monkeypatch.setenv("TENCENT_APP_ID", "123456")
    monkeypatch.setenv("TENCENT_SECRET_ID", " sid ")
    monkeypatch.setenv("TENCENT_SECRET_KEY", " skey ")
    assert tencent.available() is True


def test_tencent_accepts_appid_alias(monkeypatch):
    from assessment.scoring import tencent
    monkeypatch.delenv("TENCENT_APP_ID", raising=False)
    monkeypatch.setenv("TENCENT_APPID", "123456")
    monkeypatch.setenv("TENCENT_SECRET_ID", "sid")
    monkeypatch.setenv("TENCENT_SECRET_KEY", "skey")
    assert tencent.available() is True
