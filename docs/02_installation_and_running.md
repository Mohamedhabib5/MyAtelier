# MyAtelier — Installation & Running Guide

---

## 1. Prerequisites

| Requirement | Minimum Version |
|---|---|
| Python | 3.9+ |
| pip | Latest |
| OS | Windows / Linux / macOS |

> **Note**: The app is primarily tested and used on Windows.

---

## 2. Installation Steps

### Step 1 — Clone or Download the Project

Place the project folder at any path, e.g.:
```
D:\Programing project\MyAtelier\
```

### Step 2 — Create a Virtual Environment (Recommended)

```bash
cd "D:\Programing project\MyAtelier"
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements_dash.txt
```

This installs:
- `dash` — web framework
- `dash-bootstrap-components` — UI theme & layout components
- `dash-ag-grid` — data grid tables
- `pandas` — data manipulation
- `plotly` — interactive charts
- `openpyxl` — Excel export
- `Pillow` — image processing for dress photos
- `sqlalchemy` — ORM for SQLite/PostgreSQL
- `psycopg2-binary` — PostgreSQL driver (optional, only needed if using Postgres)
- `pytest`, `pytest-cov` — for running tests

---

## 3. Environment Variables (`.env` / System)

Create a `.env` file in the project root (see `.env.example` for reference):

| Variable | Default | Description |
|---|---|---|
| `APP_SECRET_KEY` | `myatelier-dev-secret-change-me` | Flask session secret — **must be changed in production** |
| `APP_ENV` | `development` | Set to `production` or `prod` to enable security checks |
| `APP_DEBUG` | `1` | `1`=debug mode enabled, `0`=disabled |
| `APP_RELOADER` | `0` | `1`=enable Flask hot-reload (useful in dev only) |
| `DATABASE_URL` | `sqlite:///atelier.db` | Database connection string — override for PostgreSQL |
| `APP_BOOTSTRAP_ADMIN` | `0` | Set to `1` to auto-create an admin on first run |
| `APP_BOOTSTRAP_ADMIN_USER` | `admin` | Username for bootstrap admin |
| `APP_BOOTSTRAP_ADMIN_PASSWORD` | *(empty)* | Must be ≥10 chars with upper, lower, digit |
| `APP_BOOTSTRAP_ADMIN_FULL_NAME` | `Administrator` | Display name for bootstrap admin |

> **Security Warning**: In production, always set a strong `APP_SECRET_KEY` and set `APP_ENV=production`. The app will raise a `RuntimeError` at startup if a weak key is used in production mode.

---

## 4. Running the Application

### Development Mode (Default)

```bash
python app_dash.py
```

The app starts at: **http://localhost:8050**

### Production Mode

```bash
set APP_ENV=production
set APP_SECRET_KEY=your-very-long-secret-key-here
set APP_DEBUG=0
python app_dash.py
```

Or use a proper WSGI server:
```bash
pip install gunicorn          # Linux/macOS
gunicorn app_dash:server       # The Flask server object is exported as `server`
```

On Windows with waitress:
```bash
pip install waitress
waitress-serve --port=8050 app_dash:server
```

---

## 5. First Login

When the app starts for the first time with no users in the database, a **default admin account** is automatically created:

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> ⚠️ **Change this password immediately** after first login via the **Users** panel. This seed happens once for a new empty database; after that, changing the admin username or password does not recreate `admin` again.

---

## 6. Database Initialization

On startup, `logic.init_folders()` automatically:

1. Creates the `dress_images/` directory if missing
2. Creates all database tables (`models.Base.metadata.create_all`)
3. Runs schema migrations (adds new columns if upgrading from older version)
4. Backfills data (service IDs, department names, money precision)
5. Seeds the default admin user once when the users table is empty

No manual database setup is needed.

---

## 7. Using PostgreSQL Instead of SQLite

Set the `DATABASE_URL` environment variable:

```bash
set DATABASE_URL=postgresql://user:password@localhost/atelier_db
```

The SQLAlchemy ORM is database-agnostic; all models work with PostgreSQL without code changes.

> **Note**: `psycopg2-binary` must be installed (already in `requirements_dash.txt`).

---

## 8. Running Tests

```bash
pytest tests/ -v
```

With coverage report:
```bash
pytest tests/ --cov=app --cov=logic --cov-report=term-missing
```

Available test files:
- `test_auth_logic.py` — login/password tests
- `test_customers_logic.py` — customer CRUD tests
- `test_payments_logic.py` — payment logic tests
- `test_booking_payment_integration.py` — booking+payment integration
- `test_constitution_lint.py` — architecture invariant checks
- `test_root_feedback_policy.py` — feedback message policy tests

### Running Health Check Script

```bash
python scripts/health_check.py
```

### Running E2E Tests (Playwright)

```bash
python scripts/e2e_playwright.py
```

> Requires `playwright` to be installed separately: `pip install playwright && playwright install chromium`

---

## 9. Creating a Backup

From the UI: **Settings → النسخ الاحتياطي → إنشاء وتنزيل نسخة احتياطية**

This creates:
- a timestamped snapshot folder under `backups/`
- a timestamped `.zip` archive under `releases/`
- an immediate browser download of that ZIP archive

From the command line:
```bash
python scripts/backup_restore_smoke.py
```
