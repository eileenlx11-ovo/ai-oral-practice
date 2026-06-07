# Review: auth i18n theme hardening - 2026-06-07

Reviewer: Codex
Commit: working tree

## Critical
- [x] **[assessment/app.py:70]** Session endpoints initially filtered lists by user but did not enforce ownership for direct `session_id` access. A caller who knew another session id could read or mutate summaries/turns/end state. Fixed by adding `_require_session_owner()` and applying it to chat/stream reuse, manual turns, summary, end, and talent-agent sync.

## Important
- [x] **[assessment/feedback/__init__.py:24]** Sessions needed a persisted `user_id` so progress and session list APIs could isolate authenticated users. Fixed with `user_id` on session creation and filters for list/progress while preserving `default_user` compatibility.
- [x] **[assessment/user_profile.py:85]** Profile and memory file names used raw user ids. Email ids and future ids could create awkward filenames. Fixed with `_safe_user_id()` for profile and memory paths.
- [x] **[frontend/src/main.js:10]** Settings page was available to guests while it writes account settings. Fixed by adding `requiresAuth` guard and redirect preservation.

## Minor / Style
- [x] **[frontend/styles/variables.css:97]** Duplicate dark theme token blocks existed after parallel work. Fixed by keeping one dark override block.
- [x] **[frontend/settings/SettingsView.vue:43]** Local loop variable named `t` shadowed the i18n translator. Fixed by renaming the loop variable.

## Verification
- `python -m pytest assessment\tests` - 27 passed
- `python -c "from assessment.app import app; print('OK')"` - OK
- `cd frontend && npm run build` - passed
- `cd frontend && npm test` - 4 files / 26 tests passed

## Final Review Gate
Approved for local commit. No blocking issues remain in this scope.
