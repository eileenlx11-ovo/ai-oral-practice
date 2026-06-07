# Review: architecture and security — 2026-06-07

Reviewer: Codex
Commit: working tree (`fix/polish-and-readme`)

## Critical

- [x] **[assessment/app.py:1326]** Session playback exposes full session data without owner check. `GET /api/sessions/{session_id}/turns-full` calls `store.get_session(session_id)` directly and returns the whole JSON, including transcript, corrections, custom prompt metadata, and user-related context. Other session APIs use `_require_session_owner(...)`, so this is an access-control gap rather than an intentional public route. → fix: add `user: dict | None = Depends(get_optional_user)` and call `_require_session_owner(session_id, user)` before returning data; update playback frontend to send auth headers. **FIXED (Claude, working tree): route now returns `_require_session_owner(...)`; PlaybackView sends `getAuthHeaders()`; covered by `test_turns_full_requires_owner`.**

- [x] **[assessment/app.py:1335]** Session recordings can be fetched without owner check. `GET /api/sessions/{session_id}/recording/{turn_index}` builds a path from `session_id` and serves the `.webm` file directly. `SessionStore._load` rejects traversal, but this route bypasses `_load`, so `session_id` can contain path separators and the route also ignores session ownership. → fix: validate/resolve the recording path under `RECORDINGS_DIR`, reject invalid `session_id`, and require `_require_session_owner(...)`. **FIXED (Claude, working tree): owner check (also rejects path-separator ids) + `resolve()` containment check under `RECORDINGS_DIR`; PlaybackView fetches the blob with auth then plays it; covered by `test_recording_requires_owner_and_rejects_traversal`.**

- [x] **[assessment/app.py:1344]** AI session review can be generated for another user's session. `POST /api/sessions/{session_id}/review` reads the session directly and sends the transcript to the LLM. This leaks private interview/practice content to any caller with a session id and can burn LLM quota. → fix: require owner check before reading the session and rate-limit review generation. **FIXED (Claude, working tree): owner check via `_require_session_owner(...)` before reading the session; covered by `test_review_requires_owner`. Rate-limiting deferred to the Important rate-limit item below.**

## Important

- [ ] **[frontend/chat/ChatView.vue:646]** Auth exists but most practice APIs do not send `Authorization`. Logged-in users call `/api/stream`, `/api/sessions/{id}/end`, `/api/sessions/{id}/handoff`, `/api/sessions/{id}/character`, `/api/progress`, and `/api/sessions` without `getAuthHeaders()`. The backend therefore treats these as `default_user`, breaking user isolation and causing logged-in data to mix with guest data. → fix: introduce one `apiFetch` helper that attaches `getAuthHeaders()` for all same-origin API calls, including SSE form posts.

- [ ] **[assessment/app.py:1434]** Analytics ignores user ownership. `/api/analytics` calls `assessment.analytics.get_analytics(days)`, whose loader reads every `assessment/data/sessions/*.json` and does not filter by `user_id`. The dashboard can therefore aggregate other users' vocabulary, error distribution, and practice duration. → fix: pass current user id into analytics and filter sessions consistently with `SessionStore.get_progress`.

- [ ] **[assessment/app.py:987]** `/api/assess` is anonymous, expensive, and unthrottled. Every request can run ffmpeg plus Tencent/Azure scoring. On a public demo domain this is a quota/cost exhaustion vector. Claude's previous scan also flagged this. → fix: keep demo usable but add per-IP/per-user rate limiting and a small daily cap; optionally require auth for advanced scoring.

- [ ] **[assessment/app.py:1571]** Orphan realtime WebSocket remains unauthenticated. The frontend realtime correction UI has been removed, but `/ws/realtime-pronunciation` still accepts arbitrary audio chunks and can trigger ASR + pronunciation scoring without auth or size cap. → fix: delete the route/module if the feature is not used, or add auth/token validation, per-connection byte caps, and rate limits.

- [ ] **[assessment/auth.py:20]** Production can silently fall back to a hardcoded JWT secret. If `JWT_SECRET` is missing in deployment, all tokens are signed with `oral-practice-dev-secret-change-in-prod`. → fix: fail startup in production when `JWT_SECRET` is absent or equal to the default; keep a dev-only fallback behind an explicit environment flag.

- [ ] **[assessment/app.py:121]** Upload validation is only byte-size based. `_read_audio` caps uploads at 10MB and rejects tiny files, but does not validate MIME allowlist, duration, or decoded audio properties. This leaves ffmpeg/ASR/scoring endpoints open to malformed media and long decode workloads inside the 10MB cap. → fix: allow known audio types, probe duration after decode, and enforce a short maximum duration for scoring/chat.

- [ ] **[assessment/integrations/talent_agent.py:28]** `TALENT_AGENT_URL` is environment-controlled and the client will send `X-Internal-Token` to that base URL. This is acceptable only if env is trusted, but it is an SSRF/secret-forwarding risk under compromised config or unsafe admin UI. → fix: validate allowed hostnames/schemes for production and never send the internal token to non-allowlisted hosts.

## Minor / Style

- [ ] **[frontend/composables/useAuth.js:7]** JWT is stored in `localStorage`, so any future XSS would expose bearer tokens. Current Vue templates mostly use interpolation and do not show obvious `v-html`, but this should still be called out. → fix later: consider short-lived access token + HttpOnly refresh cookie when auth becomes more serious.

- [ ] **[assessment/sms.py:24]** SMS code generation uses `random.randint`, not `secrets`. It is low risk for an MVP with SMS TTL and attempt caps, but verification codes should use `secrets.randbelow` in production.

- [ ] **[assessment/app.py:83]** CORS defaults to `"*"` when `CORS_ORIGINS` is not set. Production compose overrides it correctly, but local/staging can accidentally deploy open CORS. → fix: make production startup reject wildcard origins.

- [ ] **[assessment/scoring/tencent.py:236]** Tencent SOE `voice_id` uses `uuid.uuid1()`, which includes timestamp/MAC-derived information. This is not a direct exploit here, but `uuid4()` is cleaner for opaque request IDs.

## Notes

- The reported bug "创建对话伙伴后点击开始练习没有任何反应" was caused by `/api/sessions/topic` waiting for an LLM-generated greeting before returning. If the upstream LLM was slow or unavailable, the frontend remained in loading state and never navigated. This working tree changes `assessment/app.py` so topic session creation returns immediately with a deterministic local greeting, adds `user_id` ownership when a user is logged in, and adds a regression test in `assessment/tests/test_characters.py`.

- Architecture summary: the project is a Vue SPA behind nginx, with a FastAPI backend doing ASR, LLM chat, TTS, pronunciation scoring, file-based sessions/profiles/users, and Talent Agent integration. The main architectural risk is that auth was added after many MVP endpoints already existed, so backend ownership checks and frontend auth headers are applied inconsistently.

- Deployment summary: production compose binds frontend/backend to localhost and sets restricted `CORS_ORIGINS`, which is good. Data and audio cache are persisted in Docker volumes. The privacy claim around local recordings needs careful wording: browser object URLs are local, but backend also saves conversation recordings under `assessment/data/recordings` for playback.

- Current gate: **the three Critical session access-control issues are fixed (Claude, working tree) with regression tests (`test_session_access_control.py`), so the demo-blocking access-control risk is cleared.** Remaining Important items (anonymous/unthrottled `/api/assess`, analytics user isolation, JWT secret fallback, orphan realtime WS, upload validation, talent-agent SSRF) are accepted as known demo-only risks and tracked for post-demo hardening. The custom-topic navigation fix is low-risk and covered by a regression test.
