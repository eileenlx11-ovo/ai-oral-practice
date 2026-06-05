# Progress Dashboard

Interactive progress visualization built with Vue 3 + Chart.js.

## Features

- Summary cards: total sessions, turns spoken, corrections received, avg pronunciation
- Score trend line chart (pronunciation, fluency, accuracy over time)
- Session history list with click-to-detail
- Session detail modal: per-session report with common error patterns

## Data Source

Fetches from backend APIs:

- `GET /api/progress` — aggregated metrics
- `GET /api/sessions` — session list
- `GET /api/sessions/:id/summary` — detailed report
