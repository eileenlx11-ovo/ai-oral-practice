"""
Parse LLM response to separate reply text from grammar corrections and feedback.
Expected LLM format:
  [REPLY]
  ...natural reply...
  [CORRECTIONS]
  - "original" → "corrected" | explanation
  [FEEDBACK]
  emoji + one short sentence
  [END]
"""
import re

_REPLY_PATTERN = re.compile(
    r"\[REPLY\]\s*(.*?)\s*\[CORRECTIONS\]", re.DOTALL
)
_CORRECTION_PATTERN = re.compile(
    r'-\s*"([^"]+)"\s*→\s*"([^"]+)"\s*\|\s*(.+)'
)
_FEEDBACK_PATTERN = re.compile(
    r"\[FEEDBACK\]\s*(.*?)\s*(?:\[END\]|$)", re.DOTALL
)


def extract_corrections(raw: str) -> tuple[str, list[dict]]:
    """
    Parse structured LLM output into reply + corrections list.
    Falls back gracefully if LLM doesn't follow format exactly.
    """
    # Try structured parse
    reply_match = _REPLY_PATTERN.search(raw)
    if reply_match:
        reply_text = reply_match.group(1).strip()
    else:
        # Fallback: use everything before [CORRECTIONS] or the whole thing
        parts = raw.split("[CORRECTIONS]")
        reply_text = parts[0].replace("[REPLY]", "").strip()

    # Extract corrections
    corrections = []
    correction_section = ""
    if "[CORRECTIONS]" in raw:
        correction_section = raw.split("[CORRECTIONS]", 1)[1]
        # Stop at [FEEDBACK] or [END]
        correction_section = correction_section.split("[FEEDBACK]")[0]
        correction_section = correction_section.split("[END]")[0]

    if "NONE" not in correction_section.upper():
        for match in _CORRECTION_PATTERN.finditer(correction_section):
            corrections.append({
                "original": match.group(1),
                "corrected": match.group(2),
                "explanation": match.group(3).strip(),
            })

    # Final fallback: if reply is empty, use raw (LLM didn't follow format)
    if not reply_text:
        reply_text = raw.split("[")[0].strip() or raw.strip()

    return reply_text, corrections


def extract_feedback(raw: str) -> str | None:
    """Extract the [FEEDBACK] section from LLM output."""
    match = _FEEDBACK_PATTERN.search(raw)
    if match:
        feedback = match.group(1).strip()
        if feedback and feedback.upper() != "NONE":
            return feedback
    return None
