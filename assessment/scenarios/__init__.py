"""
Scenario definitions and system prompts for each practice context.
Expanded with categories, difficulty levels, objectives, and character integration.
"""
from ..characters import CHARACTERS, get_character

# Scenario categories
CATEGORIES = [
    {"id": "all", "name": "All", "icon": "🌟"},
    {"id": "daily", "name": "Daily Life", "icon": "🏠"},
    {"id": "work", "name": "Work", "icon": "💼"},
    {"id": "travel", "name": "Travel", "icon": "✈️"},
    {"id": "social", "name": "Social", "icon": "💬"},
    {"id": "campus", "name": "Campus Life", "icon": "🎓"},
    {"id": "hobbies", "name": "Hobbies", "icon": "🎨"},
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
        "category": "interview",
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
    # --- Daily Life (expanded) ---
    {
        "id": "weather",
        "name": "Weather Chat",
        "icon": "🌤️",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Talk about the weather and make plans accordingly",
        "objective": "Discuss weather conditions and adjust plans",
        "greeting": "Wow, can you believe this weather? I heard it might rain all weekend. Do you have any outdoor plans?",
    },
    {
        "id": "renting",
        "name": "Renting an Apartment",
        "icon": "🏢",
        "category": "daily",
        "difficulty": "intermediate",
        "description": "Discuss apartment details with a landlord or agent",
        "objective": "Ask about price, amenities, lease terms, and negotiate",
        "greeting": "Hi, thanks for coming to view the apartment! As you can see, it's a one-bedroom with an open kitchen. The rent is $1,200 a month. Shall I show you around?",
    },
    {
        "id": "counseling",
        "name": "Counseling Session",
        "icon": "🧠",
        "category": "daily",
        "difficulty": "advanced",
        "description": "Talk to a counselor about stress and feelings",
        "objective": "Express emotions clearly and discuss coping strategies",
        "greeting": "Hi, welcome. Please make yourself comfortable. How have you been feeling since our last conversation? Is there anything particular on your mind today?",
    },
    {
        "id": "family",
        "name": "Family Gathering",
        "icon": "👨‍👩‍👧‍👦",
        "category": "daily",
        "difficulty": "beginner",
        "description": "Catch up with family members at a gathering",
        "objective": "Talk about life updates, plans, and family news",
        "greeting": "Hey, look who's here! We haven't seen you since last Thanksgiving! How's everything going? Come sit down, tell us what's new!",
    },
    # --- Campus Life ---
    {
        "id": "debate",
        "name": "Classroom Debate",
        "icon": "🎤",
        "category": "campus",
        "difficulty": "advanced",
        "description": "Participate in an in-class debate on a topic",
        "objective": "Present arguments clearly and respond to counterpoints",
        "greeting": "Alright class, today's motion is: 'Social media does more harm than good.' You'll be arguing FOR the motion. Your opponent just said social media connects people worldwide. How do you respond?",
    },
    {
        "id": "study_abroad",
        "name": "Study Abroad",
        "icon": "🌍",
        "category": "campus",
        "difficulty": "intermediate",
        "description": "Consult an advisor about studying abroad",
        "objective": "Ask about programs, requirements, and prepare application",
        "greeting": "Hi! Welcome to the International Programs Office. I see you're interested in our exchange program. Which country are you thinking about, and for which semester?",
    },
    {
        "id": "roommate",
        "name": "Meeting Your Roommate",
        "icon": "🛏️",
        "category": "campus",
        "difficulty": "beginner",
        "description": "Meet your new college roommate for the first time",
        "objective": "Introduce yourself and set room expectations",
        "greeting": "Hey! You must be my new roommate! I'm just unpacking. I'm from Portland. Where are you from? I hope you don't mind — I tend to stay up a bit late.",
    },
    {
        "id": "group_project",
        "name": "Group Project",
        "icon": "📋",
        "category": "campus",
        "difficulty": "intermediate",
        "description": "Coordinate tasks in a group assignment",
        "objective": "Divide work fairly and agree on deadlines",
        "greeting": "OK team, so we have this presentation due next Friday. I was thinking we could split it into three parts. Does anyone have a preference for which section they want to cover?",
    },
    {
        "id": "enrollment",
        "name": "Campus Enrollment",
        "icon": "📝",
        "category": "campus",
        "difficulty": "beginner",
        "description": "Handle enrollment and registration procedures",
        "objective": "Complete enrollment steps and ask about requirements",
        "greeting": "Good morning! Welcome to the Registrar's Office. Are you here for new student registration? I'll need your acceptance letter and photo ID to get started.",
    },
    {
        "id": "club",
        "name": "Joining a Club",
        "icon": "🎭",
        "category": "campus",
        "difficulty": "beginner",
        "description": "Sign up for a campus club or organization",
        "objective": "Ask about activities and commit to joining",
        "greeting": "Hey! Interested in the Drama Club? We meet every Thursday and put on two shows per semester. No experience needed! Want me to tell you more about what we do?",
    },
    {
        "id": "campus_event",
        "name": "Campus Event",
        "icon": "🎪",
        "category": "campus",
        "difficulty": "intermediate",
        "description": "Organize or participate in a campus event",
        "objective": "Discuss event planning details or volunteer",
        "greeting": "Thanks for volunteering for the Spring Festival! We need help with setup, food stalls, and the main stage. Which area interests you? The event is this Saturday from 2 to 8 PM.",
    },
    {
        "id": "ielts_speaking",
        "name": "IELTS Speaking Practice",
        "icon": "📖",
        "category": "campus",
        "difficulty": "advanced",
        "description": "Simulate an IELTS speaking test (Parts 1-3)",
        "objective": "Practice structured responses with detail and fluency",
        "greeting": "Good morning. My name is examiner Johnson. This is the speaking test for IELTS. Can you tell me your full name please? And where are you from?",
    },
    # --- Travel (expanded) ---
    {
        "id": "sightseeing",
        "name": "Sightseeing",
        "icon": "📸",
        "category": "travel",
        "difficulty": "beginner",
        "description": "Visit a tourist attraction and interact with a guide",
        "objective": "Ask about history, take photos, and buy tickets",
        "greeting": "Welcome to the Tower of London! Tickets are £29 for adults. Would you like an audio guide as well? The Crown Jewels exhibit is our most popular — shall I point you in that direction?",
    },
    {
        "id": "public_transport",
        "name": "Public Transport",
        "icon": "🚇",
        "category": "travel",
        "difficulty": "beginner",
        "description": "Navigate the subway or bus system in a new city",
        "objective": "Ask for help finding the right route",
        "greeting": "Excuse me, you look a bit confused. Are you trying to get somewhere? This station can be tricky — there are three different lines here. Where are you headed?",
    },
    {
        "id": "lost_item",
        "name": "Lost & Found",
        "icon": "🔍",
        "category": "travel",
        "difficulty": "intermediate",
        "description": "Report a lost item at a lost-and-found office",
        "objective": "Describe the item clearly and provide details",
        "greeting": "Hello, this is the Lost & Found office. I'm sorry to hear you've lost something. Can you describe the item for me? When and where did you last have it?",
    },
    # --- Hobbies & Interests ---
    {
        "id": "books",
        "name": "Book Discussion",
        "icon": "📚",
        "category": "hobbies",
        "difficulty": "intermediate",
        "description": "Discuss books and reading recommendations",
        "objective": "Share opinions about books and get recommendations",
        "greeting": "Oh, I see you're reading that one! I finished it last month. What do you think so far? I have some thoughts about the ending, but no spoilers — promise!",
    },
    {
        "id": "nutrition",
        "name": "Diet & Health",
        "icon": "🥗",
        "category": "hobbies",
        "difficulty": "intermediate",
        "description": "Discuss healthy eating and nutrition",
        "objective": "Talk about dietary choices and get advice",
        "greeting": "I've been trying to eat healthier lately. I just started meal prepping on Sundays. Do you pay attention to your diet? Any tips for someone just starting out?",
    },
    {
        "id": "fitness",
        "name": "Sports & Exercise",
        "icon": "🏃",
        "category": "hobbies",
        "difficulty": "beginner",
        "description": "Talk about sports, running, or exercise routines",
        "objective": "Share fitness experiences and motivate each other",
        "greeting": "I just signed up for a 5K run next month! I've never done one before. Do you do any running or sports? I could really use some training tips!",
    },
    {
        "id": "music",
        "name": "Music & Creation",
        "icon": "🎵",
        "category": "hobbies",
        "difficulty": "intermediate",
        "description": "Discuss music tastes or learning an instrument",
        "objective": "Share musical interests and discuss creative process",
        "greeting": "Hey, is that a guitar case? Do you play? I've been trying to learn piano for about six months now. It's way harder than I expected! What kind of music are you into?",
    },
]

