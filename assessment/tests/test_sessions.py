"""Unit tests for session storage and progress tracking."""
import json
import tempfile
import shutil
from pathlib import Path
import pytest

from assessment.feedback import SessionStore


@pytest.fixture
def tmp_store(tmp_path):
    """Create a temporary session store."""
    return SessionStore(data_dir=tmp_path)


def test_create_session(tmp_store):
    session = tmp_store.create_session("interview")
    assert session["scenario"] == "interview"
    assert session["id"]
    assert session["turns"] == []
    assert session["corrections_count"] == 0


def test_add_turn(tmp_store):
    session = tmp_store.create_session("restaurant")
    turn = tmp_store.add_turn(
        session["id"],
        user_text="I want to ordering a pizza",
        reply_text="Of course! What toppings would you like?",
        corrections=[{
            "original": "to ordering",
            "corrected": "to order",
            "explanation": "Use base form after 'to'",
        }],
        pronunciation={"pronunciation_score": 72.5, "fluency_score": 80.0, "accuracy_score": 68.0},
    )
    assert turn["index"] == 0
    assert turn["user_text"] == "I want to ordering a pizza"

    # Verify persistence
    loaded = tmp_store.get_session(session["id"])
    assert len(loaded["turns"]) == 1
    assert loaded["corrections_count"] == 1
    assert loaded["scores"]["pronunciation"] == [72.5]


def test_end_session_summary(tmp_store):
    session = tmp_store.create_session("meeting")
    tmp_store.add_turn(session["id"], "user1", "reply1", [], {"pronunciation_score": 80.0, "fluency_score": 85.0, "accuracy_score": 78.0})
    tmp_store.add_turn(session["id"], "user2", "reply2", [{"original": "x", "corrected": "y", "explanation": "z"}], {"pronunciation_score": 85.0, "fluency_score": 88.0, "accuracy_score": 82.0})

    summary = tmp_store.end_session(session["id"])
    assert summary["total_turns"] == 2
    assert summary["total_corrections"] == 1
    assert summary["avg_pronunciation"] == 82.5  # (80+85)/2
    assert summary["avg_fluency"] == 86.5


def test_list_sessions(tmp_store):
    tmp_store.create_session("travel")
    tmp_store.create_session("smalltalk")
    sessions = tmp_store.list_sessions()
    assert len(sessions) == 2


def test_progress_empty(tmp_store):
    progress = tmp_store.get_progress()
    assert progress["total_sessions"] == 0
    assert progress["avg_pronunciation"] is None


def test_progress_with_data(tmp_store):
    s1 = tmp_store.create_session("interview")
    tmp_store.add_turn(s1["id"], "u", "r", [], {"pronunciation_score": 70.0, "fluency_score": 75.0, "accuracy_score": 72.0})
    s2 = tmp_store.create_session("travel")
    tmp_store.add_turn(s2["id"], "u", "r", [], {"pronunciation_score": 80.0, "fluency_score": 85.0, "accuracy_score": 82.0})

    progress = tmp_store.get_progress()
    assert progress["total_sessions"] == 2
    assert progress["total_turns"] == 2
    assert progress["avg_pronunciation"] == 75.0  # (70+80)/2
    assert len(progress["score_history"]) == 2
