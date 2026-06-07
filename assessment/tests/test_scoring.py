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


def test_tencent_normalize_extracts_phones():
    """PhoneInfos → words[].phones with IPA symbol + per-phoneme accuracy."""
    from assessment.scoring import tencent
    response = {
        "result": {
            "SuggestedScore": 82.0,
            "PronAccuracy": 80.0,
            "PronFluency": 90.0,
            "PronCompletion": 100.0,
            "word_list": [
                {
                    "word": "cat",
                    "pron_accuracy": 45.0,
                    "phone_list": [
                        {"phone": "k", "ref_phone": "k", "pron_accuracy": 95.0},
                        {"phone": "æ", "ref_phone": "æ", "pron_accuracy": 30.0},
                        {"phone": "t", "ref_phone": "t", "pron_accuracy": 88.0},
                    ],
                }
            ],
        }
    }
    out = tencent._normalize(response)
    word = out["words"][0]
    assert word["word"] == "cat"
    assert word["error_type"] == "Mispronunciation"
    assert len(word["phones"]) == 3
    assert word["phones"][1]["phone"] == "æ"
    assert word["phones"][1]["accuracy_score"] == 30.0
    # weakest phone below threshold → surfaced as a tip
    assert word["tip"] == "æ"


def test_tencent_normalize_omits_phones_when_absent():
    """No phoneme data → no `phones` key (clean fallback, e.g. IPA disabled)."""
    from assessment.scoring import tencent
    response = {"result": {"word_list": [{"word": "ok", "pron_accuracy": 90.0}]}}
    out = tencent._normalize(response)
    assert "phones" not in out["words"][0]
    assert "tip" not in out["words"][0]


def test_tencent_ipa_prefix_preserves_eval_mode(monkeypatch):
    """The {::cmd{F_IPA=true}} prefix must not flip word/sentence eval_mode."""
    from assessment.scoring import tencent
    monkeypatch.setenv("TENCENT_APP_ID", "123456")
    monkeypatch.setenv("TENCENT_SECRET_ID", "sid")
    monkeypatch.setenv("TENCENT_SECRET_KEY", "skey")
    monkeypatch.setenv("TENCENT_ENABLE_IPA", "1")
    # single word stays word-mode (0) despite the multi-token command prefix
    url = tencent._signed_url("cat")
    assert "eval_mode=0" in url
    assert "F_IPA" in url
    # phrase stays sentence-mode (1)
    url2 = tencent._signed_url("the quick brown fox")
    assert "eval_mode=1" in url2


def test_tencent_ipa_can_be_disabled(monkeypatch):
    from assessment.scoring import tencent
    monkeypatch.setenv("TENCENT_APP_ID", "123456")
    monkeypatch.setenv("TENCENT_SECRET_ID", "sid")
    monkeypatch.setenv("TENCENT_SECRET_KEY", "skey")
    monkeypatch.setenv("TENCENT_ENABLE_IPA", "0")
    url = tencent._signed_url("cat")
    assert "F_IPA" not in url