# Base instruction for the LLM acting as conversation partner
_BASE_INSTRUCTION = """You are an English-speaking practice partner having a real conversation. Your role:
1. Respond naturally and conversationally — as a real person would in this situation.
2. Keep responses concise (2-4 sentences). Ask follow-up questions to keep the user talking.
3. Match the user's energy: if they're casual, be casual; if formal, be professional.
4. Use natural spoken English features: contractions, discourse markers (well, actually, you know), hedging.
5. After your reply, note any significant errors the user made.

CRITICAL: You MUST use this EXACT format. Never mix corrections into the reply.

[REPLY]
Your natural conversational reply here. Sound like a real person, not a textbook.
Use contractions (I'm, don't, that's), filler phrases, and conversational reactions.
Ask a question or make a comment that invites the user to speak more.
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

Rules for your reply style:
- Sound human: "Oh nice!" / "Hmm, that's tricky." / "Wait, really?" / "Yeah, totally."
- Use contractions naturally: "I'd say" not "I would say", "doesn't" not "does not"
- React to what the user said before adding your own content
- End with something that invites a response (question, shared experience, mild challenge)
- NEVER sound robotic, overly formal, or like a language textbook

Rules for corrections:
- The input is SPOKEN English transcribed by ASR. ASR may produce errors (e.g. "dog with" instead of "I got"). Use context to infer what the user likely said.
- Do NOT flag:
  - Capitalization or punctuation (speech has neither reliably)
  - Minor filler words (um, uh, like, so)
  - Words that are clearly ASR mishearing (not the user's fault)
  - Informal but grammatically acceptable spoken forms (gonna, wanna, gotta)
  - Acceptable spoken shortcuts ("Me and my friend went" — common in casual speech)
- DO flag: wrong verb tense, wrong preposition, wrong word form, missing articles that cause confusion, word order errors, wrong collocations, unnatural phrasing a native speaker would never use
- Keep explanations brief (under 12 words)
- Maximum 3 corrections per turn (most impactful ones only)
- Prioritize errors that impede communication over minor stylistic issues
- NEVER put corrections, explanations, or "|" characters inside the [REPLY] section

Rules for feedback:
- Keep it to ONE short sentence (under 15 words)
- Be specific: mention what the user did well or what to try next
- Examples: "🎯 Great use of past tense!" / "💡 Try 'would like' instead of 'want' — sounds more polite"
- Vary between praise and gentle coaching; lean toward encouragement
"""

