# MyAtelier — Architecture & Code Structure

---

## 1. High-Level Architecture

```
Browser (Dash SPA)
       │
       │  HTTP / WebSocket (Dash protocol)
       ▼
┌─────────────────────────────────────────┐
│           app_dash.py (Flask/Dash)      │  ← Entry Point
│  ┌─────────────────────────────────────┐│
│  │  app/bootstrap.py (Dash factory)   ││
│  │  app/layouts/*  (UI building)      ││
│  │  app/callbacks/* (Event handlers)  ││
│  │  app/composition/* (DI wiring)     ││
│  └─────────────────────────────────────┘│
│                   │                     │
│         logic.py (Facade API)           │
│                   │                     │
│  ┌─────────────────────────────────────┐│
│  │    app/domain/* (Business Logic)   ││
│  │    ├─ auth, customers, bookings... ││
│  │    ├─ *_facade.py (data ops)       ││
│  │    ├─ logic_*_api.py (action API)  ││
│  │    ├─ data_access.py (DB reads)    ││
│  │    └─ migrations.py (schema mgmt)  ││
│  └─────────────────────────────────────┘│
│                   │                     │
│      models.py (SQLAlchemy ORM)         │
│                   │                     │
│         atelier.db (SQLite)             │
└─────────────────────────────────────────┘
```

---

## 2. Layered Architecture Explanation

### Layer 1: Entry Point — `app_dash.py`

The main file orchestrates startup:
1. Creates the Dash app via `app/bootstrap.py`
2. Configures the Flask secret key and environment checks
3. Registers a Flask route to serve dress images (`/dress_images/<filename>`)
4. Calls `logic.init_folders()` to initialize DB + folders
5. Builds runtime wiring (dependency injection) via `app/composition/wiring.py`
6. Registers all Dash callbacks via `app/callbacks/register_all.py`
7. Sets the root layout (login gate)
8. Starts the Dash dev server

### Layer 2: Bootstrap — `app/bootstrap.py`

Creates the `Dash` app instance with:
- Bootstrap LITERA theme
- Custom CSS (`assets/custom.css`)
- Bootstrap Icons (CDN)
- `suppress_callback_exceptions=True` (needed because layouts are loaded dynamically)

### Layer 3: Logic Facade — `logic.py`

This is the **single public API** for all business operations. The UI callbacks never import from `app/domain` directly — they go through `logic.py`. This provides:
- Session synchronization across domain modules (`_sync_domain_sessionlocal`)
- Cache invalidation after writes (`_invalidate_after_write`)
- All CRUD functions: `add_customer`, `update_booking`, `delete_payment`, etc.
- Auth functions: `hash_password`, `verify_password`, `check_users`, `list_visible_users`, `create_user`, `admin_update_user`, `update_own_profile`
- Data loading: `load_data` (cached pandas DataFrames)
- Column definitions: `C_COLS`, `S_COLS`, `D_COLS`, `B_COLS`, `P_COLS`

### Layer 4: Domain — `app/domain/`

The domain layer is split into three sub-layers:

| Sub-layer | Files | Purpose |
|---|---|---|
| **Data Access Functions** | `bookings.py`, `customers.py`, `dresses.py`, `payments.py`, `services.py`, `settings_departments.py` | Low-level DB read/write (SQLAlchemy sessions) |
| **Facades** | `*_facade.py` | Compositional wrappers — add ID generation, validation |
| **Logic APIs** | `logic_*_api.py` | Action handlers — compose facades + validation + cache invalidation |
| **Shared** | `data_access.py`, `auth.py`, `migrations.py`, `resolvers.py`, `formatting.py` | Cross-cutting: data loading, auth, schema migration, lookups, formatting |

### Layer 5: Layouts — `app/layouts/`

Each module has its own layout function returning a Dash component tree:

| File | Layout Function | Page Section |
|---|---|---|
| `root.py` | `layout_root()` | App shell (dcc.Location, page-content div) |
| `login.py` | `layout_login()` | Login card |
| `main.py` | `layout_main(user_data, ...)` | Sidebar + tabs + content divs |
| `finance.py` | `layout_finance()` | KPI cards + charts |
| `bookings.py` | `layout_bookings(...)` | Booking table + CRUD modals |
| `customers.py` | `layout_customers(...)` | Customer table + CRUD modals |
| `services.py` | `layout_services(...)` | Service table + CRUD modals |
| `dresses.py` | `layout_dresses(...)` | Dress grid + image upload |
| `payments.py` | `layout_payments(...)` | Payments table + CRUD modals |
| `settings.py` | `layout_settings(...)` | Backup, company name, departments |
| `users.py` | `layout_users(user_role="admin")` | Role-aware users management / self-service account screen |

### Layer 6: Callbacks — `app/callbacks/`

All Dash reactive logic. Each module has separate files for:
- `*_form.py` — Add/Edit/Delete modal callbacks
- `*_search.py` — Live search dropdown callback

