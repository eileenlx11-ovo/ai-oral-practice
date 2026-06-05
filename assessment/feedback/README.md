# Feedback & Progress Tracking

Post-session summaries and longitudinal progress data.

## API

- `GET /api/sessions` — List all past practice sessions with scores
- `GET /api/sessions/:id/summary` — Detailed session report
- `GET /api/progress` — Aggregated progress metrics over time

## Data

Sessions stored as JSON files in `data/sessions/` (MVP, upgrade to SQLite if needed).
