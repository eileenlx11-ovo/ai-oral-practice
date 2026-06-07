# Review: SSE error handling - 2026-06-07

Reviewer: Codex
Commit: working tree

## Critical
- [x] **[assessment/app.py:350]** Runtime exceptions inside the SSE generator previously closed the stream without an `event:error`, leaving the frontend with a generic disconnected state. Fixed ASR and LLM phases to emit structured `error` events and return cleanly.

## Important
- [x] **[assessment/app.py:391]** TTS failure during one streamed sentence could abort the whole chat response. Fixed by treating per-sentence TTS as optional: text still streams and `audio_url` becomes `null`.
- [x] **[voice/asr/service.js:98]** Frontend error callback only received the message string, so structured backend error metadata would be lost. Fixed by passing `(message, payload)` while preserving existing first-argument behavior.

## Minor / Style
- [x] **[frontend/__tests__/streamChat.test.js:120]** Added regression coverage for structured SSE error payloads.

## Verification
- `cd frontend && npx vitest run __tests__/streamChat.test.js` - 8 passed
- `python -m pytest assessment\tests` - 27 passed
- `python -c "from assessment.app import app; print('OK')"` - OK
- `cd frontend && npm test` - 4 files / 26 tests passed
- `cd frontend && npm run build` - passed

## Final Review Gate
Approved for local commit. No blocking issues remain in this scope.
