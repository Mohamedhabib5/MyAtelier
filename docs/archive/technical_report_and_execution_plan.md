# MyAtelier — Technical Report, Execution Plan & Recommendations

> STATUS: Historical analysis document from 2026-02-18.
> Some findings and recommendations here are no longer current.
> For current behavior, use `docs/01_overview.md` through `docs/06_developer_reference.md` and the live code.
> Examples of newer behavior not fully reflected here include the role-aware Users screen, one-time default admin seeding, and direct ZIP backup download.
> Additional newer behavior not fully reflected here includes the responsive phone/tablet shell, phone card-list rendering on data-heavy screens, and `RESPONSIVE_SMOKE` browser validation.

> **Generated:** 2026-02-18  
> **Context:** Read-only assessment of the MyAtelier Dash application  
> **Purpose:** This document is designed for any AI assistant or engineer to understand the project's current state and make informed decisions about next steps.  
> **No code was changed or commands executed to produce this report.**

---

## Project Overview

MyAtelier is a **bridal atelier management system** built with Python Dash, Flask, SQLAlchemy (SQLite). It manages customers, bookings, services, dresses, payments, and finance reports with an Arabic-language UI.

### Tech Stack
- **Frontend:** Dash + Dash Bootstrap Components + AG Grid
- **Backend:** Flask (Dash's built-in server)
- **ORM:** SQLAlchemy
- **Database:** SQLite (`atelier.db`)
- **Testing:** Playwright (E2E), custom health_check script
- **Language:** Python 3

### Entry Points
- **App:** `app_dash.py` → starts Dash server on port 8050
- **Health check:** `scripts/health_check.py`
- **E2E tests:** `scripts/e2e_playwright.py`

---

## Part A: Current-State Report

### 1. Architecture Status

The app follows a layered modular architecture:

```
app_dash.py (Entrypoint — 130 lines)
├── app/bootstrap.py          → Dash app factory (20 lines)
├── app/composition/
│   ├── wiring.py             → Runtime dependency injection (88 lines)
│   └── layout_factory.py     → Main layout builder adapter
├── app/layouts/               → 12 files, pure UI structure per feature
│   ├── main.py               → Post-login shell (sidebar, tabs, stores)
│   ├── root.py               → URL + session store wrapper
│   ├── login.py              → Login form
│   ├── customers.py, bookings.py, services.py, dresses.py
│   ├── payments.py, finance.py, settings.py, users.py
├── app/table_content/         → 8 files, table rendering per feature
│   ├── factory.py            → Builder registry
│   ├── dresses.py            → ⚠️ 67KB — anomalously large
│   └── customers.py, bookings.py, payments.py, services.py, departments.py
├── app/callbacks/             → 21 files, user interaction logic
│   ├── register_all.py       → Single callback registration hub (140 lines)
│   ├── auth.py               → Login/logout/session
│   ├── bookings_form.py      → ⚠️ 28KB — largest callback
│   ├── customers_form.py, services_form.py, dresses_form.py
│   ├── payments_form.py, details_view.py, details_actions.py
│   ├── *_search.py           → Search callbacks per feature
│   ├── navigation.py, finance.py, export.py
│   ├── settings_backup.py, settings_departments.py, users.py
├── app/services/
│   └── backup_service.py     → Full-project snapshot backup (100 lines)
├── app/ui/grid.py            → Shared AG Grid rendering helper
├── app/constants.py          → Shared constants (16 lines)
├── app/text_utils.py         → Text normalization helpers
├── logic.py                  → ⚠️ ALL business logic — 1142 lines, 53 functions
├── models.py                 → SQLAlchemy ORM models — 105 lines, 6 models
└── scripts/
    ├── health_check.py       → Data integrity checks (310 lines)
    ├── e2e_playwright.py     → ⚠️ Monolithic E2E — 1489 lines
    └── repair_data.py        → Data repair utility
```

#### Architecture Health Summary
| Component | Status | Notes |
|---|---|---|
| Entrypoint (`app_dash.py`) | ✅ Clean | Thin, only bootstrap + wiring + registration |
| Composition layer | ✅ Clean | DI pattern works well |
| Layouts | ✅ Good | Per-feature separation |
| Callbacks | ⚠️ Mostly good | `bookings_form.py` at 28KB needs splitting |
| Table content | ⚠️ One outlier | `dresses.py` at 67KB |
| Business logic (`logic.py`) | ⚠️ Monolith | 1142 lines, single file for everything |
| Models | ✅ Clean | 6 well-defined ORM models |
| Backup service | ⚠️ Costly | Full project copy on every single write |
| E2E tests | ⚠️ Monolith | 1489 lines, `main()` is 720 lines |

---

### 2. Database Schema (models.py)

6 ORM models:

| Model | Table | Primary Key | Key Fields | Relationships |
|---|---|---|---|---|
| `User` | `users` | `username` (String) | `password_hash`, `full_name`, `role`, `created_date` | — |
| `Department` | `departments` | `department_name` (String) | — | — |
| `Customer` | `customers` | `customer_id` (String, e.g. "C-101") | `name`, `groom_name`, `phone1`, `phone2`, `address`, `reg_date`, `notes` | → bookings |
| `Service` | `services` | `service_id` (String, e.g. "S-101") | `department`, `name`, `price` (Float) | — |
| `Dress` | `dresses` | `dress_code` (String) | `d_type`, `buy_date`, `description`, `image_path`, `status` | — |
| `Booking` | `bookings` | `booking_id` (String, e.g. "HR-123456") | `booking_date`, `customer_name`, `customer_id` (FK, nullable), `department`, `service_id` (FK, nullable), `service`, `dress_code`, `event_date`, `price` (Float), `paid` (Float), `remaining` (Float), `notes` | → customer, → payments |
| `Payment` | `payments` | `payment_id` (String, e.g. "PAY-123456") | `payment_date`, `booking_id` (FK), `amount` (Float), `customer_name`, `groom_name`, `remaining_after` (Float), `notes` | → booking |

#### Critical Schema Issues
1. **`Float` for money fields** — `price`, `paid`, `remaining`, `amount`, `remaining_after` all use IEEE 754 Float. This causes silent rounding errors in financial calculations.
2. **Nullable FKs** — `Booking.customer_id` and `Booking.service_id` are nullable. Some bookings link by name not ID.
3. **No FK for `dress_code`** — `Booking.dress_code` has no foreign key constraint to `dresses`.
4. **Denormalized names** — `Booking.customer_name` and `Payment.customer_name` duplicate data from `Customer.name`.
5. **String dates** — All date fields are strings, not date type. No format enforcement.

---

### 3. Authentication & Security

| Aspect | Implementation | Status |
|---|---|---|
| Hash algorithm (new) | PBKDF2-SHA256, 260K iterations, random salt | ✅ Good |
| Hash algorithm (legacy) | Plain SHA256, no salt | ⚠️ Exists in DB until user logs in |
| Hash migration | Auto-upgrade SHA256→PBKDF2 on successful login | ✅ Good |
| Session management | Flask server-side session (`flask.session`) | ✅ Good |
| Session trigger | `dcc.Store("user_session_store")` triggers callback that checks Flask session | ✅ Server-authoritative |
| Secret key | `os.environ.get("APP_SECRET_KEY", "myatelier-dev-secret-change-me")` | 🔴 **CRITICAL** if deployed without env var |
| Admin bootstrap | Env-var gated (`APP_BOOTSTRAP_ADMIN=1`), requires ≥10 char password with mixed case+digits | ✅ Secure |
| Password storage | DB column `password_hash` | ✅ |

**Key code location:** Authentication callbacks in `app/callbacks/auth.py` (96 lines). Password logic in `logic.py` lines 258-337.

---

### 4. Backup System (Current Problem)

Every single CRUD operation (add/update/delete for any entity) calls `_backup_before_write()` in `logic.py`, which calls `create_backup_snapshot()` in `app/services/backup_service.py`. This:

1. Copies the **entire project** (all code, DB, images, scripts) into `backups/<label>_<timestamp>/`
2. Creates a **zip** of the snapshot in `releases/<label>_<timestamp>.zip`

**Result:** 2853 backup folders + 60 release zips currently tracked in git.

**Impact:**
- Every CRUD operation has I/O cost of copying the entire project
- Git repository is bloated with backup data
- `.gitignore` does NOT exclude `backups/` or `releases/`

---

### 5. Testing Status

| Test | Script | What It Covers | Status |
|---|---|---|---|
| py_compile | `python -m py_compile app_dash.py logic.py models.py` | Syntax errors | ✅ PASS |
| Health check | `scripts/health_check.py` | Duplicate IDs, missing FK refs, numeric ranges, date validity, performance, roles, concurrency | ✅ PASS |
| HTTP smoke | Start app + GET `127.0.0.1:8050` | App loads | ✅ HTTP 200 |
| E2E phase1b1 | `FULL_REGRESSION=1 FULL_PHASE=phase1b1` | Depts + services + dresses + bookings CRUD | ✅ PASS |
| E2E phase1b2a | `FULL_REGRESSION=1 FULL_PHASE=phase1b2a` | Isolated services + customers CRUD | ✅ PASS |
| E2E phase1b2 | `FULL_REGRESSION=1 FULL_PHASE=phase1b2` | Combined services + customers + dependency chain | 🔴 **UNSTABLE — hangs after step 2 (customers)** |
| E2E phase2+ | Payments, settings, finance, export | — | ❌ **BLOCKED** by phase1b2 |
| Unit tests | None | — | ❌ **None exist** |

**E2E test structure problem:** `e2e_playwright.py` is 1489 lines with a single `main()` function spanning ~720 lines. Helpers (37 functions) are mixed inline. This monolithic structure makes debugging the phase1b2 hang very difficult.

---

### 6. Repository Hygiene

| Issue | Detail |
|---|---|
| `backups/` (2853 items) | Tracked in git, generated by every CRUD write |
| `releases/` (60 items) | Tracked in git, zip archives of backups |
| `atelier.db` | Tracked in git (229KB binary) |
| `dress_images/` | Tracked in git |
| `.gitignore` gaps | Missing: `backups/`, `releases/`, `atelier.db`, `dress_images/` |
| Mixed line endings | `\r\n` and `\n` mixed in `logic.py` and other files |
| `__pycache__/` in subpackages | Present on disk in `app/callbacks/`, `app/layouts/`, etc. |
| Dead code | `save_data()` is a no-op; `save_department()` is trivial wrapper |

---

### 7. Risk Registry (Ranked)

| # | Risk | Severity | Description |
|---|---|---|---|
| R1 | Default Flask secret key | **CRITICAL** | `"myatelier-dev-secret-change-me"` allows session forgery if deployed without setting `APP_SECRET_KEY` env var |
| R2 | Backup-on-every-write | **CRITICAL** | Every add/update/delete copies entire project. 2853 backups already exist. Causes I/O bottleneck and storage explosion |
| R3 | Float for money | **HIGH** | IEEE 754 rounding causes silent errors in payment remaining calculations |
| R4 | E2E phase1b2 hang | **HIGH** | Cannot validate cross-entity flows; blocks release gate |
| R5 | Sequential ID generation | **HIGH** | Scans ALL rows to find max ID. Race condition under concurrency |
| R6 | Name-based entity linking | **HIGH** | Bookings linked by customer_name/service name. Fragile despite propagation logic |
| R7 | `logic.py` monolith | **MEDIUM** | 1142 lines = high regression risk on any change |
| R8 | `e2e_playwright.py` monolith | **MEDIUM** | 1489 lines, untestable test code |
| R9 | Legacy SHA256 hashes | **MEDIUM** | Linger until user actually logs in |
| R10 | No unit tests | **MEDIUM** | Business logic has zero automated test coverage |
| R11 | Mixed line endings | **LOW** | Diff noise, potential encoding issues |
| R12 | `table_content/dresses.py` 67KB | **LOW** | Maintenance burden |

---

## Part B: Execution Plan

### Phase Sequence Overview

```
Phase 0: Immediate Safeguards     → Zero behavioral change, close critical risks
Phase 1: E2E Stabilization        → Unblock the test gate
Phase 2: Backup Policy Reform     → Stop the storage/performance bleeding
Phase 3: Financial Precision      → Fix Float→Numeric for money
Phase 4: Referential Integrity    → Name-based → ID-based linking
Phase 5: logic.py Decomposition   → Split monolith into domain services
Phase 6: Unit Test Foundation     → Add automated tests for business logic
Phase 7: Cleanup & Closure        → Dead code removal, docs update, final tag
```

---

### Phase 0: Immediate Safeguards
**Objective:** Close critical risks with zero behavioral change.  
**Files affected:** `app_dash.py`, `.gitignore`  
**Risk level:** Minimal — no logic changes.

**Steps:**
1. Add startup guard: if `APP_ENV=production` and `APP_SECRET_KEY` is the default, refuse to start.
2. Add to `.gitignore`: `backups/`, `releases/`, `atelier.db`, `dress_images/`
3. Remove `backups/` and `releases/` from git index: `git rm -r --cached backups/ releases/` (files stay on disk).

**Exit criteria:** App starts locally. `git status` is clean of backup noise.

**Validation:** py_compile → health_check → HTTP 200

---

### Phase 1: E2E Stabilization
**Objective:** Get full E2E regression to pass reliably.  
**Files affected:** `scripts/e2e_playwright.py`, possibly some layout files (adding `data-testid`).

**Steps:**
1. **Diagnose the phase1b2 hang** — the most likely causes are:
   - A modal not closing before the next action (stale DOM state)
   - A Playwright selector timing out because AG Grid row rendering hasn't completed
   - A callback chain deadlock (circular Output/Input in Dash)
   Add timestamp logging between each step in the customers flow to pinpoint exactly where it hangs.

2. **Fix the hang** — based on diagnosis, apply either:
   - `wait_for_no_modal()` calls between CRUD operations
   - Increased timeout + `page.wait_for_load_state("networkidle")` after saves
   - `data-testid` attributes on buttons/cells that currently use fragile CSS selectors

3. **Validate phase1b2** — must pass 3 consecutive runs without intervention.

4. **Unlock phase1b2b** — extend the test to cover customer→booking→payment dependency chain.

5. **Run full regression** (`FULL_REGRESSION=1 FULL_PHASE=all`) — fix remaining issues in payments/settings/finance/export phases.

6. **Refactor the test script:**
   - Extract `main()` into discrete phase functions
   - Move helpers to `scripts/e2e_helpers.py`
   - Create `CORE_SMOKE=1` mode that runs in <60 seconds

**Exit criteria:** `FULL_REGRESSION=1 FULL_PHASE=all` passes 3 consecutive clean runs.

---

### Phase 2: Backup Policy Reform
**Objective:** Stop full-project backup on every CRUD write.  
**Files affected:** `logic.py` (remove `_backup_before_write` calls), `app/services/backup_service.py`, `app/callbacks/settings_backup.py`

**Steps:**
1. Remove all `_backup_before_write()` calls from add/update/delete functions in `logic.py`. There are approximately 12 call sites (2 per entity × 3 operations + extras).
2. Keep the manual backup button in Settings as-is.
3. Add a lightweight DB-only backup option: just copy `atelier.db` instead of the whole project.
4. Add a daily startup auto-backup: on app start, if no backup exists for today, create one.
5. Add retention: keep only the last 30 backups; delete older on startup.

**Exit criteria:** CRUD operations have no backup I/O. Manual backup still works. Daily auto-backup runs on startup.

**Validation:** py_compile → health_check → HTTP 200 → time a CRUD operation (should be near-instant)

---

### Phase 3: Financial Precision
**Objective:** Replace `Float` with fixed-point for all money fields.  
**Files affected:** `models.py`, `logic.py`

**Steps:**
1. In `models.py`, change `Float` → `Numeric(precision=12, scale=2)` for: `Service.price`, `Booking.price`, `Booking.paid`, `Booking.remaining`, `Payment.amount`, `Payment.remaining_after`.
2. Since SQLite doesn't enforce column types, the ORM change is sufficient. But add explicit `round(x, 2)` or `Decimal` usage in all arithmetic in `logic.py` (especially `add_booking`, `update_booking`, `add_payment`, `update_payment`).
3. Add a health_check assertion: for every booking, verify `remaining == price - paid` within ±0.01.

**Exit criteria:** Health check financial assertion passes. E2E payment flows pass.

---

### Phase 4: Referential Integrity Hardening
**Objective:** Move from name-based to ID-based entity linking.  
**Files affected:** `models.py`, `logic.py`, `app/callbacks/bookings_form.py`

**Steps:**
1. Backfill all NULL `Booking.customer_id` values from `Booking.customer_name` matching.
2. Backfill all NULL `Booking.service_id` values (the `_backfill_booking_service_ids()` function exists but may have gaps).
3. Make `Booking.customer_id` NOT NULL after backfill.
4. Update `add_booking` and `update_booking` to always set `customer_id` and `service_id` from lookups.
5. Add FK constraint for `Booking.dress_code` → `Dress.dress_code`.
6. Add health_check: zero NULL FKs, zero orphaned references.
7. Once IDs are reliable, remove the O(n) name propagation loops in `update_customer` and `update_service`.

**Exit criteria:** Zero NULL FK fields. Zero orphan references. E2E full regression passes.

---

### Phase 5: `logic.py` Decomposition
**Objective:** Split the 1142-line monolith into domain service modules.  
**Files affected:** `logic.py` → new `app/domain/` package

**Steps:**
1. Create `app/domain/` with:
   - `customers.py` — `add_customer`, `update_customer`, `delete_customer`
   - `services.py` — `add_service`, `update_service`, `delete_service`
   - `dresses.py` — `add_dress`, `update_dress`, `delete_dress`, `save_image`
   - `bookings.py` — `add_booking`, `update_booking`, `delete_booking`
   - `payments.py` — `add_payment`, `update_payment`, `delete_payment`
   - `auth.py` — `hash_password`, `verify_password`, `check_users`, `save_users_data`, `_bootstrap_admin_if_enabled`
   - `departments.py` — `check_departments`, `add_department`, `update_department`, `delete_department`
   - `data_loader.py` — `load_data`, column mappings

2. Move functions ONE DOMAIN AT A TIME. After each move:
   - Keep a re-export in `logic.py`: `from app.domain.customers import add_customer, update_customer, delete_customer`
   - Run full validation (py_compile + health_check + E2E smoke)

3. Once all functions are moved, `logic.py` becomes a thin re-exporting facade (<100 lines).

4. Also split `app/callbacks/bookings_form.py` (28KB) into:
   - `bookings_modal.py` — modal open/close logic
   - `bookings_save.py` — save/update/delete handlers
   - `bookings_helpers.py` — dropdown population, validation helpers

**Exit criteria:** `logic.py` < 100 lines (re-exports only). Each domain file < 200 lines. Callback count unchanged. E2E passes.

---

### Phase 6: Unit Test Foundation
**Objective:** Add automated tests for business logic.  
**Files affected:** New `tests/` directory

**Steps:**
1. Create `tests/conftest.py` with in-memory SQLite fixture.
2. Write tests for each domain:
   - Add/update/delete positive cases
   - Validation rejections (missing fields, duplicate phone, etc.)
   - Referential integrity blocks (can't delete customer with bookings, etc.)
   - Password hash/verify round-trip
3. Add `pytest` to `requirements_dash.txt`.

**Exit criteria:** `pytest tests/ -v` passes. ≥1 positive + 1 negative test per CRUD operation.

---

### Phase 7: Cleanup & Closure
**Objective:** Final hygiene and documentation.  
**Files affected:** Various docs, `.py` files

**Steps:**
1. Remove dead code: `save_data()` (no-op), `save_department()` (trivial wrapper), `_migrate_departments_from_csv()` if CSV doesn't exist.
2. Normalize all `.py` line endings to `\n`.
3. Investigate `table_content/dresses.py` (67KB) — likely contains embedded data or excessive inline image rendering that should be refactored.
4. Update all `docs/` to reflect final architecture.
5. Run full validation gate.
6. Tag git release.

**Exit criteria:** All docs current. No dead code. Full test suite green. Tagged release.

---

### Definition of Done

All of the following must be true simultaneously:

- [ ] `APP_SECRET_KEY` enforced in production mode
- [ ] `.gitignore` excludes `backups/`, `releases/`, `atelier.db`
- [ ] No automatic backup on individual CRUD writes
- [ ] Financial fields use fixed-point precision; `remaining == price - paid` for all bookings
- [ ] All FK relationships populated and enforced; zero orphaned references
- [ ] `logic.py` is a thin facade (<100 lines); domain logic in `app/domain/`
- [ ] E2E full regression passes 3 consecutive runs
- [ ] Unit tests exist for all CRUD and auth operations
- [ ] Documentation reflects actual architecture
- [ ] Repository has no tracked backup/release artifacts

---

## Part C: Governance / Operating Model

### Change Protocol

Every change must follow this cycle:

```
1. Plan the step (identify exactly which 1-2 files change)
2. Implement the change
3. Run validation gates
4. If PASS → commit with descriptive message → proceed
5. If FAIL → revert → diagnose → retry
```

### Mandatory Validation Gates

Run these after EVERY step. No exceptions.

| Gate | Command | Pass Criteria |
|---|---|---|
| 1. Syntax | `python -m py_compile app_dash.py logic.py models.py` | Exit code 0 |
| 2. Import check | `python -c "import app_dash; print('callbacks', len(app_dash.app.callback_map))"` | Count matches baseline (record before starting) |
| 3. Health check | `python scripts/health_check.py` | All sections PASS |
| 4. Runtime | `python app_dash.py` + HTTP GET `http://127.0.0.1:8050` | HTTP 200, no console errors |
| 5. E2E smoke | `CORE_SMOKE=1 python scripts/e2e_playwright.py` | Passes (after Phase 1 creates this mode) |
| 6. Full E2E | `FULL_REGRESSION=1 python scripts/e2e_playwright.py` | All phases pass (only when UI flows changed) |
| 7. Unit tests | `pytest tests/ -v` | All tests pass (after Phase 6) |

### Evidence Artifacts

Each step should produce:

| Artifact | Format | Where |
|---|---|---|
| Validation output | Text log | `logs/validation_<phase>_<step>_<timestamp>.txt` |
| Health check result | Script output | `logs/health_<timestamp>.txt` |
| E2E screenshots | PNG files | `logs/e2e_<timestamp>/` |
| Git commit | Message referencing phase/step | Git history |

### Rollback Strategy

| Scenario | Action |
|---|---|
| Single step fails | `git checkout -- <modified files>` |
| Multiple commits bad | `git revert <commit-range>` (preserves history) |
| DB schema broken | Restore `atelier.db` from latest backup in `backups/` |
| Full rollback | Restore from latest release zip in `releases/` |

### Risk Control Rules

1. **Never change `logic.py` and a callback file in the same commit.** Isolate business logic changes from UI behavior changes.
2. **Record the callback count baseline before starting any work.** If `len(app.callback_map)` changes unexpectedly, investigate.
3. **Always test DB migrations on a COPY of `atelier.db` first.** Never run untested ALTER TABLE on the live database.
4. **Tag a git release before starting each phase.** Enables clean rollback.
5. **One domain at a time during decomposition.** Never move two domains in the same session.

---

## Part D: My Recommendations — What I Would Actually Do

### Priority Order Rationale

I've ordered the phases based on **risk-adjusted impact**:

1. **Phase 0 first** because the default secret key and `.gitignore` gaps can be fixed in 10 minutes with zero risk of breaking anything. There's no reason to leave critical risks open while working on harder things.

2. **Phase 2 (backup reform) before Phase 1 (E2E)** might seem counterintuitive, but here's why I'd consider it: every time you run E2E tests, the test creates entities, which triggers `_backup_before_write()` up to 20+ times per run. This makes E2E debugging slower and creates noise. **However**, if the E2E hang is truly blocking all other validation, then Phase 1 takes priority to re-establish the test gate. **My recommendation: do Phase 0 → quick Phase 2.1 (just remove the `_backup_before_write` calls) → then Phase 1.** This costs 30 minutes and makes everything after it faster.

3. **Phase 1 (E2E)** is the most critical "real" phase because without stable E2E, you can't verify that later phases don't break the UI. The phase1b2 hang is most likely a **timing issue** — Playwright clicks "Save" on a customer modal, but the modal hasn't fully closed before the next action. The fix is almost certainly adding `wait_for_no_modal()` or `page.wait_for_load_state("networkidle")` between operations. I'd investigate this specific pattern first.

4. **Phase 3 (financial precision)** before Phase 4 because money errors are silent and compounding. The Float→Numeric change in `models.py` is a 5-line edit with almost no behavioral risk on SQLite (which is dynamically typed anyway). The real work is adding `round(x, 2)` in the arithmetic paths, which is ~10 edits in `logic.py`.

5. **Phase 4 (referential integrity)** is the most complex phase and should only happen after E2E is stable (so you can verify it) and after backup reform (so you're not creating 50 backups while testing migrations).

6. **Phase 5 (decomposition)** and **Phase 6 (unit tests)** are structural improvements that don't fix bugs. They make the codebase more maintainable for future changes. I'd tackle them together: extract one domain to `app/domain/`, immediately write unit tests for it, then move to the next domain. This way each domain has tests from the moment it's extracted.

### What I Would NOT Do

1. **Don't try to fix everything at once.** The temptation is to rewrite `logic.py`, fix the schema, and stabilize E2E in one big pass. This will fail. The code works today. Each change must preserve that.

2. **Don't switch to Postgres right now.** `models.py` has `DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///atelier.db")` which shows someone was thinking about it, but the app has SQLite-specific code (`PRAGMA table_info`). The migration would be premature and high-risk.

3. **Don't rewrite the E2E test from scratch.** It's tempting because it's 1489 lines of spaghetti, but it's the only functional regression test that exists. Refactor it incrementally (extract helpers, split `main()`), don't rewrite it.

4. **Don't add a migration framework (Alembic) for SQLite.** SQLite ALTER TABLE is limited anyway. For Phase 3 and 4, manual migrations with backup+restore are simpler and less risky. Consider Alembic only if/when you move to Postgres.

### Specific Technical Opinions

**On the `_backup_before_write` pattern:**  
This was clearly added as a safety net during rapid development, and it served its purpose — you have 2853 restore points. But it's now technical debt. The correct pattern is: manual backup button + daily auto-backup on startup + backup before destructive operations only (delete, not add/update).

**On `logic.py`:**  
The facade pattern (keeping `logic.py` as re-exports) is the right approach during decomposition. It means you can move functions one at a time without updating every caller. After all functions are moved, you can update callers to import directly from `app/domain/` and eventually remove the facade.

**On the 67KB `table_content/dresses.py`:**  
This is almost certainly containing embedded Base64 image data or very large column definitions with inline rendering logic. A 67KB Python file for table rendering is abnormal. It should be investigated and refactored, but it's not blocking anything — put it in Phase 7.

**On the E2E hang:**  
Based on the code structure, `e2e_playwright.py` uses a `wait_modal_open()` function and various `safe_click()` retries. The phase1b2 hang after "customers" step likely means a modal is left open (or an alert is shown) that blocks the next navigation. The diagnostic approach is:
1. Add `print(f"[{time.time()}] Before step X")` markers
2. Add `page.screenshot(path=f"debug_{step}.png")` before/after each major action  
3. Check if a `dbc.Alert` is covering the nav buttons

**On the ID generation race condition:**  
The current pattern (`for c in session.query(Customer).all(): find max ID`) works for a single-user app. If concurrency is ever needed, the fix is simple: use a DB sequence or `SELECT MAX() + 1` in a single atomic transaction. But this is low priority since the app is currently single-user.

---

## Summary Table for Quick Reference

| What | Where | Lines/Size | Health |
|---|---|---|---|
| Entrypoint | `app_dash.py` | 130 lines | ✅ |
| App factory | `app/bootstrap.py` | 20 lines | ✅ |
| DI wiring | `app/composition/wiring.py` | 88 lines | ✅ |
| Callback hub | `app/callbacks/register_all.py` | 140 lines | ✅ |
| Auth callbacks | `app/callbacks/auth.py` | 96 lines | ✅ |
| Bookings callback | `app/callbacks/bookings_form.py` | 28KB | ⚠️ Split needed |
| Business logic | `logic.py` | 1142 lines | ⚠️ Monolith |
| ORM models | `models.py` | 105 lines | ✅ (schema issues) |
| Health check | `scripts/health_check.py` | 310 lines | ✅ |
| E2E tests | `scripts/e2e_playwright.py` | 1489 lines | ⚠️ Monolith, phase1b2 hangs |
| Backup service | `app/services/backup_service.py` | 100 lines | ⚠️ Full-copy pattern |
| Table: dresses | `app/table_content/dresses.py` | 67KB | 🔴 Investigate |
| Constants | `app/constants.py` | 16 lines | ✅ |
| Database | `atelier.db` | 229KB | ✅ |
| Backups | `backups/` | 2853 items | 🔴 Bloat |
| Releases | `releases/` | 60 items | 🔴 Bloat |
