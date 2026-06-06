"""
Comprehensive oral English grading system.

5-dimension scoring (total 100 points):
- FC (Fluency & Coherence): 30 pts — LLM-judged
- LR (Lexical Resource): 25 pts — LLM-judged
- GRA (Grammatical Range & Accuracy): 25 pts — LLM-judged
- PRO (Pronunciation): 15 pts — Azure/Tencent hard metric
- PC (Pragmatic Competence): 5 pts — LLM-judged

Combines Azure pronunciation scores (hard data) with LLM analysis (soft metrics).
"""
import json
from typing import Optional

# --- Weight Configuration ---
WEIGHTS = {
    "fc": 30,
    "lr": 25,
    "gra": 25,
    "pro": 15,
    "pc": 5,
}

# --- Level Mapping Table ---
LEVEL_MAP = [
    {"min": 90, "max": 100, "level": "L5", "label_cn": "母语近似水准", "label_en": "Near-native",
     "ielts": "8.0–9.0", "toefl": "27–30"},
    {"min": 78, "max": 89, "level": "L4", "label_cn": "流利高阶", "label_en": "Proficient",
     "ielts": "7.0–7.5", "toefl": "23–26"},
    {"min": 62, "max": 77, "level": "L3", "label_cn": "达标基准线", "label_en": "Competent",
     "ielts": "6.0–6.5", "toefl": "19–22"},
    {"min": 45, "max": 61, "level": "L2", "label_cn": "基础入门", "label_en": "Basic",
     "ielts": "5.0–5.5", "toefl": "15–18"},
    {"min": 0, "max": 44, "level": "L1", "label_cn": "薄弱待强化", "label_en": "Elementary",
     "ielts": "≤4.5", "toefl": "<15"},
]

# --- Overall Comments by Level ---
COMMENTS = {
    "L5": {
        "en": "Your daily English is nearly native-level. You can chat freely with foreigners on all daily topics with natural pronunciation, diverse vocabulary and flexible grammar.",
        "cn": "口语接近母语水准，全场景日常闲聊无障碍，发音地道、词汇句式丰富，社交表达自然得体。",
    },
    "L4": {
        "en": "You communicate proficiently in daily scenarios. Minor flaws in pronunciation and grammar won't block daily interaction, you can expand conversations spontaneously.",
        "cn": "日常沟通流利自如，少量发音语法瑕疵不影响交流，可自主拓展聊天内容，独立在境外生活无压力。",
    },
    "L3": {
        "en": "You can finish basic daily communication. Restricted by limited vocabulary and simple sentence structure, you can't extend topics actively. More practice on collocations and linking words is needed.",
        "cn": "满足出境基础生活沟通，词汇和句式偏简单，无法自主延展话题，建议积累口语短语与连接词。",
    },
    "L2": {
        "en": "Basic ideas can be delivered with frequent pauses and word-searching. Many grammar & pronunciation mistakes disturb understanding, you need intensive daily imitation practice.",
        "cn": "仅能简单表达核心想法，频繁卡壳找词，大量发音语法错误干扰理解，需坚持跟读模仿日常短句。",
    },
    "L1": {
        "en": "It's tough to complete daily communication. You're advised to start with daily single phrases and standard pronunciation drills.",
        "cn": "无法顺畅完成日常对话，建议从高频生活短句、基础发音开始系统练习。",
    },
}


def _get_level_info(total_score: float) -> dict:
    """Map total score to level info."""
    for entry in LEVEL_MAP:
        if entry["min"] <= total_score <= entry["max"]:
            return entry
    return LEVEL_MAP[-1]


def _compute_pro_score(avg_pronunciation: Optional[float]) -> tuple[float, str]:
    """
    Map Azure/Tencent pronunciation score (0-100) to PRO dimension (0-15).
    Returns (score, level).
    """
    if avg_pronunciation is None:
        # No pronunciation data available — give neutral score
        return 9.0, "L3"

    # Linear mapping: 0-100 → 0-15
    raw = avg_pronunciation / 100.0 * 15.0
    raw = max(0, min(15, raw))

    # Determine level
    if raw >= 13:
        level = "L5"
    elif raw >= 10:
        level = "L4"
    elif raw >= 7:
        level = "L3"
    elif raw >= 4:
        level = "L2"
    else:
        level = "L1"

    return round(raw, 1), level


