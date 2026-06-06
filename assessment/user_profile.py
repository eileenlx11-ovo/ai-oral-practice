"""
User profile management.
Stores user preferences, level assessment results, and conversation memories.
File-based JSON storage (MVP).
"""
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent / "data" / "profiles"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_DIR = Path(__file__).parent / "data" / "user_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# Default user ID for single-user MVP (no auth yet)
DEFAULT_USER_ID = "default_user"


class UserProfileStore:
    """Manages user profiles and conversation memory."""

    def __init__(self, data_dir: Path = DATA_DIR, memory_dir: Path = MEMORY_DIR):
        self.data_dir = data_dir
        self.memory_dir = memory_dir

    def get_or_create(self, user_id: str = DEFAULT_USER_ID) -> dict:
        """Get existing profile or create a new one."""
        profile = self._load_profile(user_id)
        if profile is None:
            profile = {
                "id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "level": None,
                "level_assessed_at": None,
                "scores": None,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "total_sessions": 0,
                "total_turns": 0,
                "preferred_scenarios": [],
                "character_affinity": {},  # scenario_id -> turn_count
            }
            self._save_profile(profile)
        return profile

    def update_level(self, user_id: str, assessment: dict) -> dict:
        """Update user's level assessment results."""
        profile = self.get_or_create(user_id)
        profile["level"] = assessment.get("level")
        profile["level_assessed_at"] = datetime.now(timezone.utc).isoformat()
        profile["scores"] = assessment.get("scores")
        profile["strengths"] = assessment.get("strengths", [])
        profile["weaknesses"] = assessment.get("weaknesses", [])
        profile["recommendations"] = assessment.get("recommendations", [])
        self._save_profile(profile)
        return profile

    def increment_affinity(self, user_id: str, scenario_id: str, turns: int = 1) -> int:
        """Increase affinity (turn count) with a character. Returns new total."""
        profile = self.get_or_create(user_id)
        current = profile["character_affinity"].get(scenario_id, 0)
        profile["character_affinity"][scenario_id] = current + turns
        profile["total_turns"] += turns
        self._save_profile(profile)
        return profile["character_affinity"][scenario_id]

    def get_affinity_level(self, user_id: str, scenario_id: str) -> int:
        """
        Get affinity level for a character (1-3).
        Level 1: 0-5 turns (formal, guided)
        Level 2: 6-20 turns (natural, some humor)
        Level 3: 21+ turns (friend-like, remembers things)
        """
        profile = self.get_or_create(user_id)
        turns = profile["character_affinity"].get(scenario_id, 0)
        if turns >= 21:
            return 3
        elif turns >= 6:
            return 2
        return 1

    # --- Conversation Memory ---

    def get_memory(self, user_id: str, scenario_id: str) -> list[str]:
        """Get stored conversation memories for a user-character pair."""
        memory_file = self.memory_dir / f"{user_id}_{scenario_id}.json"
        if not memory_file.exists():
            return []
        try:
            data = json.loads(memory_file.read_text(encoding="utf-8"))
            return data.get("memories", [])
        except (json.JSONDecodeError, KeyError):
            return []

    def add_memory(self, user_id: str, scenario_id: str, memory: str):
        """Add a conversation memory (extracted key fact about the user)."""
        memory_file = self.memory_dir / f"{user_id}_{scenario_id}.json"
        data = {"memories": []}
        if memory_file.exists():
            try:
                data = json.loads(memory_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass

        memories = data.get("memories", [])
        # Keep max 10 memories per character
        if memory not in memories:
            memories.append(memory)
            if len(memories) > 10:
                memories = memories[-10:]

        data["memories"] = memories
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        memory_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Private helpers ---

    def _load_profile(self, user_id: str) -> dict | None:
        path = self.data_dir / f"{user_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _save_profile(self, profile: dict):
        path = self.data_dir / f"{profile['id']}.json"
        path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


# Global instance
profile_store = UserProfileStore()
