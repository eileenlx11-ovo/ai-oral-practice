"""
Session storage and progress tracking.
Stores practice session data as JSON files for MVP.
Provides APIs for listing sessions, generating summaries, and progress metrics.
"""
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Session data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "sessions"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class SessionStore:
    """File-based session storage (MVP, upgrade to SQLite for production)."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, scenario: str, custom_prompt: str | None = None) -> dict:
        """Start a new practice session.

        custom_prompt: optional full system prompt that overrides the scenario
        prompt for this session (used by /api/sessions/custom).
        """
        session = {
            "id": uuid.uuid4().hex[:12],
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

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """List sessions sorted by most recent first."""
        sessions = []
        for f in sorted(self.data_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
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

    def get_progress(self) -> dict:
        """Aggregate progress metrics across all sessions."""
        all_sessions = []
        for f in sorted(self.data_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
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

        return {
            "total_sessions": len(all_sessions),
            "total_turns": total_turns,
            "total_corrections": total_corrections,
            "avg_pronunciation": _avg(all_pron),
            "avg_fluency": _avg(all_flu),
            "avg_accuracy": _avg(all_acc),
            "score_history": score_history,
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
        path = self.data_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 1)


# Global store instance
store = SessionStore()