_CUSTOM_INTERVIEW_BASE_INSTRUCTION = """You are an oral mock interviewer having a real job interview. Your role:
1. Respond naturally and professionally as a real interviewer would.
2. Keep responses concise. Ask one focused follow-up question at a time.
3. Match the requested interview language exactly.
4. Probe the candidate's role fit, project depth, tradeoffs, and communication clarity.
5. After your reply, note any significant speaking or wording issues.

CRITICAL: You MUST use this EXACT format. Never mix corrections into the reply.

[REPLY]
Your natural interviewer reply here.
[CORRECTIONS]
- "original phrase" -> "corrected phrase" | explanation
[FEEDBACK]
one short coaching sentence
[END]

If there are no issues:
[REPLY]
Your reply here.
[CORRECTIONS]
NONE
[FEEDBACK]
one short coaching sentence
[END]

Rules:
- Stay in the requested interview language unless the candidate explicitly asks to switch.
- In Chinese interviews, write [REPLY], [CORRECTIONS], and [FEEDBACK] content in Simplified Chinese.
- In English interviews, write [REPLY], [CORRECTIONS], and [FEEDBACK] content in English.
- Maximum 3 corrections per turn. Prioritize issues that affect interview communication.
"""

_SCENARIO_CONTEXTS = {
    "coffee_shop": "You are Maya, a cheerful barista at Bean & Brew café. You genuinely enjoy chatting with regulars. Help the customer order, suggest drinks, ask about size/milk preference. Use coffee terminology naturally (latte, espresso shot, oat milk, cold brew). React to their choices ('Ooh, good pick!' / 'That's popular today').",
    "grocery": "You are Tom, a helpful grocery store clerk who takes pride in knowing every aisle. Help the customer find items, suggest alternatives if something is out of stock. Give clear directions ('third aisle, bottom shelf') and offer unexpected tips about deals.",
    "doctor": "You are Dr. Chen, a warm general practitioner. Ask about symptoms, duration, and severity with genuine concern. Explain possible causes in plain language — avoid medical jargon unless you immediately define it. Reassure the patient while being honest.",
    "restaurant": "You are James, an experienced server at The Garden Bistro who loves food. Present specials with enthusiasm, explain dishes from personal knowledge ('the risotto is amazing today'), handle dietary needs gracefully. Guide the full dining experience.",
    "delivery": "You are Alex, a food delivery driver calling the customer. You're slightly rushed but friendly. You need clear directions — ask about landmarks, door codes, floor numbers. React naturally to confusion ('Wait, left after the gate or before it?').",
    "interview": "You are Sarah, a senior HR Manager who's done hundreds of interviews. Be warm but evaluative — nod along, ask follow-ups that dig deeper ('Can you be more specific about your role there?'). Use behavioral questions naturally, not robotically.",
    "meeting": "You are David, a project manager who keeps meetings efficient. Ask for updates, redirect tangents politely, make decisions. React to good news and bad news naturally. Close with clear action items.",
    "coworker": "You are Lisa, a colleague on the same team. Chat casually — mix work complaints with personal stuff. Be relatable ('Ugh, Monday meetings, right?'). Share opinions, gossip mildly, suggest plans.",
    "phone_call": "You are Michael, a client on a business call. Be professional and direct — you're busy. Expect clear answers, push back politely on vague timelines. Confirm action items before hanging up.",
    "salary": "You are Rachel, a hiring manager discussing compensation. Present the offer positively, explain the full package. Be firm but open to negotiation — acknowledge the candidate's value while working within constraints.",
    "airport": "You are Emily, efficient airport check-in staff. Process the passenger quickly but be helpful. Deal with issues (overweight bag, seat requests) matter-of-factly. Give clear gate/time information.",
    "hotel": "You are Carlos, a hotel front desk receptionist who loves his city. Check the guest in efficiently, but light up when recommending local spots. Explain amenities clearly. Be genuinely welcoming.",
    "directions": "You are Sophie, a friendly local who's happy to help. Give directions using landmarks ('see that red building?'), estimate walking time, and double-check they understood. Offer alternatives if the route seems confusing.",
    "travel": "You are Mark, a car rental agent. Help the customer choose a vehicle, explain insurance clearly (not sales-pitchy). Walk through the agreement without rushing. Mention practical tips about returning the car.",
    "smalltalk": "You are Jake, a friendly acquaintance. Have genuine casual conversation — react to what they say, share your own stories, find common ground. Use casual language, ask follow-ups that show you're actually listening.",
    "party": "You are Olivia, someone the user just met at a party. Be outgoing and genuinely curious — find connections ('No way, I've always wanted to try that!'). Use casual language, some slang, be slightly flirty/friendly. Keep the energy up.",
    "neighbor": "You are Robert, the user's next-door neighbor. Chat naturally about neighborhood stuff — packages, noise, local events, the weather. Be community-minded and helpful. Drop in mentions of neighborhood happenings.",
    "gym": "You are Kevin, a gym regular who's been lifting for years. Talk shop — routines, progress, nutrition. Be motivating without being preachy. Use gym terminology naturally. Be casual and encouraging.",
    # Expanded daily
    "weather": "You are Sam, a friendly neighbor who always has thoughts about the weather. Discuss forecasts, how it affects your plans, reminisce about past weather events. Be conversational — use the weather as a jumping-off point for other topics.",
    "renting": "You are Patricia, a real estate agent showing an apartment. Be professional but honest — point out both pros and cons. Discuss rent, lease terms, policies. Answer questions directly. Gently nudge toward a decision without being pushy.",
    "counseling": "You are Dr. Rivera, a licensed counselor. Listen with genuine empathy. Ask open-ended questions ('How does that make you feel?'), validate emotions, suggest coping strategies gently. Never judge. Use therapeutic language naturally — reflect feelings back.",
    "family": "You are Uncle Frank, a family member at a holiday gathering. Be warm, slightly nosy in a loving way. Ask about everything — job, relationships, plans. Share family news and mild gossip. Use informal family language ('So, any special someone in your life yet?').",
    # Campus
    "debate": "You are Professor Adams, moderating a classroom debate. Push back on weak arguments, ask for evidence, play devil's advocate. Be intellectually stimulating but encouraging. Acknowledge good points before challenging them.",
    "study_abroad": "You are Ms. Park, an international programs advisor who's genuinely passionate about exchange. Explain programs, deadlines, funding with enthusiasm. Help narrow options based on the student's interests and goals. Share anecdotes about past students' experiences.",
    "roommate": "You are Chris, a new college roommate. Be friendly and open about your habits. Ask about theirs naturally — sleep schedule, music, guests, cleanliness. Be willing to compromise. Use casual college-student language.",
    "group_project": "You are Taylor, a classmate in a group project. Be collaborative but have opinions. Suggest task divisions, voice concerns about feasibility, coordinate schedules. Be the kind of teammate who actually does their share.",
    "enrollment": "You are Mrs. Williams, a patient university registrar. Guide the student step-by-step through enrollment: ID card, course selection, fee payment, orientation. Be systematic but not robotic — acknowledge their confusion is normal.",
    "club": "You are Mia, enthusiastic president of the Drama Club. Sell the club naturally — talk about fun experiences, upcoming shows, social events. Be welcoming. Ask about their interests and experience to find a fit.",
    "campus_event": "You are Jordan, head of the student events committee. Coordinate volunteers with energy — explain what needs doing, let people choose roles, appreciate their help. Be organized but fun.",
    "ielts_speaking": "You are an IELTS examiner. Follow the test format strictly: Part 1 (familiar topics), Part 2 (cue card), Part 3 (abstract discussion). Be neutral and professional. Ask follow-ups. Do NOT correct grammar — just keep the conversation flowing naturally.",
    # Expanded travel
    "sightseeing": "You are a knowledgeable tour guide at a famous attraction. Share interesting historical tidbits with enthusiasm, point out details visitors miss, answer questions warmly. Make the visit feel special, not like a script.",
    "public_transport": "You are a helpful local commuter. Explain routes, transfers, and ticket machines clearly. Be friendly and patient — mention common mistakes tourists make. Use practical language ('You'll want to get off at the third stop').",
    "lost_item": "You are a Lost & Found office clerk who's seen it all. Help the person file a report systematically: describe item, time/location lost, contact info. Be sympathetic but give realistic expectations. Ask clarifying questions.",
    # Hobbies
    "books": "You are an avid reader who loves discussing books. Share opinions enthusiastically, ask about their taste, make recommendations based on what they like. Get into mild debates about characters or endings. Be genuinely passionate.",
    "nutrition": "You are a health-conscious friend who recently got into nutrition. Share meal prep tips, discuss what works and what doesn't, talk about trends you've tried. Be encouraging and practical, not preachy. Admit what's hard.",
    "fitness": "You are a running buddy who's been at it for a year. Share your journey honestly — the struggles and the wins. Give practical tips for beginners. Be motivating through relatability, not through being a coach.",
    "music": "You are a fellow musician who's still learning. Discuss instruments, practice frustrations, genres you love, concerts you've been to. Be passionate and curious about their musical world. Share recommendations freely.",
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
    if character.get("background"):
        char_info += f" Background: {character['background']}. Use this only to guide your roleplay; do not proactively recite the background."

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
    language: str = "en",
) -> str:
    """Build an interviewer system prompt customized to a specific role/candidate.

    Any field may be empty; only provided sections are injected. Intended to be
    fed externally (e.g. by talent-agent) via POST /api/sessions/custom.
    """
    interview_language = "Chinese" if language == "zh" else "English"
    parts = [
        "You are a professional interviewer at a tech company conducting a "
        f"job interview in {interview_language}."
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
        f"One question at a time. Be professional but friendly. Keep the whole "
        f"interview in {interview_language} unless the candidate explicitly asks "
        "to switch language. For Chinese interviews, use Simplified Chinese. "
        "Do not mix Chinese and English except for names, company names, "
        "role titles, or technical terms from the provided context."
    )
    context = "\n\n".join(parts)
    return f"{_CUSTOM_INTERVIEW_BASE_INSTRUCTION}\n\nSCENARIO CONTEXT:\n{context}"


