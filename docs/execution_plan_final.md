# MyAtelier — Execution Plan v2 (Corrected)

> STATUS: Historical execution plan.
> This file describes a proposed step-by-step plan at the time it was written, not the current implemented state.
> For current behavior and architecture, use `docs/01_overview.md` through `docs/06_developer_reference.md`.

> **Created:** 2026-02-18  
> **Corrected based on:** ChatGPT review feedback (6 points addressed)  
> **Execution model:** Step-by-step with your approval before each step. No step runs until you say go.

---

## Corrections Applied (vs v1)

| v1 Issue | Fix in v2 |
|---|---|
| Assumed phase1b1 PASS — actually failing on Services export | Phase 1 now starts by diagnosing ALL current test failures, no assumptions |
| `git reset --hard` in rollback | Removed. Only `git revert` (safe, preserves history) |
| Phase 6 & 7 too large for "small step" | Each domain extraction is now a separate numbered step with its own validation |
| Phase 0.3 (git rm --cached backups/) is a big index change | Marked as REQUIRES YOUR EXPLICIT APPROVAL, separated from other steps |
| "No commands until approval" conflicts with workflow | Changed to: each step proposed → you approve → execute → report PASS/FAIL |
| Numbers may drift | All counts labeled as "at time of analysis" — verify before acting |

---

## Execution Model

```
For each step:
  1. AI proposes what to do (exact files, exact changes)
  2. You approve or modify
  3. AI executes the change
  4. AI runs validation
  5. AI reports PASS/FAIL
  6. If PASS → commit → next step
  7. If FAIL → revert → diagnose → retry
```

**No step skipping. No combining steps. One commit per step.**

---

## Phase 0: Immediate Safeguards

**Time:** ~30 min | **Risk:** Minimal | **Behavioral change:** None

### Step 0.1 — Secret Key Production Guard
**File:** `app_dash.py` (after line 9)  
**Change:** Add 3 lines: if `APP_ENV=production` and secret key is default → print error, exit.  
**Risk:** Zero. Only affects production mode.  
**Validate:** py_compile → health_check → app starts locally

### Step 0.2 — Update .gitignore
**File:** `.gitignore`  
**Change:** Add `backups/`, `releases/`, `atelier.db`, `dress_images/`  
**Risk:** Zero. Only affects future git tracking.  
**Validate:** py_compile (sanity) → `git status` shows fewer noise files

### Step 0.3 — Untrack Backup/Release Artifacts from Git Index
⚠️ **REQUIRES YOUR EXPLICIT APPROVAL BEFORE EXECUTING**  
**Command:** `git rm -r --cached backups/ releases/ atelier.db`  
**What happens:** Files stay on disk. Git stops tracking them. Next commit will be large (removing index entries).  
**Why separate:** This is a significant git history change. You decide when/if to do it.  
**Validate:** `git status` clean of backup noise

### Step 0.4 — Create Status Tracker
**File:** `docs/phase_status_tracker.md`  
**Change:** Simple checklist file to track progress across sessions.

---

## Phase 1: E2E Stabilization

**Time:** 1-3 hours | **Risk:** Low (test code only) | **Priority:** Highest

### Step 1.1 — Discover Actual Test State (NO ASSUMPTIONS)
**Action:** Run each test mode and record actual results. Do not assume anything passes.
```
python -m py_compile app_dash.py logic.py models.py
python scripts/health_check.py
python app_dash.py  →  verify http://127.0.0.1:8050
CORE_SMOKE=1 python scripts/e2e_playwright.py
FULL_REGRESSION=1 FULL_PHASE=phase1b1 python scripts/e2e_playwright.py
FULL_REGRESSION=1 FULL_PHASE=phase1b2a python scripts/e2e_playwright.py
FULL_REGRESSION=1 FULL_PHASE=phase1b2 python scripts/e2e_playwright.py
```
**Output:** Actual PASS/FAIL for each. Screenshot of each failure point.  
**No fixes yet.** Just establish ground truth.

### Step 1.2 — Fix Earliest Failing Test
**Action:** Take the FIRST test phase that fails (could be phase1b1/Services export if ChatGPT is right). Diagnose and fix ONE issue:
- Add diagnostic prints + screenshot before the failure point
- Identify root cause (timeout? selector? modal stuck? export path?)
- Apply minimal targeted fix

**Validate:** The fixed test passes. Earlier passing tests still pass.

### Step 1.3 — Repeat Step 1.2 for Next Failure
**Action:** If more phases fail, fix one at a time. Each fix = one step = one commit.  
**Repeat until:** phase1b1 passes.

