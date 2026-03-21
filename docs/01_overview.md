# MyAtelier — نظام إدارة الأتيليه
## Application Overview & Introduction

---

## 1. What Is MyAtelier?

**MyAtelier** is a full-featured **Arabic-language atelier (bridal studio) management system** built with [Plotly Dash](https://dash.plotly.com/) + Flask. It runs entirely in the browser and is designed to be deployed as a local application or on a server.

The application manages the complete workflow of a bridal atelier business:

| Module | Arabic Name | Purpose |
|---|---|---|
| **Finance Dashboard** | التقارير المالية | Revenue KPIs and charts |
| **Bookings** | الحجوزات | Customer event bookings |
| **Customers** | العملاء | Bride & groom registry |
| **Services** | الخدمات | Service catalog by department |
| **Dresses** | الفساتين | Dress inventory with photos |
| **Payments** | المدفوعات | Payment tracking per booking |
| **Settings** | الإعدادات | Departments, company name, backups |
| **Users** | المستخدمين / حسابي | Admin user management + self-service account editing |

---

## 2. Key Features

- **Role-aware users screen**: `admin` users manage all accounts; regular `user` accounts see only their own profile and can update their name/password.
- **Secure login**: PBKDF2-SHA256 password hashing with automatic upgrade from legacy SHA-256.
- **Real-time search**: Every module has a live `Dropdown`-style search bar.
- **Modal-based CRUD**: Add / Edit / Delete via pop-up dialogs — no page reloads.
- **Data tables**: Powered by `dash-ag-grid` with pagination (10 rows/page) and column filters.
- **Finance charts**: Plotly bar/pie charts for daily income, income by department, and top services.
- **Dress image management**: Upload and serve dress photos via Flask static route.
- **Backup system**: One click creates a full snapshot, builds a ZIP archive, and downloads the ZIP in the browser.
- **Responsive UI**: Sidebar navigation for desktop, bottom navigation bar for mobile.
- **In-memory data cache**: 2-second TTL cache on DB reads to reduce latency.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Web Framework** | Plotly Dash 2.x (built on Flask) |
| **UI Components** | Dash Bootstrap Components (`dbc.themes.LITERA`) |
| **Data Grid** | `dash-ag-grid` |
| **Charts** | Plotly Express |
| **Database ORM** | SQLAlchemy |
| **Database** | SQLite (default) / PostgreSQL (via `DATABASE_URL` env var) |
| **Data Processing** | Pandas |
| **Image Handling** | Pillow |
| **Export** | openpyxl (Excel) |
| **Testing** | pytest + pytest-cov |
| **Icons** | Bootstrap Icons 1.10.5 (CDN) |

---

## 4. Application Version

`APP_VERSION = "2.01"` — defined in `app/constants.py`.

---

## 5. Language & Locale

The entire UI is in **Arabic (RTL)**. All user-facing labels, error messages, and column headers are defined as Arabic strings (UTF-8 encoded). Column names are translated from English DB field names to Arabic display names via the `*_COLS_MAP` dictionaries in `app/domain/data_access.py`.

---

## 6. Directory Map

```
MyAtelier/
├── app_dash.py              ← Application entry point
├── logic.py                 ← Public business logic facade
├── models.py                ← SQLAlchemy ORM models + DB engine
├── requirements_dash.txt    ← Python dependencies
├── atelier.db               ← SQLite database file
├── dress_images/            ← Uploaded dress photos
├── backups/                 ← Snapshot folders created by manual backup
├── releases/                ← Downloadable ZIP backup archives
├── assets/
│   └── custom.css           ← Custom styles
├── app/
│   ├── bootstrap.py         ← Dash app factory
│   ├── constants.py         ← All app-wide constants & Arabic messages
│   ├── text_utils.py        ← normalize_code(), delete_reason()
│   ├── callbacks/           ← All Dash callback functions
│   ├── composition/         ← Dependency wiring (DI)
│   ├── domain/              ← Business logic, DB access, migrations
│   ├── layouts/             ← UI layout functions per module
│   ├── services/            ← (Reserved for future service wrappers)
│   ├── table_content/       ← Table builder factories
│   └── ui/
│       └── grid.py          ← build_data_table() function
├── docs/                    ← Documentation (this folder)
├── scripts/                 ← Utility & testing scripts
└── tests/                   ← pytest unit tests
```
