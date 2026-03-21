# MyAtelier System Update Manual

Version: 2.01  
Date: 2026-02-21

## 1) Purpose
This document explains how the system is built, where each type of logic lives, and how to make safe updates without breaking existing behavior.

## 2) High-Level Architecture
The app follows layered architecture:

1. `app_dash.py`
- Application entrypoint.
- Creates Dash app/server.
- Initializes folders and DB bootstrap through `logic.init_folders()`.
- Builds runtime wiring and registers all callbacks.

2. `app/composition/*`
- Dependency wiring and composition layer.
- `wiring.py` builds table-content factories and `main_layout`.
- Keeps cross-feature plumbing in one place.

3. `app/layouts/*` + `app/table_content/*` + `app/ui/grid.py`
- UI structure and rendered table components.
- Should stay presentation-focused.

4. `app/callbacks/*`
- User interaction/event handling.
- Reads/writes through `logic.py` API (instead of embedding DB logic directly).

5. `logic.py` + `models.py`
- Core business rules and data access.
- SQLAlchemy models and DB session lifecycle.

## 3) Core Files And Responsibilities
`app_dash.py`
- Bootstraps app and Flask route for `dress_images/`.
- Binds all runtime services/layouts/callbacks.

`models.py`
- Defines entities: `User`, `Department`, `Customer`, `Service`, `Dress`, `Booking`, `Payment`.
- Configures `engine`, `SessionLocal`, `init_db()`.

`logic.py`
- Central business API used by callbacks.
- Validation rules, migration/backfill helpers, CRUD operations.
- Maintains dependent updates (example: payment updates booking paid/remaining).

`app/callbacks/register_all.py`
- Single registration point for all callback modules.
- New callback modules should be registered here.

`assets/custom.css`
- Shared visual styling.
- Keep structural logic out of CSS.

## 4) Runtime Flow (Request To Persistence)
1. User action in UI triggers a callback in `app/callbacks/*`.
2. Callback calls a function from `logic.py`.
3. `logic.py` validates rules and updates entities using SQLAlchemy (`models.py`).
4. Callback refreshes table/content output for the affected view.

## 5) Business-Logic Rules You Must Preserve
`logic.py` currently enforces important invariants:

- Money values normalized to 2 decimals (`_money`, `_normalize_money_precision`).
- Booking payment constraints:
  - paid cannot exceed booking price.
  - payment cannot exceed booking remaining.
- Referential safety:
  - cannot delete customer/service/dress when linked bookings exist.
  - cannot delete booking with linked payments.
- Dress booking collision:
  - same dress code cannot be booked for the same event date.
- Backward compatibility:
  - migration/backfill helpers keep legacy records usable.

## 6) Authentication And Users
- Password verification is in `logic.verify_password`.
- Password hashing supports modern PBKDF2 hash flow and legacy compatibility path.
- Bootstrap/default admin checks run during initialization (`init_folders` path).

## 7) Data Model Relationship Notes
- `Booking.customer_id` -> `Customer.customer_id` (nullable legacy-safe link).
- `Booking.service_id` -> `Service.service_id` (nullable legacy-safe link).
- `Payment.booking_id` -> `Booking.booking_id`.
- `Booking` also stores display copies (`customer_name`, `service`) for compatibility with existing UI/data flows.

## 8) Where To Edit By Change Type
UI layout change:
- Edit `app/layouts/<feature>.py` and maybe `assets/custom.css`.

Table rendering change:
- Edit `app/table_content/<feature>.py` and/or `app/ui/grid.py`.

Interaction behavior change:
- Edit the corresponding module in `app/callbacks/`.

Business rule or DB write behavior change:
- Edit `logic.py` (and `models.py` only if schema truly changes).

Cross-feature wiring/runtime composition:
- Edit `app/composition/wiring.py` or `app/composition/layout_factory.py`.

## 9) Safe Update Workflow
1. Define one small objective.
2. Touch minimum files required.
3. Keep Arabic labels/messages unchanged unless explicitly requested.
4. Run required validation after each change:
   - `python -m py_compile app_dash.py logic.py models.py`
   - `python app_dash.py` and verify `http://127.0.0.1:8050`
   - `python scripts/health_check.py`
   - If UI flow changed: targeted checks or `python scripts/e2e_playwright.py`
5. Document what changed and risk impact.

## 10) Current Version Stamp
- System version constant: `app/constants.py` -> `APP_VERSION = "2.01"`
- Manual/document version: this file is stamped `2.01`.

## 11) Quick Orientation For New Maintainers
1. Start at `app_dash.py` to understand startup flow.
2. Open `app/callbacks/register_all.py` to map feature behavior modules.
3. Use `logic.py` as source of truth for business rules.
4. Use `models.py` for schema/relations.
5. Validate every small change with syntax + app run + health check.
