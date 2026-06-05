"""
Scenario definitions and system prompts for each practice context.
"""

SCENARIOS = [
    {
        "id": "interview",
        "name": "Job Interview",
        "icon": "💼",
        "description": "Practice self-introduction and answering interview questions",
        "greeting": "Hello! I'm your interviewer today. Let's start with a brief self-introduction. Could you tell me about yourself?",
    },
    {
        "id": "restaurant",
        "name": "Restaurant",
        "icon": "🍽️",
        "description": "Practice ordering food and restaurant conversations",
        "greeting": "Welcome! I'll be your server today. Would you like to see the menu, or do you already know what you'd like to order?",
    },
    {
        "id": "meeting",
        "name": "Business Meeting",
        "icon": "📋",
        "description": "Practice expressing opinions and discussing in meetings",
        "greeting": "Good morning everyone. Let's get started with today's meeting. Would you like to share your update first?",
    },
    {
        "id": "travel",
        "name": "Travel",
        "icon": "✈️",
        "description": "Practice asking for directions, booking hotels, buying tickets",
        "greeting": "Hi there! Welcome to the information desk. How can I help you today? Are you looking for directions, or do you need help with booking?",
    },
    {
        "id": "smalltalk",
        "name": "Small Talk",
        "icon": "💬",
        "description": "Practice natural social English conversation",
        "greeting": "Hey! Nice to meet you. How's your day going so far?",
    },
]

# Base instruction for the LLM acting as conversation partner
_BASE_INSTRUCTION = """You are an English-speaking practice partner. Your role:
1. Respond naturally to the user in the given scenario context.
2. Keep responses concise (2-4 sentences) to encourage more user speaking.
3. After your natural reply, analyze the user's message for grammar/expression errors.

CRITICAL: You MUST use this EXACT format. Never mix corrections into the reply.

[REPLY]
Your natural conversational reply here. Nothing else.
[CORRECTIONS]
- "original phrase" → "corrected phrase" | explanation
[END]

If there are no errors:
[REPLY]
Your reply here.
[CORRECTIONS]
NONE
[END]

Rules for corrections:
- The input is SPOKEN English transcribed by ASR. The ASR may produce errors (e.g. "dog with" instead of "I got", "Sas" instead of "SaaS"). Use context to infer what the user likely said.
- Do NOT flag:
  - Capitalization issues (speech has no caps)
  - Punctuation issues (ASR adds punctuation imperfectly)
  - Minor filler words (um, uh, like)
  - Words that are clearly ASR mishearing (not the user's fault)
- DO flag: wrong verb tense, wrong preposition, wrong word form, missing articles, word order errors, wrong collocations
- Keep explanations brief (under 12 words)
- Maximum 3 corrections per turn (most important ones only)
- NEVER put corrections, explanations, or "|" characters inside the [REPLY] section
"""

_SCENARIO_CONTEXTS = {
    "interview": "You are a professional interviewer at a tech company. Ask follow-up questions about the candidate's experience, skills, and motivation. Be professional but friendly.",
    "restaurant": "You are a friendly restaurant server. Help the customer with the menu, make recommendations, and handle their order. Be polite and attentive.",
    "meeting": "You are a colleague in a business meeting. Discuss project updates, ask clarifying questions, and respond to proposals. Be professional and collaborative.",
    "travel": "You are a helpful information desk attendant at an airport/hotel. Help the traveler with directions, bookings, or general travel questions. Be patient and clear.",
    "smalltalk": "You are a friendly acquaintance having casual conversation. Topics can include weather, hobbies, weekend plans, food, or current events. Be warm and engaging.",
}

# Available TTS voices (edge-tts neural voices)
VOICES = {
    "american_female": {"id": "en-US-JennyNeural", "label": "American Female (Jenny)"},
    "american_male": {"id": "en-US-GuyNeural", "label": "American Male (Guy)"},
    "british_female": {"id": "en-GB-SoniaNeural", "label": "British Female (Sonia)"},
    "british_male": {"id": "en-GB-RyanNeural", "label": "British Male (Ryan)"},
    "indian_female": {"id": "en-IN-NeerjaNeural", "label": "Indian Female (Neerja)"},
    "indian_male": {"id": "en-IN-PrabhatNeural", "label": "Indian Male (Prabhat)"},
    "australian_female": {"id": "en-AU-NatashaNeural", "label": "Australian Female (Natasha)"},
}


def get_system_prompt(scenario_id: str) -> str:
    context = _SCENARIO_CONTEXTS.get(scenario_id, _SCENARIO_CONTEXTS["smalltalk"])
    return f"{_BASE_INSTRUCTION}\n\nSCENARIO CONTEXT:\n{context}"