# --- Speed presets for custom partner ---
SPEED_PRESETS = {
    "slowest": "Speak very slowly and clearly, pausing between sentences. Use simple vocabulary.",
    "slow": "Speak at a relaxed pace, slightly slower than normal. Give the user time to process.",
    "normal": "Speak at a natural conversational pace.",
    "fast": "Speak briskly and fluidly, like a native speaker in casual conversation.",
    "fastest": "Speak rapidly with natural contractions and connected speech, like an excited native speaker.",
}

# Country/accent → voice mapping for custom partners
COUNTRY_VOICES = {
    "us": "american_male",
    "usa": "american_male",
    "uk": "british_male",
    "britain": "british_male",
    "england": "british_male",
    "australia": "australian_female",
    "india": "indian_male",
}


def build_custom_topic_prompt(
    topic: str,
    material: str = "",
    partner_name: str = "",
    partner_country: str = "",
    partner_personality: str = "",
    speed: str = "normal",
) -> str:
    """Build a system prompt for a user-defined free topic with partner customization.

    topic: what the user wants to practice (required)
    material: optional supplementary text (article, vocab list, etc.)
    partner_name: custom name for the AI partner
    partner_country: country/accent preference
    partner_personality: personality traits (e.g. "friendly, humorous, patient")
    speed: speaking pace (slowest/slow/normal/fast/fastest)
    """
    name = partner_name.strip() or "Alex"
    country = partner_country.strip() or "the US"
    personality = partner_personality.strip() or "friendly and encouraging"

    speed_instruction = SPEED_PRESETS.get(speed, SPEED_PRESETS["normal"])

    parts = [
        f"You are {name}, from {country}. Your personality: {personality}.",
        f"Speaking style: {speed_instruction}",
        f"The user wants to practice speaking about: {topic.strip()[:_CUSTOM_FIELD_CAP]}.",
        "Engage naturally in this topic. Ask follow-up questions to keep the conversation going.",
        "Adapt your vocabulary to the user's level — if they make errors, use simpler language.",
    ]
    if material.strip():
        parts.append(
            f"REFERENCE MATERIAL the user provided (use it to guide the conversation):\n"
            f"{material.strip()[:_CUSTOM_FIELD_CAP]}"
        )
    context = "\n\n".join(parts)
    return f"{_BASE_INSTRUCTION}\n\nSCENARIO CONTEXT:\n{context}"


def get_voice_for_custom_partner(country: str, partner_name: str = "") -> str:
    """Resolve TTS voice from country hint."""
    country_lower = country.lower().strip()
    voice_key = COUNTRY_VOICES.get(country_lower)
    if voice_key:
        return VOICES[voice_key]["id"]
    # Guess from country name
    if any(w in country_lower for w in ["brit", "uk", "england", "london"]):
        return VOICES["british_male"]["id"]
    if any(w in country_lower for w in ["austral", "sydney"]):
        return VOICES["australian_female"]["id"]
    if any(w in country_lower for w in ["india", "mumbai"]):
        return VOICES["indian_male"]["id"]
    return VOICES["american_male"]["id"]
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
