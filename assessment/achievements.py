"""
Achievement and check-in system.
Tracks daily practice streaks, milestones, and unlockable badges.
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

DATA_DIR = Path(__file__).parent / "data" / "achievements"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Achievement definitions
ACHIEVEMENTS = [
    # Streak achievements
    {"id": "streak_3", "name": "Getting Started", "icon": "🔥", "description": "连续练习 3 天", "condition": "streak", "threshold": 3},
    {"id": "streak_7", "name": "One Week Strong", "icon": "💪", "description": "连续练习 7 天", "condition": "streak", "threshold": 7},
    {"id": "streak_30", "name": "Monthly Master", "icon": "🏆", "description": "连续练习 30 天", "condition": "streak", "threshold": 30},
    # Session count achievements
    {"id": "sessions_5", "name": "First Steps", "icon": "👣", "description": "完成 5 次练习", "condition": "sessions", "threshold": 5},
    {"id": "sessions_20", "name": "Regular Learner", "icon": "📚", "description": "完成 20 次练习", "condition": "sessions", "threshold": 20},
    {"id": "sessions_50", "name": "Dedicated Speaker", "icon": "🎓", "description": "完成 50 次练习", "condition": "sessions", "threshold": 50},
    # Turns achievements
    {"id": "turns_50", "name": "Chatty", "icon": "💬", "description": "累计对话 50 轮", "condition": "turns", "threshold": 50},
    {"id": "turns_200", "name": "Conversationalist", "icon": "🗣️", "description": "累计对话 200 轮", "condition": "turns", "threshold": 200},
    {"id": "turns_500", "name": "Eloquent Speaker", "icon": "🎤", "description": "累计对话 500 轮", "condition": "turns", "threshold": 500},
    # Pronunciation achievements
    {"id": "pron_80", "name": "Clear Voice", "icon": "🎯", "description": "单次发音评分达到 80+", "condition": "max_pronunciation", "threshold": 80},
    {"id": "pron_90", "name": "Native-like", "icon": "⭐", "description": "单次发音评分达到 90+", "condition": "max_pronunciation", "threshold": 90},
    # Scenario achievements
    {"id": "scenarios_5", "name": "Explorer", "icon": "🗺️", "description": "尝试 5 个不同场景", "condition": "unique_scenarios", "threshold": 5},
]


class AchievementStore:
    """File-based achievement and check-in tracking."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_file(self, user_id: str) -> Path:
        return self.data_dir / f"{user_id}.json"

    def _load(self, user_id: str) -> dict:
        path = self._get_user_file(user_id)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"user_id": user_id, "checkins": [], "unlocked": []}

    def _save(self, user_id: str, data: dict):
        path = self._get_user_file(user_id)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def record_checkin(self, user_id: str) -> dict:
        """Record a daily check-in. Idempotent per day."""
        data = self._load(user_id)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today not in data["checkins"]:
            data["checkins"].append(today)
            self._save(user_id, data)
        return {"date": today, "streak": self.get_streak(user_id)}

    def get_streak(self, user_id: str) -> int:
        """Calculate current consecutive practice days."""
        data = self._load(user_id)
        checkins = sorted(data["checkins"], reverse=True)
        if not checkins:
            return 0

        today = datetime.now(timezone.utc).date()
        streak = 0
        for i, date_str in enumerate(checkins):
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected = today - timedelta(days=i)
            if check_date == expected:
                streak += 1
            elif i == 0 and check_date == today - timedelta(days=1):
                streak += 1
                today = today - timedelta(days=1)
            else:
                break
        return streak

    def get_checkin_calendar(self, user_id: str, days: int = 90) -> list[dict]:
        """Get check-in data for the last N days (for heatmap)."""
        data = self._load(user_id)
        checkins_set = set(data["checkins"])
        today = datetime.now(timezone.utc).date()
        calendar = []
        for i in range(days):
            date = today - timedelta(days=days - 1 - i)
            date_str = date.strftime("%Y-%m-%d")
            calendar.append({"date": date_str, "checked": date_str in checkins_set})
        return calendar

    def check_achievements(self, user_id: str, stats: dict) -> list[dict]:
        """Evaluate all achievements against current stats."""
        data = self._load(user_id)
        streak = self.get_streak(user_id)
        unlocked_ids = set(data["unlocked"])
        results = []
        newly_unlocked = []

        for achievement in ACHIEVEMENTS:
            cond = achievement["condition"]
            threshold = achievement["threshold"]
            if cond == "streak":
                current = streak
            elif cond in stats:
                current = stats[cond]
            else:
                current = 0

            is_unlocked = current >= threshold
            is_new = is_unlocked and achievement["id"] not in unlocked_ids
            results.append({
                **achievement,
                "unlocked": is_unlocked,
                "progress": min(current, threshold),
                "is_new": is_new,
            })
            if is_new:
                newly_unlocked.append(achievement["id"])

        if newly_unlocked:
            data["unlocked"].extend(newly_unlocked)
            self._save(user_id, data)

        return results


# Global instance
achievement_store = AchievementStore()
