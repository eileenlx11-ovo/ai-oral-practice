"""
Scenario definitions and system prompts for each practice context.
Expanded with categories, difficulty levels, objectives, and character integration.
"""
from ..characters import get_character, CHARACTERS

# Scenario categories
CATEGORIES = [
    {"id": "all", "name": "All", "icon": "🌟"},
    {"id": "daily", "name": "Daily Life", "icon": "🏠"},
    {"id": "work", "name": "Work", "icon": "💼"},
    {"id": "travel", "name": "Travel", "icon": "✈️"},
    {"id": "social", "name": "Social", "icon": "💬"},
]

SCENARIOS = [
    # --- Daily Life ---
    {
        "id": "coffee_shop",
        "name": "Coffee Shop",
        "icon": "☕",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Order your favorite drink at a cozy café",
        "objective": "Successfully order a customized coffee drink",
        "greeting": "Hey there! Welcome to Bean & Brew. What can I get started for you today?",
    },
    {
        "id": "grocery",
        "name": "Grocery Shopping",
        "icon": "🛒",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Navigate the supermarket and find what you need",
        "objective": "Ask for help finding items and check out",
        "greeting": "Hi! Can I help you find something today? We just rearranged a few aisles.",
    },
    {
        "id": "doctor",
        "name": "Doctor's Visit",
        "icon": "🏥",
        "category": "daily",
        "difficulty": "intermediate",
        "description": "Describe symptoms and understand medical advice",
        "objective": "Explain your symptoms and understand the treatment plan",
        "greeting": "Good morning! I'm Dr. Chen. What brings you in today? How have you been feeling?",
    },
    {
        "id": "restaurant",
        "name": "Restaurant",
        "icon": "🍽️",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Order food, ask about the menu, handle the bill",
        "objective": "Order a complete meal including drinks and dessert",
        "greeting": "Good evening! Welcome to The Garden Bistro. Table for one? Here's our menu — can I start you off with something to drink?",
    },
    {
        "id": "delivery",
        "name": "Food Delivery",
        "icon": "🚴",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Handle a phone call with your delivery driver",
        "objective": "Give clear directions and resolve a delivery issue",
        "greeting": "Hey, this is Alex with your delivery. I'm at your building but I can't find the entrance. Can you help me out?",
    },
    # --- Work ---
    {
        "id": "interview",
        "name": "Job Interview",
        "icon": "💼",
        "category": "work",
        "difficulty": "advanced",
        "description": "Ace behavioral and technical interview questions",
        "objective": "Present yourself professionally and answer questions confidently",
        "greeting": "Hello! I'm Sarah from the People team. Thanks for coming in today. Let's start with — could you walk me through your background?",
    },
    {
        "id": "meeting",
        "name": "Team Meeting",
        "icon": "📋",
        "category": "work",
        "difficulty": "intermediate",
        "description": "Share updates and discuss project decisions",
        "objective": "Present your status update and respond to questions",
        "greeting": "Alright everyone, let's get started. We've got a few items on the agenda. Would you like to kick us off with your update?",
    },
    {
        "id": "coworker",
        "name": "Office Chat",
        "icon": "👩‍💻",
        "category": "work",
        "difficulty": "intermediate",
        "description": "Casual conversation with a colleague",
        "objective": "Build rapport and discuss work-life topics naturally",
        "greeting": "Hey! Finally grabbed lunch? Mind if I join? I've been stuck in back-to-back meetings all morning...",
    },
    {
        "id": "phone_call",
        "name": "Business Call",
        "icon": "📞",
        "category": "work",
        "difficulty": "advanced",
        "description": "Handle a professional phone conversation with a client",
        "objective": "Communicate clearly and confirm action items",
        "greeting": "Hi, this is Michael from Apex Solutions. Thanks for taking my call. I wanted to follow up on the proposal we sent last week — have you had a chance to review it?",
    },
    {
        "id": "salary",
        "name": "Salary Negotiation",
        "icon": "💰",
        "category": "work",
        "difficulty": "advanced",
        "description": "Discuss compensation and negotiate your offer",
        "objective": "Express your expectations and reach a fair agreement",
        "greeting": "Great news — we'd like to extend an offer! The base salary we're proposing is $85,000. I'd love to walk you through the full package. What questions do you have?",
    },
    # --- Travel ---
    {
        "id": "airport",
        "name": "Airport Check-in",
        "icon": "✈️",
        "category": "travel",
        "difficulty": "intermediate",
        "description": "Check in for your flight and handle luggage",
        "objective": "Complete check-in and resolve a seat/baggage issue",
        "greeting": "Good morning! Passport and booking reference, please. Are you checking any bags today?",
    },
    {
        "id": "hotel",
        "name": "Hotel Check-in",
        "icon": "🏨",
        "category": "travel",
        "difficulty": "beginner",
        "description": "Check into your hotel and ask about amenities",
        "objective": "Complete check-in and get local recommendations",
        "greeting": "Welcome to The Grand! Do you have a reservation with us? May I have your name, please?",
    },
    {
        "id": "directions",
        "name": "Asking Directions",
        "icon": "🗺️",
        "category": "travel",
        "difficulty": "beginner",
        "description": "Ask a local for directions to your destination",
        "objective": "Get clear directions and confirm you understood",
        "greeting": "Oh, you look a bit lost! Can I help you find somewhere? This area can be a bit confusing.",
    },
    {
        "id": "travel",
        "name": "Car Rental",
        "icon": "🚗",
        "category": "travel",
        "difficulty": "intermediate",
        "description": "Rent a car and understand the terms",
        "objective": "Choose the right car and understand insurance options",
        "greeting": "Welcome to QuickDrive Rentals! I see you have a reservation. Let me pull that up — what name is it under?",
    },
    # --- Social ---
    {
        "id": "smalltalk",
        "name": "Small Talk",
        "icon": "💬",
        "category": "social",
        "difficulty": "beginner",
        "description": "Practice casual everyday conversation",
        "objective": "Keep a natural conversation going for 5+ exchanges",
        "greeting": "Hey! Nice to see you around. How's your week been going?",
    },
    {
        "id": "party",
        "name": "Party Chat",
        "icon": "🎉",
        "category": "social",
        "difficulty": "intermediate",
        "description": "Meet new people and make conversation at a party",
        "objective": "Introduce yourself and find common interests",
        "greeting": "Hi! I don't think we've met — I'm Olivia, a friend of Sam's. How do you know the host?",
    },
    {
        "id": "neighbor",
        "name": "Neighbor Chat",
        "icon": "🏠",
        "category": "social",
        "difficulty": "beginner",
        "description": "Chat with your neighbor about everyday things",
        "objective": "Have a friendly exchange about the neighborhood",
        "greeting": "Oh hello! I've been meaning to say hi — I noticed you moved in recently. How are you settling in?",
    },
    {
        "id": "gym",
        "name": "Gym Buddy",
        "icon": "💪",
        "category": "social",
        "difficulty": "intermediate",
        "description": "Chat with someone at the gym about fitness",
        "objective": "Discuss workout routines and give/receive tips",
        "greeting": "Hey man! I've seen you here a few times. You're pretty consistent! How long have you been working out?",
    },
]

