"""
Level assessment — evaluates user's English speaking level through a short test.
Outputs a CEFR-aligned level (A1-C1) and identifies strengths/weaknesses.
"""
import json
from datetime import datetime, timezone

LEVEL_TEST_QUESTIONS = [
    {
        "index": 0,
        "difficulty": "A1",
        "prompt": "Let's start easy. Can you introduce yourself? Tell me your name, where you're from, and what you do.",
        "evaluates": ["basic_vocabulary", "sentence_structure"],
    },
    {
        "index": 1,
        "difficulty": "A2",
        "prompt": "What did you do last weekend? Tell me about it in a few sentences.",
        "evaluates": ["past_tense", "narrative"],
    },
    {
        "index": 2,
        "difficulty": "B1",
        "prompt": "If you could live anywhere in the world, where would you choose and why?",
        "evaluates": ["conditional", "reasoning", "vocabulary_range"],
    },
    {
        "index": 3,
        "difficulty": "B2",
        "prompt": "Some people say AI will replace most jobs in the future. What's your opinion on this?",
        "evaluates": ["opinion_expression", "complex_grammar", "discourse"],
    },
    {
        "index": 4,
        "difficulty": "C1",
        "prompt": "Describe a significant challenge you overcame and what it taught you about yourself.",
        "evaluates": ["advanced_vocabulary", "narrative_complexity", "abstract_thinking"],
    },
]

ASSESSMENT_PROMPT = """You are an English language assessor. Evaluate the learner's spoken responses (transcribed by ASR).

For each response, assess:
1. Grammar complexity and accuracy (1-10)
2. Vocabulary range and appropriateness (1-10)
3. Fluency and coherence (1-10)
4. Task completion (did they address the prompt?) (1-10)

Consider that this is SPOKEN English transcribed by ASR, so:
- Ignore capitalization and punctuation issues
- Don't penalize natural speech hesitations
- Focus on actual language ability, not transcription quality

After evaluating all responses, determine the overall CEFR level:
- A1: Can produce simple phrases about personal details
- A2: Can describe routine matters and immediate needs
- B1: Can deal with most situations, produce connected text on familiar topics
- B2: Can interact with fluency, produce detailed text on wide range of subjects
- C1: Can express ideas fluently, use language flexibly for social/professional purposes

Output strict JSON (no markdown):
{
  "level": "B1",
  "scores": {
    "grammar": 6,
    "vocabulary": 7,
    "fluency": 5,
    "task_completion": 7
  },
  "strengths": ["vocabulary range", "task completion"],
  "weaknesses": ["grammar accuracy", "fluency"],
  "summary": "One sentence overall assessment in Chinese",
  "recommendations": ["specific suggestion 1", "specific suggestion 2"]
}
"""


def build_assessment_messages(responses: list[dict]) -> list[dict]:
    """Build messages for the level assessment LLM call."""
    content = "Here are the learner's responses to progressively harder prompts:\n\n"

    for resp in responses:
        q = LEVEL_TEST_QUESTIONS[resp["index"]]
        content += f"Question ({q['difficulty']}): {q['prompt']}\n"
        content += f"Response: {resp['text']}\n\n"

    return [
        {"role": "system", "content": ASSESSMENT_PROMPT},
        {"role": "user", "content": content},
    ]