### Step 1.4 — Fix phase1b2 Hang
**Action:** Same diagnostic approach for the phase1b2 hang after customers step:
- Add timestamp logging between each action in the customers flow
- Add screenshots before/after modal interactions
- Most likely fix: add `wait_for_no_modal()` or `page.wait_for_load_state("networkidle")` between operations

**Validate:** phase1b2 passes 3 consecutive runs.

### Step 1.5 — Unlock Full Regression
**Action:** Run `FULL_REGRESSION=1 FULL_PHASE=all`. Fix remaining failures one at a time.  
**Validate:** Full regression passes.

### Step 1.6 — Verify Smoke Suite
**Action:** Confirm `CORE_SMOKE=1` mode works and completes in under 60 seconds.  
**Validate:** Smoke passes in < 60s.

### Phase 1 Exit Criteria
- `FULL_REGRESSION=1 FULL_PHASE=all` passes 3 consecutive runs
- `CORE_SMOKE=1` passes in < 60s

---

## Phase 2: Backup Drag Removal

**Time:** ~30 min | **Risk:** Low | **Impact:** Every CRUD gets faster

### Step 2.1 — List All _backup_before_write Call Sites
**Action:** grep `logic.py` for `_backup_before_write`. List each call site.  
**No changes yet.** Just inventory.

### Step 2.2 — Remove Backup Calls from CRUD Functions
**File:** `logic.py`  
**Change:** Remove every `_backup_before_write(...)` call and associated guard `if not ok_backup`.  
**Keep:** The function definition, the import, manual backup button in Settings.  
**Validate:** py_compile → health_check → smoke E2E → manually test add customer (should be instant now)

### Step 2.3 — Verify Manual Backup Still Works
**Action:** Start app → Settings → click backup button → verify snapshot created.

### Step 2.4 — Add Lightweight Daily Auto-Backup (Optional)
**File:** `logic.py` → `init_folders()`  
**Change:** On app startup, copy `atelier.db` once per day to `backups/daily_YYYYMMDD.db`.  
**Validate:** Restart app → check backup file created → restart again → no duplicate

### Phase 2 Exit Criteria
- CRUD operations have no backup I/O delay
- Manual backup works
- Daily startup backup works

---

## Phase 3: Repository Hygiene

**Time:** ~30 min | **Risk:** Minimal

### Step 3.1 — Verify .gitignore Working
**Action:** `git status` should not show backup/release files.

### Step 3.2 — Fix __pycache__ Gitignore
**File:** `.gitignore`  
**Change:** Ensure `**/__pycache__/` covers all subpackages.

### Step 3.3 — Normalize Line Endings
**File:** `.gitattributes` (new file)  
**Change:** Add `*.py text eol=lf` rules. Run `git add --renormalize .`  
**Validate:** py_compile passes

### Step 3.4 — Remove Dead Code
**File:** `logic.py`  
**Change:** Remove `save_data()` (no-op at line ~448) and `save_department()` (trivial wrapper at line ~547).  
**Validate:** py_compile → health_check → grep to confirm nothing calls them

### Phase 3 Exit Criteria
- `git diff` shows only real code changes
- No dead functions remain

---

## Phase 4: Financial Precision

**Time:** ~1 hour | **Risk:** Medium (touches data layer)

### Step 4.1 — Change Model Types
**File:** `models.py`  
**Change:** `Float` → `Numeric(precision=12, scale=2)` for all money columns.  
**Validate:** py_compile → health_check → smoke E2E

### Step 4.2 — Add Rounding to Booking Arithmetic
**File:** `logic.py`  
**Change:** `round(x, 2)` on all `remaining = price - paid` calculations in `add_booking`, `update_booking`.  
**Validate:** py_compile → health_check → add a test booking via E2E

### Step 4.3 — Add Rounding to Payment Arithmetic
**File:** `logic.py`  
**Change:** `round(x, 2)` on all `remaining_after` calculations in `add_payment`, `update_payment`.  
**Validate:** py_compile → health_check → add a test payment via E2E

### Step 4.4 — Add Financial Health Check
**File:** `scripts/health_check.py`  
**Change:** New function `_check_financial_integrity()`: assert `remaining == price - paid` (±0.01) for all bookings.  
**Validate:** health_check passes with new assertion

### Phase 4 Exit Criteria
- health_check financial assertions pass with zero discrepancies
- E2E payment flows pass

---

## Phase 5: Referential Integrity

**Time:** 2-3 hours | **Risk:** Medium-High (data layer + callbacks)

