# Reviews

## Current Review Gate

- Scope: architecture/security full-project scan + custom-topic start fix
- Review file: `reviews/2026-06-07_arch_security.md`
- Status: Not approved for deploy until Critical session access-control findings are fixed or explicitly accepted as demo-only risk
- Verification:
  - `python -m pytest assessment\tests` - 46 passed
  - `cd frontend && npm run build` - OK
  - `python -c "from assessment.app import app; print('OK')"` - OK
