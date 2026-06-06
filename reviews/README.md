# Reviews

## Current Review Gate

- Scope: auth i18n theme hardening
- Review file: `reviews/2026-06-07_auth_i18n_theme.md`
- Status: Approved for local commit
- Verification:
  - `python -m pytest assessment\tests` - 27 passed
  - `python -c "from assessment.app import app; print('OK')"` - OK
  - `cd frontend && npm run build` - passed
  - `cd frontend && npm test` - 4 files / 26 tests passed