# Minimum turns required for full grading
MIN_TURNS_FOR_GRADING = 3


# --- LLM Grading Prompt ---

GRADING_PROMPT_TEMPLATE = """You are an expert English oral proficiency assessor for daily conversational English.
Evaluate the following student's spoken English from a practice session.

## Context
- Scenario: {scenario}
- Total conversation turns: {total_turns}
- Grammar corrections received: {corrections_count}

## Student's spoken utterances (all turns concatenated):
{user_texts}

## Grammar errors detected during session:
{corrections_summary}

## Scoring Instructions

Score EXACTLY these 4 dimensions. Each dimension has a maximum score and 5 levels (L5=best, L1=worst).

### 1. FC — Fluency & Coherence (max 30 points)
- L5 (25-30): Speaks fluently with minimal hesitation, extends topics naturally, uses diverse linking words (well/actually/by the way etc.)
- L4 (21-24): Generally fluent with occasional brief pauses, can add details to topics
- L3 (16-20): Completes basic responses but cannot extend topics, uses only basic connectors (and/so)
- L2 (9-15): Fragmented speech, frequent repetition, needs prompting to continue
- L1 (0-8): Cannot form coherent responses

### 2. LR — Lexical Resource (max 25 points)
- L5 (21-25): Uses idiomatic expressions, phrasal verbs, synonym substitution ≥4 per 100 words
- L4 (17-20): Adequate vocabulary with some natural expressions, minor misuse
- L3 (13-16): Basic vocabulary only, high-frequency word repetition (good/nice/very), no collocations
- L2 (7-12): Frequent word-searching, resorts to L1 translation patterns
- L1 (0-6): Only isolated words, cannot form phrases

### 3. GRA — Grammatical Range & Accuracy (max 25 points)
- L5 (21-25): Complex sentences ≥40%, error rate <3%, flexible tense switching
- L4 (17-20): Some complex sentences (25-39%), error rate 3-8%
- L3 (13-16): Mostly simple sentences, error rate 9-18%, basic tense errors
- L2 (7-12): Almost all simple sentences, error rate 19-35%, causes confusion
- L1 (0-6): Severe grammar breakdown, error rate >35%

### 4. PC — Pragmatic Competence (max 5 points)
- L5 (4-5): Perfectly appropriate register, polite forms, follows Western social conventions
- L4 (3): At most 1 pragmatic slip, generally appropriate
- L3 (2): 2-3 minor pragmatic issues, basic politeness OK
- L2 (1): Multiple pragmatic errors, sounds blunt or rude
- L1 (0): No awareness of social conventions

## Scoring Examples (for calibration)

Example A — Strong student (Coffee Shop, 6 turns):
"Hi, could I get a flat white please? Actually, make that an oat milk one. Oh and do you guys have any pastries left? I'll grab a croissant too. By the way, is it alright if I sit over by the window? Perfect, thank you so much!"
→ FC: 26 (L5), LR: 19 (L4), GRA: 20 (L4), PC: 5 (L5)

Example B — Intermediate student (Restaurant, 5 turns):
"I want... um... a hamburger. And... water please. Yes, this one. How much is it? OK thank you. Can I have... the bill?"
→ FC: 14 (L2), LR: 10 (L2), GRA: 14 (L3), PC: 3 (L4)

Example C — Beginner (Grocery Shopping, 4 turns):
"This... how much? I want buy two. Where is... milk? Thank you."
→ FC: 8 (L1), LR: 6 (L1), GRA: 7 (L2), PC: 2 (L3)

## Output Format
Return ONLY a valid JSON object (no markdown, no explanation):
{{
  "fc": {{"score": <int>, "level": "<L1-L5>", "comment": "<one sentence in Chinese>"}},
  "lr": {{"score": <int>, "level": "<L1-L5>", "comment": "<one sentence in Chinese>"}},
  "gra": {{"score": <int>, "level": "<L1-L5>", "comment": "<one sentence in Chinese>"}},
  "pc": {{"score": <int>, "level": "<L1-L5>", "comment": "<one sentence in Chinese>"}}
}}
"""


