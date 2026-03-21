# Refactor Status (2026-03-05)

## Completed
- `C2.1` Refactored one duplicated `manage_bookings` return path to shared helper.
- `C2.2` Refactored an additional duplicated `manage_bookings` return path.
- `T5` Hardened `CORE_SMOKE` mode behavior in `scripts/e2e_playwright.py`.
- `C1.1` Introduced `app/domain` package and first extraction (`formatting`).
- `C1.2` Moved auth logic to `app/domain/auth.py` with `logic.py` wrappers.
- `C1.3` Moved customer logic to `app/domain/customers.py` with wrappers.
- `C1.4` Moved services logic to `app/domain/services.py` with wrappers.
- `C1.5` Moved dresses logic to `app/domain/dresses.py` with wrappers.
- `C1.6` Moved bookings logic to `app/domain/bookings.py` with wrappers.
- `C1.7` Moved payments logic to `app/domain/payments.py` with wrappers.
- `C1.8` Removed unreachable legacy code from `logic.py` (thin facade cleanup).
- Post-plan hardening: synced domain `SessionLocal` from `logic.SessionLocal` for test monkeypatch compatibility.
- Post-plan cleanup: removed unused imports from `logic.py`.

## Current State
- `logic.py` is reduced and acts as a facade over domain modules.
- Domain modules now own CRUD/auth logic:
  - `app/domain/auth.py`
  - `app/domain/customers.py`
  - `app/domain/services.py`
  - `app/domain/dresses.py`
  - `app/domain/bookings.py`
  - `app/domain/payments.py`
- Baseline validations are green on this snapshot:
  - `python -m py_compile app_dash.py logic.py models.py`
  - `python scripts/health_check.py`
  - `python -m pytest -q` (10 passed)
  - App HTTP probe to `http://127.0.0.1:8050` returned `200`

## Notes
- Health check currently reports some historical missing-reference rows in live DB test data for names created during tests.
- This status file is documentation-only and does not change runtime behavior.

