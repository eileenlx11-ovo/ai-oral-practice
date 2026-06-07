"""Tests for story-mode definitions and API wiring."""

from fastapi.testclient import TestClient

from assessment.app import app
from assessment.feedback import store
from assessment.stories import (
    ADVANCE_MARKER,
    build_story_prompt,
    get_story,
    list_stories,
    next_scene_index,
    strip_scene_advance_marker,
)


def test_list_stories_is_lightweight():
    stories = list_stories()

    assert len(stories) >= 3
    assert {"id", "title", "title_zh", "cover_emoji", "difficulty", "synopsis_zh"} <= set(stories[0])
    assert "scenes" not in stories[0]


def test_get_story_and_prompt_include_scene_goal():
    story = get_story("airport_rebook")
    prompt = build_story_prompt("airport_rebook", 0)

    assert story["title_zh"] == "机场误机改签危机"
    assert story["scenes"][0]["goal"] in prompt
    assert ADVANCE_MARKER in prompt


def test_strip_scene_advance_marker():
    text, advanced = strip_scene_advance_marker(f"Great, I can help. {ADVANCE_MARKER}")

    assert advanced is True
    assert ADVANCE_MARKER not in text
    assert text == "Great, I can help."


def test_next_scene_index_progresses_until_last_scene():
    story = get_story("airport_rebook")
    last_index = len(story["scenes"]) - 1

    next_index, advanced, completed = next_scene_index("airport_rebook", 0)
    assert next_index == 1
    assert advanced is True
    assert completed is False

    next_index, advanced, completed = next_scene_index("airport_rebook", last_index)
    assert next_index == last_index
    assert advanced is False
    assert completed is True

    next_index, advanced, completed = next_scene_index("airport_rebook", last_index - 1)
    assert next_index == last_index
    assert advanced is True
    assert completed is False


def test_story_api_list_detail_and_start():
    client = TestClient(app)

    list_res = client.get("/api/stories")
    assert list_res.status_code == 200
    assert any(item["id"] == "airport_rebook" for item in list_res.json())

    detail_res = client.get("/api/stories/airport_rebook")
    assert detail_res.status_code == 200
    assert detail_res.json()["scenes"][0]["setup_zh"]

    start_res = client.post("/api/stories/airport_rebook/start")
    assert start_res.status_code == 200
    payload = start_res.json()
    assert payload["scene_index"] == 0
    assert payload["ai_opening"]

    session = store.get_session(payload["session_id"])
    assert session["story_id"] == "airport_rebook"
    assert session["story_scene_index"] == 0
    assert session["greeting"] == payload["ai_opening"]
