"""Unit tests for correction parser."""
from assessment.correction import extract_corrections


def test_structured_format():
    raw = """[REPLY]
That sounds great! Tell me more about your experience.
[CORRECTIONS]
- "I have work there" → "I have worked there" | Use present perfect for past experience
- "since 3 year" → "for 3 years" | Use 'for' with duration, plural noun
[END]"""
    reply, corrections = extract_corrections(raw)
    assert reply == "That sounds great! Tell me more about your experience."
    assert len(corrections) == 2
    assert corrections[0]["original"] == "I have work there"
    assert corrections[0]["corrected"] == "I have worked there"
    assert "present perfect" in corrections[0]["explanation"]


def test_no_corrections():
    raw = """[REPLY]
Nice! That's a great answer.
[CORRECTIONS]
NONE
[END]"""
    reply, corrections = extract_corrections(raw)
    assert reply == "Nice! That's a great answer."
    assert corrections == []


def test_fallback_unstructured():
    raw = "Sure, I'd love to help you with that. What position are you applying for?"
    reply, corrections = extract_corrections(raw)
    assert "Sure" in reply
    assert corrections == []
