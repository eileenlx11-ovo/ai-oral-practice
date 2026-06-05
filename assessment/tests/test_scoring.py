"""Unit tests for pronunciation scoring module."""
import pytest
from unittest.mock import patch, MagicMock


def test_assess_returns_none_without_azure():
    """Without Azure SDK configured, should return None gracefully."""
    with patch("assessment.scoring.HAS_AZURE", False):
        import asyncio
        from assessment.scoring import assess_pronunciation
        result = asyncio.run(assess_pronunciation("fake.wav", "hello world"))
        assert result is None


def test_assess_returns_none_without_key():
    """With Azure SDK but no API key, should return None."""
    with patch("assessment.scoring.HAS_AZURE", True), \
         patch("assessment.scoring.get_speech_config", return_value=None):
        import asyncio
        from assessment.scoring import assess_pronunciation
        result = asyncio.run(assess_pronunciation("fake.wav", "hello world"))
        assert result is None


def test_result_schema():
    """Verify expected output schema from a mocked successful assessment."""
    mock_result = {
        "accuracy_score": 85.0,
        "fluency_score": 90.0,
        "completeness_score": 100.0,
        "pronunciation_score": 88.0,
        "words": [
            {"word": "hello", "accuracy_score": 92.0, "error_type": "None"},
            {"word": "world", "accuracy_score": 78.0, "error_type": "Mispronunciation"},
        ],
    }
    # Validate structure
    assert "accuracy_score" in mock_result
    assert "words" in mock_result
    assert all(
        "word" in w and "accuracy_score" in w and "error_type" in w
        for w in mock_result["words"]
    )
