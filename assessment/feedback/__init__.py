"""
Session storage and progress tracking.
Stores practice session data as JSON files for MVP.
Provides APIs for listing sessions, generating summaries, and progress metrics.
"""
import json
import uuid
from pathlib import Path
from datetime import date, datetime, timedelta, timezone

# Session data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "sessions"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class SessionStore:
    """File-based session storage (MVP, upgrade to SQLite for production)."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        scenario: str,
        custom_prompt: str | None = None,
        user_id: str = "default_user",
        metadata: dict | None = None,
    ) -> dict:
        """Start a new practice session.

        custom_prompt: optional full system prompt that overrides the scenario
        prompt for this session (used by /api/sessions/custom).
        metadata: optional extra fields stored on the session (e.g. partner
        info for custom_topic sessions).
        """
        session = {
            "id": uuid.uuid4().hex[:12],
            "user_id": user_id,
            "scenario": scenario,
            "custom_prompt": custom_prompt,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "ended_at": None,
            "turns": [],
            "scores": {
                "pronunciation": [],
                "fluency": [],
                "accuracy": [],
            },
            "corrections_count": 0,
        }
        if metadata:
            session.update(metadata)
        self._save(session)
        return session

    def add_turn(
        self,
        session_id: str,
        user_text: str,
        reply_text: str,
        corrections: list[dict],
        pronunciation: dict | None = None,
    ) -> dict:
        """Record a conversation turn with optional scoring."""
        session = self._load(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        turn = {
            "index": len(session["turns"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_text": user_text,
            "reply_text": reply_text,
            "corrections": corrections,
            "pronunciation": pronunciation,
        }
        session["turns"].append(turn)
        session["corrections_count"] += len(corrections)

        if pronunciation:
            session["scores"]["pronunciation"].append(
                pronunciation.get("pronunciation_score", 0)
            )
            session["scores"]["fluency"].append(
                pronunciation.get("fluency_score", 0)
            )
            session["scores"]["accuracy"].append(
                pronunciation.get("accuracy_score", 0)
            )

        self._save(session)
        return turn

    def end_session(self, session_id: str) -> dict:
        """Mark session as ended and generate summary."""
        session = self._load(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        session["ended_at"] = datetime.now(timezone.utc).isoformat()
        self._save(session)
        return self.get_summary(session_id)

    def get_session(self, session_id: str) -> dict | None:
        return self._load(session_id)

    def update_session_fields(self, session_id: str, **fields) -> dict:
        """Update selected top-level session fields and persist them."""
        session = self._load(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.update(fields)
        self._save(session)
        return session

    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: str | None = None,
    ) -> list[dict]:
        """List sessions sorted by most recent first."""
        sessions = []
        for f in sorted(self.data_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if user_id is not None and data.get("user_id", "default_user") != user_id:
                    continue
                sessions.append(self._to_summary_item(data))
            except (json.JSONDecodeError, KeyError):
                continue

        return sessions[offset: offset + limit]

    def get_summary(self, session_id: str) -> dict:
        """Generate a detailed session summary."""
        session = self._load(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        scores = session["scores"]
        n_turns = len(session["turns"])

        return {
            "session_id": session["id"],
            "scenario": session["scenario"],
            "started_at": session["started_at"],
            "ended_at": session["ended_at"],
            "total_turns": n_turns,
            "total_corrections": session["corrections_count"],
            "avg_pronunciation": _avg(scores["pronunciation"]),
            "avg_fluency": _avg(scores["fluency"]),
            "avg_accuracy": _avg(scores["accuracy"]),
            "score_trend": {
                "pronunciation": scores["pronunciation"],
                "fluency": scores["fluency"],
                "accuracy": scores["accuracy"],
            },
            "common_errors": self._extract_common_errors(session),
        }

    def get_progress(self, user_id: str | None = None) -> dict:
        """Aggregate progress metrics across all sessions."""
        all_sessions = []
        for f in sorted(self.data_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if user_id is not None and data.get("user_id", "default_user") != user_id:
                    continue
                all_sessions.append(data)
            except (json.JSONDecodeError, KeyError):
                continue

        if not all_sessions:
            return {
                "total_sessions": 0,
                "total_turns": 0,
                "total_corrections": 0,
                "avg_pronunciation": None,
                "avg_fluency": None,
                "avg_accuracy": None,
                "sessions_over_time": [],
                "score_history": [],
                "streak": {
                    "current": 0,
                    "longest": 0,
                    "active_dates": [],
                    "daily_counts": {},
                },
                "weakness": {
                    "common_grammar_errors": [],
                    "weak_scenarios": [],
                    "low_dimension": None,
                },
                "scenario_distribution": {},
                "daily_plan": {
                    "focus": "baseline",
                    "recommended_scenario": None,
                    "target_turns": 3,
                    "target_minutes": 10,
                    "tasks": [
                        "Complete one short conversation",
                        "Record one pronunciation practice sentence",
                        "Review your first correction",
                    ],
                },
            }

        total_turns = sum(len(s["turns"]) for s in all_sessions)
        total_corrections = sum(s["corrections_count"] for s in all_sessions)

        all_pron = [sc for s in all_sessions for sc in s["scores"]["pronunciation"]]
        all_flu = [sc for s in all_sessions for sc in s["scores"]["fluency"]]
        all_acc = [sc for s in all_sessions for sc in s["scores"]["accuracy"]]

        # Per-session averages for charting
        score_history = []
        for s in all_sessions:
            score_history.append({
                "session_id": s["id"],
                "date": s["started_at"][:10],
                "scenario": s["scenario"],
                "avg_pronunciation": _avg(s["scores"]["pronunciation"]),
                "avg_fluency": _avg(s["scores"]["fluency"]),
                "avg_accuracy": _avg(s["scores"]["accuracy"]),
                "turns": len(s["turns"]),
            })

        streak = _build_streak(all_sessions)
        weakness = _build_weakness(all_sessions, all_pron, all_flu, all_acc)
        scenario_distribution = _scenario_distribution(all_sessions)

        return {
            "total_sessions": len(all_sessions),
            "total_turns": total_turns,
            "total_corrections": total_corrections,
            "avg_pronunciation": _avg(all_pron),
            "avg_fluency": _avg(all_flu),
            "avg_accuracy": _avg(all_acc),
            "score_history": score_history,
            "streak": streak,
            "weakness": weakness,
            "scenario_distribution": scenario_distribution,
            "daily_plan": _build_daily_plan(streak, weakness),
        }

    def _extract_common_errors(self, session: dict) -> list[dict]:
        """Find most frequent correction patterns in a session."""
        error_map: dict[str, int] = {}
        for turn in session["turns"]:
            for c in turn.get("corrections", []):
                key = c.get("explanation", "")[:50]
                error_map[key] = error_map.get(key, 0) + 1

        sorted_errors = sorted(error_map.items(), key=lambda x: -x[1])
        return [{"pattern": k, "count": v} for k, v in sorted_errors[:5]]

    def _to_summary_item(self, session: dict) -> dict:
        scores = session["scores"]
        return {
            "session_id": session["id"],
            "user_id": session.get("user_id", "default_user"),
            "scenario": session["scenario"],
            "started_at": session["started_at"],
            "turns": len(session["turns"]),
            "avg_pronunciation": _avg(scores["pronunciation"]),
            "avg_fluency": _avg(scores["fluency"]),
        }

    def _save(self, session: dict):
        path = self.data_dir / f"{session['id']}.json"
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self, session_id: str) -> dict | None:
        # Sanitize session_id to prevent path traversal
        if not session_id or "/" in session_id or "\\" in session_id or ".." in session_id:
            return None
        path = self.data_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def _build_streak(sessions: list[dict]) -> dict:
    daily_counts: dict[str, int] = {}
    for session in sessions:
        day = session.get("started_at", "")[:10]
        if not day:
            continue
        daily_counts[day] = daily_counts.get(day, 0) + 1

    active_dates = sorted(daily_counts)
    active_set = set(active_dates)
    if not active_dates:
        return {"current": 0, "longest": 0, "active_dates": [], "daily_counts": {}}

    anchor = min(date.today(), date.fromisoformat(active_dates[-1]))
    current = 0
    cursor = anchor
    while cursor.isoformat() in active_set:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    run = 0
    prev_day = None
    for day_str in active_dates:
        day = date.fromisoformat(day_str)
        if prev_day is not None and day == prev_day + timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
        prev_day = day

    return {
        "current": current,
        "longest": longest,
        "active_dates": active_dates,
        "daily_counts": daily_counts,
    }


def _build_weakness(
    sessions: list[dict],
    all_pron: list[float],
    all_flu: list[float],
    all_acc: list[float],
) -> dict:
    grammar_counts: dict[str, int] = {}
    scenario_scores: dict[str, list[float]] = {}
    scenario_sessions: dict[str, int] = {}

    for session in sessions:
        scenario = session.get("scenario", "unknown")
        scenario_sessions[scenario] = scenario_sessions.get(scenario, 0) + 1
        scores = session.get("scores", {})
        combined_scores = [
            score
            for dimension in ("pronunciation", "fluency", "accuracy")
            for score in scores.get(dimension, [])
            if isinstance(score, (int, float))
        ]
        if combined_scores:
            scenario_scores.setdefault(scenario, []).extend(combined_scores)

        for turn in session.get("turns", []):
            for correction in turn.get("corrections", []):
                pattern = (correction.get("explanation") or "").strip()[:50]
                if pattern:
                    grammar_counts[pattern] = grammar_counts.get(pattern, 0) + 1

    common_grammar_errors = [
        {"pattern": pattern, "count": count}
        for pattern, count in sorted(grammar_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    ]

    weak_scenarios = [
        {
            "scenario": scenario,
            "avg_score": _avg(scores),
            "sessions": scenario_sessions.get(scenario, 0),
        }
        for scenario, scores in scenario_scores.items()
        if scores
    ]
    weak_scenarios.sort(key=lambda item: (item["avg_score"], -item["sessions"], item["scenario"]))

    dimensions = {
        "pronunciation": _avg(all_pron),
        "fluency": _avg(all_flu),
        "accuracy": _avg(all_acc),
    }
    available_dimensions = {key: value for key, value in dimensions.items() if value is not None}
    low_dimension = min(available_dimensions, key=available_dimensions.get) if available_dimensions else None

    return {
        "common_grammar_errors": common_grammar_errors,
        "weak_scenarios": weak_scenarios[:3],
        "low_dimension": low_dimension,
    }


def _scenario_distribution(sessions: list[dict]) -> dict:
    distribution: dict[str, int] = {}
    for session in sessions:
        scenario = session.get("scenario", "unknown")
        distribution[scenario] = distribution.get(scenario, 0) + 1
    return distribution


def _build_daily_plan(streak: dict, weakness: dict) -> dict:
    low_dimension = weakness.get("low_dimension") or "pronunciation"
    weak_scenarios = weakness.get("weak_scenarios") or []
    recommended_scenario = weak_scenarios[0]["scenario"] if weak_scenarios else None

    dimension_task = {
        "pronunciation": "Repeat 5 low-score words slowly, then read one full sentence",
        "fluency": "Answer one question twice: first clearly, then more smoothly",
        "accuracy": "Review one grammar correction and reuse the corrected phrase",
    }.get(low_dimension, "Complete one focused speaking drill")

    scenario_task = (
        f"Practice the {recommended_scenario} scenario for at least 3 turns"
        if recommended_scenario
        else "Try one new scenario for at least 3 turns"
    )

    streak_task = (
        "Keep your streak alive with a 10-minute session today"
        if streak.get("current", 0) > 0
        else "Start today's streak with one short conversation"
    )

    return {
        "focus": low_dimension,
        "recommended_scenario": recommended_scenario,
        "target_turns": 5 if streak.get("current", 0) >= 3 else 3,
        "target_minutes": 15 if streak.get("current", 0) >= 3 else 10,
        "tasks": [scenario_task, dimension_task, streak_task],
    }


# Global store instance
store = SessionStore()
