"""Story mode definitions and prompt helpers."""

from __future__ import annotations

ADVANCE_MARKER = "[SCENE_ADVANCE]"


STORIES: dict[str, dict] = {
    "airport_rebook": {
        "id": "airport_rebook",
        "title": "Missed Flight Rebooking",
        "title_zh": "机场误机改签危机",
        "cover_emoji": "✈️",
        "difficulty": "intermediate",
        "synopsis": "Negotiate with airline staff after missing a flight.",
        "synopsis_zh": "你错过航班，需要解释情况、改签并确认行李安排。",
        "character": {
            "name": "Morgan",
            "role": "Airline service agent",
            "personality": "Calm, procedural, helpful when the traveler is specific.",
        },
        "scenes": [
            {
                "id": "counter",
                "setup": "You arrive at the airline counter after missing your flight by 15 minutes.",
                "setup_zh": "你晚到 15 分钟，航班已经关闭登机口。",
                "goal": "Explain what happened and ask what options are available.",
                "ai_opening": "Good afternoon. I can help you here. What seems to be the problem with your booking?",
            },
            {
                "id": "rebook",
                "setup": "The next direct flight is expensive, but there is a cheaper connecting flight.",
                "setup_zh": "下一班直飞很贵，但有一班更便宜的中转航班。",
                "goal": "Compare the options and politely negotiate the fee.",
                "ai_opening": "I found two options: a direct flight tonight with a change fee, or a cheaper connecting flight tomorrow morning.",
            },
            {
                "id": "baggage",
                "setup": "Your checked baggage may already be in the airport system.",
                "setup_zh": "你的托运行李可能已经进入机场系统。",
                "goal": "Confirm where the baggage is and how to pick it up.",
                "ai_opening": "Before I finalize the rebooking, we should check your baggage status.",
            },
            {
                "id": "finalize",
                "setup": "You need a written confirmation and a boarding time.",
                "setup_zh": "你需要确认邮件、登机时间和注意事项。",
                "goal": "Confirm the itinerary and ask for final instructions.",
                "ai_opening": "Your new itinerary is almost ready. Please confirm the passenger name and email address.",
            },
        ],
    },
    "hotel_complaint": {
        "id": "hotel_complaint",
        "title": "Hotel Complaint",
        "title_zh": "酒店投诉与补偿",
        "cover_emoji": "🏨",
        "difficulty": "intermediate",
        "synopsis": "Handle a room problem without sounding rude.",
        "synopsis_zh": "房间出现问题，你需要清楚投诉、争取换房或补偿。",
        "character": {
            "name": "Avery",
            "role": "Hotel front desk manager",
            "personality": "Professional, busy, responsive to clear evidence and reasonable requests.",
        },
        "scenes": [
            {
                "id": "report",
                "setup": "Your hotel room has a loud air conditioner and weak Wi-Fi.",
                "setup_zh": "你的房间空调噪音很大，Wi-Fi 也很差。",
                "goal": "Describe both issues clearly.",
                "ai_opening": "Good evening. How can I help with your stay tonight?",
            },
            {
                "id": "evidence",
                "setup": "The manager asks for details before making a decision.",
                "setup_zh": "经理需要更多细节才能决定处理方式。",
                "goal": "Give concrete examples and explain the impact.",
                "ai_opening": "I am sorry to hear that. Could you tell me when the problems started and how they affected you?",
            },
            {
                "id": "resolution",
                "setup": "A new room may be available, but compensation is not guaranteed.",
                "setup_zh": "可能可以换房，但补偿还不能保证。",
                "goal": "Ask for a room change or a fair compensation.",
                "ai_opening": "I may be able to move you to another room. What resolution would you prefer?",
            },
            {
                "id": "close",
                "setup": "The manager offers a partial solution.",
                "setup_zh": "经理给出部分解决方案，你需要确认细节。",
                "goal": "Confirm the next steps politely.",
                "ai_opening": "We can arrange the move now and add breakfast tomorrow. Does that work for you?",
            },
        ],
    },
    "final_interview": {
        "id": "final_interview",
        "title": "Final Interview",
        "title_zh": "求职终面",
        "cover_emoji": "💼",
        "difficulty": "advanced",
        "synopsis": "Answer deeper questions from a hiring manager.",
        "synopsis_zh": "终面中，你需要讲清项目取舍、协作方式和岗位匹配度。",
        "character": {
            "name": "Jordan",
            "role": "Hiring manager",
            "personality": "Direct, thoughtful, focused on evidence and communication quality.",
        },
        "scenes": [
            {
                "id": "intro",
                "setup": "The hiring manager wants a concise self-introduction.",
                "setup_zh": "面试官希望你做一个简洁、有重点的自我介绍。",
                "goal": "Summarize your background and target role fit.",
                "ai_opening": "Thanks for joining the final interview. Please start with a brief introduction and why this role fits you.",
            },
            {
                "id": "project",
                "setup": "The interviewer asks about a project with technical tradeoffs.",
                "setup_zh": "面试官追问一个有技术取舍的项目。",
                "goal": "Explain the problem, your decision, and the result.",
                "ai_opening": "Tell me about one project where you had to make a difficult technical tradeoff.",
            },
            {
                "id": "collaboration",
                "setup": "The interviewer tests teamwork and conflict handling.",
                "setup_zh": "面试官考察你的协作和冲突处理方式。",
                "goal": "Describe a disagreement and how you handled it.",
                "ai_opening": "Can you describe a time when you disagreed with a teammate?",
            },
            {
                "id": "closing",
                "setup": "You can ask final questions and close strongly.",
                "setup_zh": "你可以提问并做最后总结。",
                "goal": "Ask one thoughtful question and summarize your value.",
                "ai_opening": "Before we wrap up, what questions do you have for me?",
            },
        ],
    },
    "mystery_clues": {
        "id": "mystery_clues",
        "title": "Mystery Clues",
        "title_zh": "悬疑找线索",
        "cover_emoji": "🕵️",
        "difficulty": "advanced",
        "synopsis": "Interview witnesses and connect clues in English.",
        "synopsis_zh": "你要通过英文提问收集证词、确认时间线并找出矛盾。",
        "character": {
            "name": "Riley",
            "role": "Nervous witness",
            "personality": "Guarded at first, more open when asked precise and respectful questions.",
        },
        "scenes": [
            {
                "id": "approach",
                "setup": "A witness saw something unusual near a closed gallery.",
                "setup_zh": "一位目击者在关闭的画廊附近看到了异常情况。",
                "goal": "Build trust and ask what they saw.",
                "ai_opening": "I do not want to get involved, but yes, I saw something near the gallery.",
            },
            {
                "id": "timeline",
                "setup": "The exact time matters.",
                "setup_zh": "准确时间非常关键。",
                "goal": "Clarify the timeline and sequence of events.",
                "ai_opening": "It happened quickly. I remember looking at my phone, but I am not sure of the exact minute.",
            },
            {
                "id": "contradiction",
                "setup": "One detail conflicts with another witness statement.",
                "setup_zh": "一个细节和另一份证词不一致。",
                "goal": "Ask about the contradiction without accusing the witness.",
                "ai_opening": "Someone else said the lights were already off. I remember seeing a light under the door.",
            },
            {
                "id": "conclusion",
                "setup": "You need to summarize the clue and decide the next step.",
                "setup_zh": "你需要总结线索并决定下一步调查方向。",
                "goal": "Restate the key clue and ask for one final detail.",
                "ai_opening": "That is all I remember, unless there is something specific you want me to think about.",
            },
        ],
    },
}


