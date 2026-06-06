"""
Hint system — generates suggested responses when users get stuck.
Provides 2-3 contextual response options based on conversation history.
"""

HINT_PROMPT = """Based on the conversation below, suggest 2-3 short responses the learner could say next.
Each suggestion should be natural, contextually appropriate, and at the learner's level.

Rules:
- Keep each suggestion to 1-2 sentences
- Vary difficulty: one simple, one slightly more complex
- Make them feel natural, not textbook-perfect
- Include a brief Chinese hint for what each one means
- Format as JSON array

Output format (strict JSON, no markdown):
[
  {"text": "English response option", "hint": "中文提示", "difficulty": "easy"},
  {"text": "English response option", "hint": "中文提示", "difficulty": "medium"},
  {"text": "English response option", "hint": "中文提示", "difficulty": "hard"}
]

Conversation so far:
"""


def build_hint_messages(scenario_id: str, history: list[dict]) -> list[dict]:
    """Build messages for the hint generation request."""
    from .scenarios import get_system_prompt

    # Use last 6 turns for context
    recent = history[-6:] if len(history) > 6 else history

    conversation_text = ""
    for msg in recent:
        role_label = "AI" if msg["role"] == "assistant" else "Learner"
        conversation_text += f"{role_label}: {msg['content']}\n"

    return [
        {"role": "system", "content": HINT_PROMPT + conversation_text},
        {"role": "user", "content": "Generate hint suggestions now."},
    ]
