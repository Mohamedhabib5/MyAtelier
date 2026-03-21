# MyAtelier Documentation Index

Welcome to the complete documentation for **MyAtelier — نظام إدارة الأتيليه**.

---

## 📋 Document List

| # | Document | Audience | Description |
|---|---|---|---|
| [01](01_overview.md) | **Application Overview** | Everyone | What the app is, key features, tech stack, directory map |
| [02](02_installation_and_running.md) | **Installation & Running** | Developers / Admins | Setup, environment vars, running, testing, backup |
| [03](03_architecture.md) | **Architecture & Code Structure** | Developers | Layers, data flow, auth flow, caching, navigation |
| [04](04_data_model.md) | **Database & Data Model** | Developers | All tables, ERD, column mapping, migrations, financial logic |
| [05](05_user_guide.md) | **User Guide (دليل المستخدم)** | End Users | How to use every module: login, bookings, customers, etc. |
| [06](06_developer_reference.md) | **Developer Reference** | Developers | Adding modules, API reference, callback patterns, testing |

---

## Current vs Historical Docs

Use these as the current source of truth:
- `docs/01_overview.md`
- `docs/02_installation_and_running.md`
- `docs/03_architecture.md`
- `docs/04_data_model.md`
- `docs/05_user_guide.md`
- `docs/06_developer_reference.md`

Treat these as historical or planning artifacts:
- `docs/technical_report_and_execution_plan.md`
- `docs/execution_plan_final.md`
- `docs/architecture_remediation_master_plan.md`
- `docs/codex_plan.md`

If a historical document conflicts with the current app behavior, follow the current docs above and the live code.

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements_dash.txt

# 2. Run the app
python app_dash.py

# 3. Open browser
http://localhost:8050

# 4. First-time login
Username: admin
Password: admin123
```

> The default `admin / admin123` account is created only on the first run of a new empty database.

---

## 🗂️ App Modules Summary

| Module | Arabic | Function |
|---|---|---|
| Finance Dashboard | الرئيسية | KPIs + charts |
| Bookings | الحجوزات | Event bookings management |
| Customers | العملاء | Bride/groom registry |
| Services | الخدمات | Service catalog |
| Dresses | الفساتين | Dress inventory + photos |
| Payments | المدفوعات | Payment tracking |
| Settings | الإعدادات | Config + backup + departments |
| Users | المستخدمين / حسابي | Admin user management + self account editing |

---

## 🔗 Related Files

- [`logic.py`](../logic.py) — Business logic facade (main API)
- [`models.py`](../models.py) — Database ORM models
- [`app_dash.py`](../app_dash.py) — Application entry point
- [`app/constants.py`](../app/constants.py) — All Arabic strings & constants
- [`requirements_dash.txt`](../requirements_dash.txt) — Python dependencies
- [`.env.example`](../.env.example) — Environment variable template