async def grade_session(session_data: dict, llm_client, llm_model: str) -> dict:
    """
    Grade a completed session using Azure hard metrics + LLM soft metrics.

    Args:
        session_data: Full session dict from SessionStore
        llm_client: AsyncOpenAI client instance
        llm_model: Model name for LLM calls

    Returns:
        Complete grading result dict
    """
    # 1. Compute PRO from Azure/Tencent hard data
    pron_scores = session_data.get("scores", {}).get("pronunciation", [])
    avg_pron = sum(pron_scores) / len(pron_scores) if pron_scores else None
    pro_score, pro_level = _compute_pro_score(avg_pron)

    # 2. Check minimum turn threshold
    turns = session_data.get("turns", [])
    user_turns = [t for t in turns if t.get("user_text")]

    if len(user_turns) < MIN_TURNS_FOR_GRADING:
        return _insufficient_result(pro_score, pro_level, len(user_turns))

    # 3. Prepare data for LLM grading
    user_texts = "\n".join(
        f"Turn {i+1}: {t['user_text']}" for i, t in enumerate(turns) if t.get("user_text")
    )

    if not user_texts.strip():
        # No user speech to grade — return minimal result
        return _empty_result(pro_score, pro_level)

    # Collect corrections summary
    all_corrections = []
    for t in turns:
        for c in t.get("corrections", []):
            all_corrections.append(f"  \"{c.get('original', '')}\" → \"{c.get('corrected', '')}\"")
    corrections_summary = "\n".join(all_corrections[:20]) if all_corrections else "None detected"

    # 3. Call LLM for FC/LR/GRA/PC
    prompt = GRADING_PROMPT_TEMPLATE.format(
        scenario=session_data.get("scenario", "general"),
        total_turns=len(turns),
        corrections_count=session_data.get("corrections_count", 0),
        user_texts=user_texts,
        corrections_summary=corrections_summary,
    )

    try:
        resp = await llm_client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        raw = resp.choices[0].message.content or ""
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        llm_scores = json.loads(raw)
    except Exception:
        # LLM unavailable — use estimation based on corrections count
        llm_scores = _estimate_scores(session_data)

    # 4. Assemble final result
    fc = llm_scores.get("fc", {"score": 16, "level": "L3", "comment": "数据不足"})
    lr = llm_scores.get("lr", {"score": 13, "level": "L3", "comment": "数据不足"})
    gra = llm_scores.get("gra", {"score": 13, "level": "L3", "comment": "数据不足"})
    pc = llm_scores.get("pc", {"score": 2, "level": "L3", "comment": "数据不足"})

    # Clamp scores to their max
    fc["score"] = max(0, min(WEIGHTS["fc"], fc["score"]))
    lr["score"] = max(0, min(WEIGHTS["lr"], lr["score"]))
    gra["score"] = max(0, min(WEIGHTS["gra"], gra["score"]))
    pc["score"] = max(0, min(WEIGHTS["pc"], pc["score"]))

    total = fc["score"] + lr["score"] + gra["score"] + pro_score + pc["score"]
    total = round(total, 1)

    level_info = _get_level_info(total)
    comments = COMMENTS.get(level_info["level"], COMMENTS["L3"])

    return {
        "total_score": total,
        "level": level_info["level"],
        "level_label_cn": level_info["label_cn"],
        "level_label_en": level_info["label_en"],
        "ielts_equiv": level_info["ielts"],
        "toefl_equiv": level_info["toefl"],
        "dimensions": {
            "fc": {"score": fc["score"], "max": 30, "level": fc["level"], "comment": fc.get("comment", "")},
            "lr": {"score": lr["score"], "max": 25, "level": lr["level"], "comment": lr.get("comment", "")},
            "gra": {"score": gra["score"], "max": 25, "level": gra["level"], "comment": gra.get("comment", "")},
            "pro": {"score": pro_score, "max": 15, "level": pro_level, "comment": _pro_comment(pro_level)},
            "pc": {"score": pc["score"], "max": 5, "level": pc["level"], "comment": pc.get("comment", "")},
        },
        "overall_comment_en": comments["en"],
        "overall_comment_cn": comments["cn"],
    }


