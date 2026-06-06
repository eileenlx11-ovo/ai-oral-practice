"""
Talent Agent integration client.
Connects to https://github.com/DNMCJH/talent-agent for interview preparation features.

Talent Agent provides:
- JD analysis and skill matching
- Mock interview question generation
- Interview performance debriefing

This module enables:
1. Pulling JD-tailored interview questions into our speaking practice
2. Syncing oral practice performance back to talent-agent
3. Using talent-agent's project matching to personalize interview scenarios
"""
import os
import json
import httpx
from typing import Optional


class TalentAgentClient:
    """Client for talent-agent API integration."""

    def __init__(
        self,
        base_url: str = "",
        token: str = "",
    ):
        self.base_url = base_url or os.getenv("TALENT_AGENT_URL", "http://localhost:8001")
        self.token = token or os.getenv("TALENT_AGENT_TOKEN", "")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0,
            )
        return self._client

    async def health_check(self) -> dict:
        """Check if talent-agent service is available."""
        try:
            client = await self._get_client()
            resp = await client.get("/health")
            resp.raise_for_status()
            return {"status": "connected", "data": resp.json()}
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    async def get_interview_context(self, jd_text: str, language: str = "en") -> dict:
        """
        Analyze a JD via talent-agent's matching engine.
        Returns structured data for generating targeted interview questions.

        Args:
            jd_text: Raw job description text
            language: Response language (en/zh)

        Returns:
            {
                "key_skills": [...],
                "suggested_questions": [...],
                "difficulty_level": "intermediate",
                "focus_areas": [...]
            }
        """
        try:
            client = await self._get_client()
            resp = await client.post(
                "/match",
                json={"raw_jd": jd_text, "top_k": 3, "language": language},
            )
            resp.raise_for_status()
            match_result = resp.json()

            # Extract relevant info for interview prep
            return {
                "key_skills": match_result.get("required_skills", []),
                "focus_areas": match_result.get("skill_gaps", []),
                "difficulty_level": _infer_difficulty(match_result),
                "match_data": match_result,
            }
        except Exception as e:
            return {"error": str(e), "key_skills": [], "focus_areas": []}

    async def start_mock_interview(self, jd_text: str, interview_type: str = "tech") -> dict:
        """
        Start a mock interview session via talent-agent.
        Returns the first question to ask.

        Args:
            jd_text: Job description for context
            interview_type: One of 'tech', 'behavior', 'comprehensive'
        """
        try:
            client = await self._get_client()
            resp = await client.post(
                "/interview/start",
                json={
                    "raw_jd": jd_text,
                    "interview_type": interview_type,
                    "mode": "tech",
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    async def submit_interview_turn(self, session_id: str, answer: str) -> dict:
        """
        Submit an interview answer and get the next question + feedback.

        Args:
            session_id: Talent-agent interview session ID
            answer: User's spoken answer (transcribed)
        """
        try:
            client = await self._get_client()
            resp = await client.post(
                "/interview/turn",
                json={
                    "session_id": session_id,
                    "answer": answer,
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    async def get_interview_debrief(self, session_id: str) -> dict:
        """
        Get performance debrief after completing an interview session.

        Args:
            session_id: Talent-agent interview session ID
        """
        try:
            client = await self._get_client()
            resp = await client.post(
                "/interview/debrief",
                json={"session_id": session_id},
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    async def sync_practice_result(self, session_data: dict) -> dict:
        """
        Sync oral practice results back to talent-agent.
        This allows talent-agent to track speaking skill progress.

        Args:
            session_data: Our session summary (scenario, turns, scores, corrections)
        """
        try:
            client = await self._get_client()
            # Use a custom endpoint or application tracking
            resp = await client.post(
                "/applications",
                json={
                    "title": f"Oral Practice: {session_data.get('scenario', 'unknown')}",
                    "status": "applied",
                    "notes": json.dumps({
                        "type": "oral_practice_sync",
                        "session_id": session_data.get("session_id"),
                        "scenario": session_data.get("scenario"),
                        "total_turns": session_data.get("total_turns", 0),
                        "avg_pronunciation": session_data.get("avg_pronunciation"),
                        "avg_fluency": session_data.get("avg_fluency"),
                    }),
                },
            )
            resp.raise_for_status()
            return {"synced": True, "data": resp.json()}
        except Exception as e:
            return {"synced": False, "error": str(e)}

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


def _infer_difficulty(match_result: dict) -> str:
    """Infer interview difficulty from match score."""
    score = match_result.get("blended_score", 0.5)
    if score >= 0.7:
        return "advanced"
    elif score >= 0.4:
        return "intermediate"
    return "beginner"


# Global instance (lazy init)
_client: Optional[TalentAgentClient] = None


def get_talent_agent() -> TalentAgentClient:
    """Get or create the global talent-agent client."""
    global _client
    if _client is None:
        _client = TalentAgentClient()
    return _client