def list_stories() -> list[dict]:
    """Return lightweight story cards for the frontend."""
    return [
        {
            "id": story["id"],
            "title": story["title"],
            "title_zh": story["title_zh"],
            "cover_emoji": story["cover_emoji"],
            "difficulty": story["difficulty"],
            "synopsis": story["synopsis"],
            "synopsis_zh": story["synopsis_zh"],
            "scene_count": len(story["scenes"]),
        }
        for story in STORIES.values()
    ]


def get_story(story_id: str) -> dict | None:
    """Get a full story definition."""
    return STORIES.get(story_id)


def build_story_prompt(story_id: str, scene_index: int) -> str:
    """Build the system prompt for the current story scene."""
    story = get_story(story_id)
    if story is None:
        raise KeyError(story_id)

    scenes = story["scenes"]
    scene_index = max(0, min(scene_index, len(scenes) - 1))
    scene = scenes[scene_index]
    character = story["character"]

    return f"""You are running an English speaking practice story mode.

Role:
- Name: {character['name']}
- Role: {character['role']}
- Personality: {character['personality']}

Story: {story['title']}
Scene {scene_index + 1}/{len(scenes)}: {scene['id']}
Situation: {scene['setup']}
Learner goal: {scene['goal']}

Rules:
- Stay in character and keep replies natural, concise, and spoken-English friendly.
- Ask one follow-up question when the learner needs more support.
- Do not solve the scene for the learner.
- When the learner has substantially achieved the scene goal, end your reply with {ADVANCE_MARKER}.
- Never explain this marker or include it in the spoken content.
- After your normal reply, include grammar corrections using the existing format:
[CORRECTIONS]
original | corrected | explanation
[END]
Use NONE if there are no corrections."""


def strip_scene_advance_marker(text: str) -> tuple[str, bool]:
    """Remove story scene marker from model output and report whether it appeared."""
    advanced = ADVANCE_MARKER in text
    return text.replace(ADVANCE_MARKER, "").strip(), advanced


def next_scene_index(story_id: str, current_index: int) -> tuple[int, bool, bool]:
    """Return (next_index, advanced, completed)."""
    story = get_story(story_id)
    if story is None:
        raise KeyError(story_id)
    last_index = len(story["scenes"]) - 1
    if current_index >= last_index:
        return current_index, False, True
    next_index = current_index + 1
    return next_index, True, False