| Callback File | Handles |
|---|---|
| `auth.py` | Login, logout, session display, modal resets |
| `navigation.py` | Sidebar tab switching (clientside) |
| `finance.py` | KPI + chart data loading |
| `bookings_form.py` | Add/edit/delete booking |
| `bookings_search.py` | Booking search dropdown |
| `customers_form.py` | Add/edit/delete customer |
| `customers_search.py` | Customer search dropdown |
| `services_form.py` | Add/edit/delete service |
| `services_search.py` | Service search dropdown |
| `dresses_form.py` | Add/edit/delete dress + image upload |
| `dresses_search.py` | Dress search dropdown |
| `payments_form.py` | Add/edit/delete payment |
| `payments_search.py` | Payment search dropdown |
| `settings_backup.py` | Backup creation + direct ZIP download + folder open |
| `settings_departments.py` | Department CRUD |
| `users.py` | Admin user management + regular-user self profile editing |
| `details_actions.py` | View-details modal (customer bookings, payment details, etc.) |
| `export.py` | Excel/CSV export |
| `feedback.py` | Toast/alert feedback messages |

### Layer 7: Composition — `app/composition/`

Dependency injection without a DI framework. `wiring.py` builds all composites:
- Creates `create_dt` (data table factory)
- Creates `table_content_builders` (one per entity)
- Creates `main_layout` (closure with all dependencies injected)
- Returns a dictionary of all runtime-wired components

---

## 3. Data Flow: A Complete Example (Adding a Booking)

```
User fills booking form → clicks "تأكيد الحجز"
        │
        ▼
  Dash callback: register_bookings_form_callbacks → btn-save-booking n_clicks
        │
        ▼
  Validates inputs (price > 0, event_date exists, etc.)
        │
        ▼
  logic.add_booking(customer_name, dept, service, dress_code, ...)
        │
        ├─ resolvers_domain.find_customer_by_name_or_id(session, ...)
        ├─ resolvers_domain.find_service_by_name_or_id(session, ...)
        ├─ bookings_facade_domain.add_booking(session, booking_obj)
        │     └─ auto-generates booking_id (e.g. "HR-123456")
        │     └─ calculates remaining = price - paid
        ├─ logic.add_payment(...) ← auto-records down-payment if paid > 0
        └─ _invalidate_after_write() ← clears "bookings" and "payments" cache
        │
        ▼
  Callback refreshes table: get_bookings_table_content()
        │
        ▼
  load_data("bookings.csv") → DB query → Pandas DataFrame → ag-Grid table
        │
        ▼
  UI updates: modal closes, table refreshed, alert shows "تمت الإضافة"
```

---

## 4. Session & Authentication Flow

```
App root layout: layout_root()
  └── dcc.Location (URL tracking)
  └── dcc.Store id="user_session_store" (client-side session token)
  └── html.Div id="page-content" (swapped based on auth state)

On page load:
  display_page() callback fires:
    └── Checks Flask server-side session (flask.session["logged_in"])
    └── If not logged in → returns login_layout
    └── If logged in → returns main_layout(user_data)

On login button click:
  login() callback:
    └── Queries users DB
    └── Verifies password (PBKDF2 or legacy SHA-256)
    └── Auto-upgrades SHA-256 hashes to PBKDF2
    └── Sets flask.session["logged_in"], ["role"], etc.
    └── Sets dcc.Store user_session_store = {logged_in: True, login_ts: ...}

On logout:
  logout() callback:
    └── Clears flask.session
    └── Sets user_session_store = None
    └── display_page() fires → returns login_layout
```

---

## 5. Caching Strategy

The app uses a simple in-memory dict cache (`DATA_CACHE`) with a **2-second TTL**:

```python
CACHE_TTL_SECONDS = 2.0
DATA_CACHE = {}  # { "bookings": (timestamp, DataFrame) }
```

- **Cache hit**: Returns a copy of the cached DataFrame (fast)
- **Cache miss**: Queries the DB, stores result with timestamp
- **Invalidation**: After any write operation, `invalidate_data_cache(file_name)` removes the relevant cache key

---

## 6. ID Generation Patterns

| Entity | ID Format | Example |
|---|---|---|
| Customer | `C-<seq>` | `C-101` |
| Service | `S-<seq>` | `S-205` |
| Dress | User-defined code | `DR-001` |
| Booking | `<dept_code>-<random6>` | `HR-432198` |
| Payment | `PAY-<random6>` | `PAY-876543` |

Department codes for bookings:
```python
BOOKING_DEPT_MAP = {
    "المكياج": "MK",
    "التصوير": "PH",
    "الشعر": "HR",
    "البشرة": "SK",
    "الفساتين": "DR",
}
```

---

## 7. Navigation Architecture

The app uses **hidden tabs** for navigation, not URL routing:

```
Main layout has:
  dbc.Tabs (display: none) — these are never shown visually
  html.Div id="tab-content" containing:
    - view-finance   (display: block by default)
    - view-bookings  (display: none)
    - view-customers (display: none)
    - ...etc

Sidebar nav link clicks → update active_tab on dbc.Tabs
  → clientside JS callback toggles which view-* div is visible
```

This approach renders ALL tab content **once on login** (not lazy) but uses CSS show/hide for instant switching.
