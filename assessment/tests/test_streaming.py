"""Unit tests for streaming sentence splitter."""
from assessment.streaming import SentenceSplitter


def test_single_sentence():
    s = SentenceSplitter()
    results = s.feed("Hello there! ")
    assert len(results) == 1
    assert results[0]["text"] == "Hello there!"
    assert results[0]["index"] == 0


def test_multiple_sentences():
    s = SentenceSplitter()
    results = s.feed("First sentence. Second one! Third? ")
    assert len(results) == 3
    assert results[0]["text"] == "First sentence."
    assert results[1]["text"] == "Second one!"
    assert results[2]["text"] == "Third?"


def test_incremental_tokens():
    s = SentenceSplitter()
    assert s.feed("I would ") == []
    assert s.feed("like to ") == []
    results = s.feed("help you. ")
    assert len(results) == 1
    assert results[0]["text"] == "I would like to help you."


def test_flush_remaining():
    s = SentenceSplitter()
    s.feed("This is incomplete")
    remaining = s.flush()
    assert remaining is not None
    assert remaining["text"] == "This is incomplete"


def test_flush_empty():
    s = SentenceSplitter()
    s.feed("Done. ")
    s.feed("")  # consume it
    remaining = s.flush()
    assert remaining is None


def test_short_fragments_ignored():
    s = SentenceSplitter()
    results = s.feed("Hi. ")  # too short (<=3 chars)
    assert len(results) == 0