# Base instruction for the LLM acting as conversation partner
_BASE_INSTRUCTION = """You are an English-speaking practice partner. Your role:
1. Respond naturally to the user in the given scenario context.
2. Keep responses concise (2-4 sentences) to encourage more user speaking.
3. After your natural reply, analyze the user's message for grammar/expression errors.
4. After corrections, provide a brief encouraging feedback line.

CRITICAL: You MUST use this EXACT format. Never mix corrections into the reply.

[REPLY]
Your natural conversational reply here. Nothing else.
[CORRECTIONS]
- "original phrase" → "corrected phrase" | explanation
[FEEDBACK]
emoji + one short encouraging or coaching sentence
[END]

If there are no errors:
[REPLY]
Your reply here.
[CORRECTIONS]
NONE
[FEEDBACK]
emoji + one short encouraging sentence
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

Rules for feedback:
- Keep it to ONE short sentence (under 15 words)
- Be specific: mention what the user did well or what to try next
- Examples: "🎯 Great use of past tense!" / "💡 Try using 'would like' instead of 'want' for politeness"
- Vary between praise and gentle coaching
"""

_SCENARIO_CONTEXTS = {
    "coffee_shop": "You are Maya, a cheerful barista at Bean & Brew café. Help the customer order, suggest drinks, ask about size/milk preference. Be chatty and friendly. Use coffee terminology naturally (latte, espresso shot, oat milk, etc).",
    "grocery": "You are Tom, a helpful grocery store clerk. Help the customer find items, suggest alternatives if something is out of stock. Be patient and give clear directions within the store.",
    "doctor": "You are Dr. Chen, a general practitioner. Ask about symptoms, duration, and severity. Explain possible causes in simple terms. Suggest treatment options. Be professional and reassuring.",
    "restaurant": "You are James, a server at The Garden Bistro. Present specials, explain dishes, take orders, check on dietary restrictions. Be polite and attentive. Handle the full dining experience from drinks to dessert.",
    "delivery": "You are Alex, a food delivery driver calling the customer. You're at their building but need help finding the entrance. Be quick and friendly. Ask for clear directions or landmarks.",
    "interview": "You are Sarah, an HR Manager at a tech company. Conduct a professional interview: ask behavioral questions (tell me about a time...), follow up on answers, assess communication skills. Be warm but evaluative.",
    "meeting": "You are David, a project manager. Run a team meeting: ask for updates, discuss blockers, make decisions. Be organized and collaborative. Respond to proposals constructively.",
    "coworker": "You are Lisa, a colleague on the same tech team. Chat casually about work, weekend plans, office gossip, or shared interests. Be friendly and relatable. Mix work talk with personal chat.",
    "phone_call": "You are Michael, a client on a business call. Discuss project deliverables, timelines, or concerns. Be professional and direct. Expect clear answers and confirm action items.",
    "salary": "You are Rachel, a hiring manager discussing compensation. Present an offer, explain benefits, and be open to negotiation. Be firm but fair. Use HR terminology around total compensation.",
    "airport": "You are Emily, airport check-in staff. Process the passenger's check-in, handle baggage, assign seats. Deal with any issues (overweight bag, seat preference) efficiently and helpfully.",
    "hotel": "You are Carlos, a hotel front desk receptionist. Check the guest in, explain amenities (breakfast, wifi, pool), offer room upgrades, give local recommendations. Be welcoming and informative.",
    "directions": "You are Sophie, a friendly local. Give directions using landmarks, distances, and street names. Offer alternative routes. Check if the person understood. Be warm and patient.",
    "travel": "You are Mark, a car rental agent. Help the customer choose a vehicle, explain insurance options, go through the rental agreement. Be informative and suggest value-adds without being pushy.",
    "smalltalk": "You are Jake, a friendly acquaintance. Have casual conversation about weather, hobbies, weekend plans, food, movies, or current events. Be warm, ask follow-up questions, and share your own stories.",
    "party": "You are Olivia, someone the user just met at a party. Be outgoing and curious. Ask about their job, hobbies, how they know the host. Share your own stories. Use casual language and some slang.",
    "neighbor": "You are Robert, the user's next-door neighbor. Chat about the neighborhood, local events, weather, home stuff. Be friendly and community-minded. Occasionally mention neighborhood happenings.",
    "gym": "You are Kevin, a gym regular. Talk about workouts, routines, fitness goals, nutrition. Be motivating and share tips. Use fitness terminology naturally. Be casual and encouraging.",
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
    """Build full system prompt for a scenario, including character context."""
    context = _SCENARIO_CONTEXTS.get(scenario_id, _SCENARIO_CONTEXTS["smalltalk"])
    character = get_character(scenario_id)

    # Add character personality to context
    char_info = f"\nYour name is {character['name']}. Personality: {character['personality']}. Speaking style: {character['speaking_style']}."

    return f"{_BASE_INSTRUCTION}\n\nSCENARIO CONTEXT:\n{context}{char_info}"


def get_voice_for_scenario(scenario_id: str) -> str:
    """Get the appropriate TTS voice ID for a scenario's character."""
    character = get_character(scenario_id)
    voice_key = character.get("voice", "american_female")
    return VOICES.get(voice_key, VOICES["american_female"])["id"]


# Per-field cap to keep the system prompt within a sane token budget.
_CUSTOM_FIELD_CAP = 2000


def build_custom_interview_prompt(
    jd_text: str = "",
    resume_text: str = "",
    project_context: str = "",
) -> str:
    """Build an interviewer system prompt customized to a specific role/candidate.

    Any field may be empty; only provided sections are injected. Intended to be
    fed externally (e.g. by talent-agent) via POST /api/sessions/custom.
    """
    parts = [
        "You are a professional interviewer at a tech company conducting a "
        "job interview in English."
    ]
    if jd_text.strip():
        parts.append(f"JOB DESCRIPTION the candidate is applying for:\n{jd_text.strip()[:_CUSTOM_FIELD_CAP]}")
    if resume_text.strip():
        parts.append(f"CANDIDATE BACKGROUND:\n{resume_text.strip()[:_CUSTOM_FIELD_CAP]}")
    if project_context.strip():
        parts.append(
            "CANDIDATE'S PROJECT (ask technical follow-ups about this):\n"
            f"{project_context.strip()[:_CUSTOM_FIELD_CAP]}"
        )
    parts.append(
        "Ask focused, progressively deeper questions that probe whether the "
        "candidate fits THIS role and can substantiate THEIR claimed experience. "
        "One question at a time. Be professional but friendly."
    )
    context = "\n\n".join(parts)
    return f"{_BASE_INSTRUCTION}\n\nSCENARIO CONTEXT:\n{context}"



# Practice sentences for pronunciation assessment (per scenario)
PRACTICE_SENTENCES = {
    "coffee_shop": [
        "I'd like a medium latte with oat milk, please.",
        "Could I also get a blueberry muffin to go?",
        "Do you have any seasonal specials today?",
        "Can I pay with my phone?",
    ],
    "grocery": [
        "Excuse me, where can I find the pasta sauce?",
        "Do you have any organic vegetables in stock?",
        "I'd like half a pound of sliced turkey, please.",
        "Is this item on sale this week?",
    ],
    "doctor": [
        "I've been having a headache for about three days now.",
        "The pain gets worse in the morning and evening.",
        "I'm not currently taking any medication.",
        "Should I schedule a follow-up appointment?",
    ],
    "restaurant": [
        "I'd like to start with the soup of the day, please.",
        "Could you tell me what the chef recommends?",
        "I have a nut allergy. Is this dish safe for me?",
        "Could we get the check when you have a moment?",
    ],
    "delivery": [
        "I'm in the building on the left side of the street.",
        "You need to enter the code one two three four at the gate.",
        "I'll come downstairs to meet you at the entrance.",
        "The apartment number is three zero five on the third floor.",
    ],
    "interview": [
        "I have three years of experience in software development.",
        "My biggest strength is my ability to learn quickly.",
        "I led a team of five engineers on that project.",
        "I'm looking for a role where I can grow technically.",
    ],
    "meeting": [
        "I'd like to share a quick update on our progress.",
        "We're currently on track to meet the deadline.",
        "I think we should consider an alternative approach.",
        "Let me summarize the action items from today.",
    ],
    "coworker": [
        "Hey, do you want to grab coffee after this meeting?",
        "I'm thinking about taking a vacation next month.",
        "Have you tried the new restaurant down the street?",
        "The deadline got pushed back to next Friday.",
    ],
    "phone_call": [
        "Thank you for taking the time to speak with me today.",
        "I'd like to discuss the timeline for the next deliverable.",
        "Could you send me that in writing after our call?",
        "Let me confirm the next steps before we hang up.",
    ],
    "salary": [
        "I appreciate the offer and I'm very excited about the role.",
        "Based on my research, I was hoping for something closer to ninety thousand.",
        "Could you tell me more about the equity package?",
        "I'd like a few days to review the complete offer.",
    ],
    "airport": [
        "I'd like a window seat if one is available, please.",
        "I have one checked bag and one carry-on.",
        "What time does boarding start for my flight?",
        "Is there a lounge I can access with this ticket?",
    ],
    "hotel": [
        "I have a reservation under the name Johnson for three nights.",
        "Is breakfast included with my room?",
        "Could you recommend a good restaurant nearby?",
        "What time is checkout tomorrow morning?",
    ],
    "directions": [
        "Excuse me, could you tell me how to get to the museum?",
        "Is it within walking distance from here?",
        "Should I take the first or second left turn?",
        "Thank you so much for your help. I appreciate it.",
    ],
    "travel": [
        "I'd like to rent a mid-size sedan for five days.",
        "Does the insurance cover damage to the windshield?",
        "What's your policy on returning the car with a full tank?",
        "Can I drop off the car at a different location?",
    ],
    "smalltalk": [
        "I've been really into cooking lately. It's so relaxing.",
        "The weather has been great this week, hasn't it?",
        "I just started watching a new show on Netflix.",
        "Do you have any plans for the weekend?",
    ],
    "party": [
        "It's nice to meet you! I'm a friend of a friend.",
        "So what do you do for work? That sounds really interesting.",
        "Have you been to one of these parties before?",
        "We should definitely exchange numbers and hang out sometime.",
    ],
    "neighbor": [
        "Hi there! The neighborhood seems really nice and quiet.",
        "Do you know if there's a good coffee shop nearby?",
        "I noticed there's a park down the street. Is it nice?",
        "Thanks for the tip! I'll definitely check it out.",
    ],
    "gym": [
        "I usually work out about four times a week.",
        "I've been focusing on building upper body strength.",
        "Do you have any tips for improving my deadlift form?",
        "I try to get at least eight hours of sleep for recovery.",
    ],
}


def get_practice_sentences(scenario_id: str) -> list[str]:
    """Get pronunciation practice sentences for a scenario."""
    return PRACTICE_SENTENCES.get(scenario_id, PRACTICE_SENTENCES["smalltalk"])
