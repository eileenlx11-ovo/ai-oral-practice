"""
Learning analytics module.
Loads session JSON files and computes vocabulary trends, pronunciation curves,
error distributions, scenario coverage, and practice duration metrics.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Session data directory (same as feedback store)
DATA_DIR = Path(__file__).parent / "data" / "sessions"


def _load_sessions(days: int) -> list[dict]:
    """Load session files within the specified day range."""
    if not DATA_DIR.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days > 0 else None
    sessions = []

    for f in DATA_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        started_at = data.get("started_at")
        if not started_at:
            continue

        # Parse session start time
        try:
            session_time = datetime.fromisoformat(started_at)
        except (ValueError, TypeError):
            continue

        if cutoff and session_time < cutoff:
            continue

        sessions.append(data)

    return sessions


def _extract_words(text: str) -> list[str]:
    """Extract lowercase words from text using regex."""
    return re.findall(r"[a-z']+", text.lower())


def _get_week_key(iso_str: str) -> str:
    """Get ISO week key (YYYY-WNN) from an ISO datetime string."""
    try:
        dt = datetime.fromisoformat(iso_str)
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week:02d}"
    except (ValueError, TypeError):
        return "unknown"


def _get_date_key(iso_str: str) -> str:
    """Get date key (YYYY-MM-DD) from an ISO datetime string."""
    try:
        return iso_str[:10]
    except (TypeError, IndexError):
        return "unknown"


def _categorize_correction(explanation: str) -> str:
    """Categorize a correction by its explanation keywords."""
    text = explanation.lower()
    if "tense" in text:
        return "grammar_tense"
    if "article" in text:
        return "grammar_articles"
    if "preposition" in text:
        return "grammar_prepositions"
    if "word" in text or "vocabulary" in text:
        return "vocabulary"
    if "pronunciation" in text:
        return "pronunciation"
    return "other"


def get_analytics(days: int = 30) -> dict:
    """
    Compute learning analytics over the specified number of days.

    Returns dict with:
      - vocabulary_trend: weekly cumulative unique word count
      - pronunciation_curve: daily average pronunciation scores
      - error_distribution: corrections categorized by type
      - scenario_coverage: session count per scenario
      - practice_duration: daily estimated minutes (turns * 0.5)
      - summary: {total_sessions, total_words_spoken, unique_words}
    """
    sessions = _load_sessions(days)

    # --- Vocabulary Trend (weekly cumulative unique words) ---
    weekly_words: dict[str, set] = defaultdict(set)
    all_words: list[str] = []
    unique_words_set: set = set()

    for session in sessions:
        week_key = _get_week_key(session.get("started_at", ""))
        for turn in session.get("turns", []):
            user_text = turn.get("user_text", "")
            words = _extract_words(user_text)
            all_words.extend(words)
            unique_words_set.update(words)
            weekly_words[week_key].update(words)

    # Build cumulative unique word count per week
    sorted_weeks = sorted(weekly_words.keys())
    cumulative_words: set = set()
    vocabulary_trend: list[dict] = []
    for week in sorted_weeks:
        cumulative_words.update(weekly_words[week])
        vocabulary_trend.append({
            "week": week,
            "unique_words": len(cumulative_words),
        })

    # --- Pronunciation Curve (daily average) ---
    daily_scores: dict[str, list[float]] = defaultdict(list)

    for session in sessions:
        date_key = _get_date_key(session.get("started_at", ""))
        for score in session.get("scores", {}).get("pronunciation", []):
            if score and score > 0:
                daily_scores[date_key].append(score)

    sorted_dates = sorted(daily_scores.keys())
    pronunciation_curve: list[dict] = []
    for date in sorted_dates:
        scores = daily_scores[date]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        pronunciation_curve.append({
            "date": date,
            "avg_score": avg,
        })

    # --- Error Distribution ---
    error_counts: dict[str, int] = defaultdict(int)

    for session in sessions:
        for turn in session.get("turns", []):
            for correction in turn.get("corrections", []):
                explanation = correction.get("explanation", "")
                category = _categorize_correction(explanation)
                error_counts[category] += 1

    error_distribution: dict[str, int] = dict(error_counts)

    # --- Scenario Coverage ---
    scenario_counts: dict[str, int] = defaultdict(int)

    for session in sessions:
        scenario = session.get("scenario", "unknown")
        scenario_counts[scenario] += 1

    scenario_coverage: dict[str, int] = dict(scenario_counts)

    # --- Practice Duration (daily estimated minutes: turns * 0.5) ---
    daily_turns: dict[str, int] = defaultdict(int)

    for session in sessions:
        date_key = _get_date_key(session.get("started_at", ""))
        daily_turns[date_key] += len(session.get("turns", []))

    sorted_duration_dates = sorted(daily_turns.keys())
    practice_duration: list[dict] = []
    for date in sorted_duration_dates:
        minutes = round(daily_turns[date] * 0.5, 1)
        practice_duration.append({
            "date": date,
            "minutes": minutes,
        })

    # --- Summary ---
    summary = {
        "total_sessions": len(sessions),
        "total_words_spoken": len(all_words),
        "unique_words": len(unique_words_set),
    }

    return {
        "vocabulary_trend": vocabulary_trend,
        "pronunciation_curve": pronunciation_curve,
        "error_distribution": error_distribution,
        "scenario_coverage": scenario_coverage,
        "practice_duration": practice_duration,
        "summary": summary,
    }