### Step 5.1 — Backfill NULL customer_id in Bookings
**File:** `logic.py`  
**Change:** Add `_backfill_booking_customer_ids()` called from `init_folders()`.  
**Validate:** health_check → count of NULL customer_id should be 0

### Step 5.2 — Verify service_id Backfill Complete
**Action:** Query DB to confirm zero NULL `service_id` in bookings.  
**If gaps exist:** Fix backfill logic, re-run.

### Step 5.3 — Update add_booking to Always Set IDs
**File:** `logic.py` → `add_booking()`  
**Change:** Always resolve and set `customer_id` and `service_id` from lookups.  
**Validate:** py_compile → health_check → E2E: add booking flow

### Step 5.4 — Update update_booking to Always Set IDs
**File:** `logic.py` → `update_booking()`  
**Change:** Same as 5.3 for update path.  
**Validate:** py_compile → health_check → E2E: edit booking flow

### Step 5.5 — Add Orphan Detection to Health Check
**File:** `scripts/health_check.py`  
**Change:** Enhance `_check_missing_refs()` for all FK relationships.  
**Validate:** health_check passes with zero orphans

### Step 5.6 — Simplify Name Propagation (After IDs Reliable)
**File:** `logic.py` → `update_customer()`, `update_service()`  
**Change:** Replace O(n) scan-all-bookings loop with ID-based update.  
**Validate:** py_compile → health_check → FULL E2E

### Phase 5 Exit Criteria
- Zero NULL FK fields
- Zero orphaned references in health_check
- FULL E2E passes

---

## Phase 6: logic.py Decomposition

**Time:** 3-5 hours | **Risk:** Medium (structural, but facade preserves behavior)

**Each sub-step = one domain moved + one validation cycle.**

### Step 6.1 — Create app/domain/ Package
**Action:** Create `app/domain/__init__.py` and empty domain files.  
**Validate:** py_compile

### Step 6.2 — Extract Auth Domain
**Move to `app/domain/auth.py`:** `hash_password`, `verify_password`, `check_users`, `save_users_data`, `update_user_password_hash`, `_hash_password_*`, `_is_strong_bootstrap_password`, `_bootstrap_admin_if_enabled`  
**In `logic.py`:** Add `from app.domain.auth import *`  
**Validate:** py_compile → health_check → smoke E2E

### Step 6.3 — Extract Departments Domain
**Move to `app/domain/departments.py`:** `check_departments`, `add_department`, `update_department`, `delete_department`, `_find_department_by_name`, `_canonical_department_name`, `_ensure_unknown_department`, `_migrate_departments_from_csv`  
**In `logic.py`:** Add `from app.domain.departments import *`  
**Validate:** py_compile → health_check → smoke E2E

### Step 6.4 — Extract Customers Domain
**Move to `app/domain/customers.py`:** `add_customer`, `update_customer`, `delete_customer`  
**Validate:** py_compile → health_check → smoke E2E

### Step 6.5 — Extract Services Domain
**Move to `app/domain/services.py`:** `add_service`, `update_service`, `delete_service`  
**Validate:** py_compile → health_check → smoke E2E

### Step 6.6 — Extract Dresses Domain
**Move to `app/domain/dresses.py`:** `add_dress`, `update_dress`, `delete_dress`, `save_image`  
**Validate:** py_compile → health_check → smoke E2E

### Step 6.7 — Extract Bookings Domain
**Move to `app/domain/bookings.py`:** `add_booking`, `update_booking`, `delete_booking`  
⚠️ This has the most cross-domain dependencies. Move carefully.  
**Validate:** py_compile → health_check → FULL E2E

### Step 6.8 — Extract Payments Domain
**Move to `app/domain/payments.py`:** `add_payment`, `update_payment`, `delete_payment`  
**Validate:** py_compile → health_check → FULL E2E

### Step 6.9 — Extract Data Loader
**Move to `app/domain/data_loader.py`:** `load_data`, column mappings (`C_COLS_MAP`, etc.)  
**Validate:** py_compile → health_check → FULL E2E

### Step 6.10 — Slim logic.py to Facade
**File:** `logic.py`  
**Change:** Should now only contain re-exports + `init_folders()` + `DATA_CACHE`. Target < 100 lines.  
**Validate:** py_compile → callback count unchanged → FULL E2E

### Step 6.11 — Split bookings_form.py
**File:** `app/callbacks/bookings_form.py` (28KB)  
**Split into:**
- `bookings_modal.py` — modal open/close
- `bookings_save.py` — save/update/delete
- `bookings_helpers.py` — dropdown population, validation  
**Update:** `register_all.py`  
**Validate:** py_compile → callback count unchanged → FULL E2E

