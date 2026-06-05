"""
Parse LLM response to separate reply text from grammar corrections.
Expected LLM format:
  [REPLY]
  ...natural reply...
  [CORRECTIONS]
  - "original" → "corrected" | explanation
  [END]
"""
import re

_REPLY_PATTERN = re.compile(
    r"\[REPLY\]\s*(.*?)\s*\[CORRECTIONS\]", re.DOTALL
)
_CORRECTION_PATTERN = re.compile(
    r'-\s*"([^"]+)"\s*→\s*"([^"]+)"\s*\|\s*(.+)'
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