def _empty_result(pro_score: float, pro_level: str) -> dict:
    """Return a minimal grading result when no user speech is available."""
    return {
        "total_score": pro_score,
        "level": "L1",
        "level_label_cn": "薄弱待强化",
        "level_label_en": "Elementary",
        "ielts_equiv": "≤4.5",
        "toefl_equiv": "<15",
        "dimensions": {
            "fc": {"score": 0, "max": 30, "level": "L1", "comment": "无有效发言数据"},
            "lr": {"score": 0, "max": 25, "level": "L1", "comment": "无有效发言数据"},
            "gra": {"score": 0, "max": 25, "level": "L1", "comment": "无有效发言数据"},
            "pro": {"score": pro_score, "max": 15, "level": pro_level, "comment": _pro_comment(pro_level)},
            "pc": {"score": 0, "max": 5, "level": "L1", "comment": "无有效发言数据"},
        },
        "overall_comment_en": COMMENTS["L1"]["en"],
        "overall_comment_cn": COMMENTS["L1"]["cn"],
    }


def _insufficient_result(pro_score: float, pro_level: str, turn_count: int) -> dict:
    """Return a partial result when turns are below minimum threshold."""
    return {
        "total_score": None,
        "level": None,
        "level_label_cn": "样本不足",
        "level_label_en": "Insufficient data",
        "ielts_equiv": None,
        "toefl_equiv": None,
        "insufficient": True,
        "min_turns_required": MIN_TURNS_FOR_GRADING,
        "current_turns": turn_count,
        "dimensions": {
            "fc": {"score": None, "max": 30, "level": None, "comment": f"至少需要{MIN_TURNS_FOR_GRADING}轮对话才能评估"},
            "lr": {"score": None, "max": 25, "level": None, "comment": f"至少需要{MIN_TURNS_FOR_GRADING}轮对话才能评估"},
            "gra": {"score": None, "max": 25, "level": None, "comment": f"至少需要{MIN_TURNS_FOR_GRADING}轮对话才能评估"},
            "pro": {"score": pro_score, "max": 15, "level": pro_level, "comment": _pro_comment(pro_level)},
            "pc": {"score": None, "max": 5, "level": None, "comment": f"至少需要{MIN_TURNS_FOR_GRADING}轮对话才能评估"},
        },
        "overall_comment_en": f"Please complete at least {MIN_TURNS_FOR_GRADING} conversation turns for a full assessment. Keep practicing!",
        "overall_comment_cn": f"至少完成{MIN_TURNS_FOR_GRADING}轮对话才能生成完整评估，继续加油练习吧！",
    }


def _estimate_scores(session_data: dict) -> dict:
    """Fallback estimation when LLM is unavailable."""
    turns = session_data.get("turns", [])
    n_turns = len(turns)
    corrections = session_data.get("corrections_count", 0)

    # Rough heuristic: more turns = better fluency, fewer corrections = better grammar
    fc_score = min(30, max(8, 16 + n_turns * 2 - corrections))
    gra_score = min(25, max(7, 20 - corrections * 2))
    lr_score = min(25, max(7, 13 + n_turns))
    pc_score = min(5, max(1, 3))

    return {
        "fc": {"score": fc_score, "level": _score_to_level(fc_score, 30), "comment": "LLM不可用，基于统计估算"},
        "lr": {"score": lr_score, "level": _score_to_level(lr_score, 25), "comment": "LLM不可用，基于统计估算"},
        "gra": {"score": gra_score, "level": _score_to_level(gra_score, 25), "comment": "LLM不可用，基于统计估算"},
        "pc": {"score": pc_score, "level": _score_to_level(pc_score, 5), "comment": "LLM不可用，基于统计估算"},
    }


def _score_to_level(score: float, max_score: int) -> str:
    """Convert a dimension score to L1-L5 level."""
    ratio = score / max_score
    if ratio >= 0.83:
        return "L5"
    elif ratio >= 0.67:
        return "L4"
    elif ratio >= 0.5:
        return "L3"
    elif ratio >= 0.3:
        return "L2"
    return "L1"


def _pro_comment(level: str) -> str:
    """Generate pronunciation dimension comment."""
    comments = {
        "L5": "发音贴近英美日常口语，连读自然，听音零障碍",
        "L4": "个别单词发音偏差，语调正常，轻松听懂",
        "L3": "中式发音明显，逐字读单词，但整体能辨认内容",
        "L2": "发音偏差大，部分单词需要重复确认",
        "L1": "发音严重失真，难以听懂",
    }
    return comments.get(level, comments["L3"])