### Phase 6 Exit Criteria
- `logic.py` < 100 lines
- Each domain file < 250 lines
- Callback count unchanged
- FULL E2E passes

---

## Phase 7: Unit Tests

**Time:** 2-3 hours | **Risk:** None (additive only)

**Each sub-step = one test file.**

### Step 7.1 — Test Infrastructure
**Create:** `tests/conftest.py` with in-memory SQLite fixture + `tests/__init__.py`  
**Add:** `pytest` to `requirements_dash.txt`  
**Validate:** `pytest tests/` runs (0 tests collected, no errors)

### Step 7.2 — Auth Tests
**File:** `tests/test_auth.py`  
**Tests:** hash→verify round-trip, wrong password, legacy SHA256, strong password rules  
**Validate:** `pytest tests/test_auth.py -v`

### Step 7.3 — Customer CRUD Tests
**File:** `tests/test_customers.py`  
**Tests:** add valid, add missing fields, add duplicate phone, update, delete, delete-blocked  
**Validate:** `pytest tests/test_customers.py -v`

### Step 7.4 — Service CRUD Tests
**File:** `tests/test_services.py`  
**Validate:** `pytest tests/test_services.py -v`

### Step 7.5 — Dress CRUD Tests
**File:** `tests/test_dresses.py`  
**Validate:** `pytest tests/test_dresses.py -v`

### Step 7.6 — Booking CRUD Tests
**File:** `tests/test_bookings.py`  
**Tests:** Include financial calculations (remaining = price - paid)  
**Validate:** `pytest tests/test_bookings.py -v`

### Step 7.7 — Payment CRUD Tests
**File:** `tests/test_payments.py`  
**Tests:** Include remaining_after calculations, cumulative payments  
**Validate:** `pytest tests/test_payments.py -v`

### Phase 7 Exit Criteria
- `pytest tests/ -v` all pass
- ≥1 positive + 1 negative test per CRUD operation

---

## Phase 8: Cleanup & Closure

**Time:** ~1 hour

### Step 8.1 — Investigate table_content/dresses.py (67KB)
**Action:** Examine why it's so large. Likely contains embedded data or excessive inline logic. Refactor if easy.

### Step 8.2 — Update All Docs
**Files:** All `docs/*.md`  
**Change:** Reflect actual final architecture (include `app/domain/` layer).

### Step 8.3 — Final Full Validation
```
python -m py_compile app_dash.py logic.py models.py
python -c "import app_dash; print('callbacks', len(app_dash.app.callback_map))"
python scripts/health_check.py
pytest tests/ -v
FULL_REGRESSION=1 FULL_PHASE=all python scripts/e2e_playwright.py  (3 consecutive PASS)
```

### Step 8.4 — Tag Release
```
git tag -a v1.0-stable -m "All phases complete"
```

### Definition of Done
- [ ] Secret key enforced in production
- [ ] .gitignore excludes generated artifacts
- [ ] No automatic backup on CRUD writes
- [ ] Financial fields use fixed-point, `remaining == price - paid`
- [ ] All FK relationships populated, zero orphans
- [ ] `logic.py` < 100 lines (facade only)
- [ ] E2E full regression passes 3 consecutive runs
- [ ] Unit tests pass for all CRUD + auth
- [ ] Docs reflect actual architecture

---

## Rollback Strategy (Safe Only)

| Scenario | Action |
|---|---|
| Single file broke | `git checkout -- <file>` |
| Last commit was bad | `git revert HEAD` |
| Multiple commits bad | `git revert <oldest-bad>..HEAD` |
| Database corrupted | Copy latest `backups/daily_*.db` → `atelier.db` |
| Full project restore | Unzip latest from `releases/` |

> ⚠️ **Never use `git reset --hard`.** Always use `git revert` to preserve history.

---

## Quick Reference

| Phase | What | Time | Risk |
|---|---|---|---|
| 0 | Secret key + .gitignore | 30 min | Zero |
| 1 | E2E stabilization | 1-3 hrs | Low |
| 2 | Remove backup-per-write | 30 min | Low |
| 3 | Repo hygiene | 30 min | Minimal |
| 4 | Financial precision | 1 hr | Medium |
| 5 | Referential integrity | 2-3 hrs | Medium-High |
| 6 | logic.py decomposition | 3-5 hrs | Medium |
| 7 | Unit tests | 2-3 hrs | None |
| 8 | Closure | 1 hr | None |

**Total: ~12-18 hours across multiple sessions.**
