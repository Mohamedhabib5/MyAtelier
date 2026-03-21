# MyAtelier — Developer Reference

This document is for developers who want to understand or extend the application.

---

## 1. Adding a New Module (End-to-End Example)

Suppose you want to add a new "Reports Archive" module. Follow these steps:

### Step 1 — Add the Model (if new table needed)
Edit `models.py`:
```python
class ReportArchive(Base):
    __tablename__ = "report_archives"
    report_id = Column(String, primary_key=True)
    title = Column(String)
    created_date = Column(String)
    content = Column(String)
```

### Step 2 — Add Domain Logic
Create `app/domain/reports.py` with SQLAlchemy session functions.
Create `app/domain/reports_facade.py` for ID generation + data ops.
Create `app/domain/logic_reports_api.py` for action handlers.

### Step 3 — Expose via `logic.py`
Add a function to `logic.py`:
```python
from app.domain import reports_facade as reports_facade_domain
from app.domain import logic_reports_api as logic_reports_api_domain

def add_report(title, content):
    return logic_reports_api_domain.add_report(
        reports_facade_domain,
        _with_synced_sessionlocal,
        reports_domain,
        _invalidate_after_write,
        title=title,
        content=content,
        ...
    )
```

### Step 4 — Create the Layout
Create `app/layouts/reports.py`:
```python
def layout_reports():
    return html.Div([
        html.H3("أرشيف التقارير"),
        ...
    ])
```

Add to `app_dash.py`:
```python
from app.layouts.reports import layout_reports
```

### Step 5 — Create Callbacks
Create `app/callbacks/reports_form.py` and `app/callbacks/reports_search.py`.

### Step 6 — Register Callbacks
Add to `app/callbacks/register_all.py`:
```python
from app.callbacks.reports_form import register_reports_form_callbacks
# ...in register_all_callbacks():
register_reports_form_callbacks(app, ...)
```

### Step 7 — Add Navigation
Add a nav link in `app/layouts/main.py`:
```python
dbc.NavLink([html.I(className="bi bi-archive"), "التقارير"],
    href="#", id="nav-reports", n_clicks=0, className="nav-link"),
```

And a corresponding view div:
```python
html.Div(layout_reports(), id="view-reports", style={"display": "none"}),
```

---

## 2. Constants Reference (`app/constants.py`)

All string constants are centrally defined here. **Never** hardcode Arabic strings in callbacks or layouts.

### Department Names (Arabic)
```python
DEPT_MAKEUP  = "المكياج"
DEPT_PHOTO   = "التصوير"
DEPT_HAIR    = "الشعر"
DEPT_SKIN    = "البشرة"
DEPT_DRESSES = "الفساتين"
NO_DRESS_LABEL = "بدون فستان"
```

### Status Messages
```python
MSG_ADDED    = "تمت الإضافة"
MSG_UPDATED  = "تم التعديل"
MSG_DELETED  = "تم الحذف"
MSG_NOT_FOUND     = "غير موجود"
MSG_ALREADY_EXISTS = "موجود بالفعل"
MSG_MISSING_INFO  = "الرجاء إدخال البيانات"
MSG_IN_USE        = "مرتبط ببيانات أخرى"
MSG_INVALID_PHONE = "رقم الهاتف غير صحيح"
MSG_PHONE_USED_BY_ANOTHER = "رقم الهاتف مستخدم لعميل آخر"
MSG_HAS_BOOKINGS  = "لديه حجوزات"
MSG_CODE_EXISTS   = "الكود موجود بالفعل"
MSG_NEW_CODE_EXISTS = "الكود الجديد موجود بالفعل"
MSG_INVALID_VALUE = "❌ قيمة غير صحيحة"
MSG_PAID_GT_PRICE = "❌ المبلغ المدفوع أكبر من السعر"
MSG_PAYMENT_GT_REMAINING = "❌ الدفعة أكبر من المتبقي"
MSG_DRESS_BOOKED_SAME_DATE = "الفستان محجوز بهذا التاريخ"
```

### Booking Action Labels (used in details modals)
```python
PAYMENTS_ACTION_LABEL         = "تفاصيل الدفعات"
CUSTOMER_BOOKINGS_ACTION_LABEL = "تفاصيل الحجوزات"
DRESS_BOOKINGS_ACTION_LABEL   = "تفاصيل الحجوزات"
PAYMENT_BOOKING_ACTION_LABEL  = "تفاصيل الحجز"
```

---

## 3. Data Column Constants

Defined in `app/domain/data_access.py`. These are the **Arabic** DataFrame column names used throughout the app.

```python
C_COLS = ["كود العميل", "تاريخ التسجيل", "اسم العروسه", "اسم العريس",
          "العنوان", "تليفون 1", "تليفون 2", "ملاحظات"]

S_COLS = ["كود الخدمة", "القسم", "اسم الخدمة", "السعر المقترح"]

D_COLS = ["كود الفستان", "نوع الفستان", "تاريخ الشراء", "وصف الفستان",
          "صورة الفستان", "حالة الفستان"]

B_COLS = ["كود الحجز", "تاريخ الحجز", "اسم العروسه", "القسم", "الخدمة",
          "كود الفستان", "تاريخ المناسبة", "السعر المتفق", "المدفوع",
          "المتبقي", "ملاحظات الحجز", "حالة الحجز"]

P_COLS = ["كود الدفع", "التاريخ", "كود الحجز", "القيمة المدفوعة",
          "اسم العروسه", "اسم العريس", "المتبقي بعد الدفعة", "ملاحظات الدفع"]
```

---

## 4. `logic.py` Public API Reference

All functions available at the `logic` module level:

### Data Loading
| Function | Returns | Description |
|---|---|---|
| `logic.load_data(file_name, columns=None)` | `pd.DataFrame` | Load a cached entity DataFrame. `file_name` is one of `"customers"`, `"services"`, `"dresses"`, `"bookings"`, `"payments"` |

### Customer Operations
| Function | Returns |
|---|---|
| `logic.add_customer(name, groom, phone1, phone2, address, reg_date, notes)` | `(bool, str)` |
| `logic.update_customer(c_id, name, groom, phone1, phone2, address, reg_date, notes)` | `(bool, str)` |
| `logic.delete_customer(c_id)` | `(bool, str)` |

### Service Operations
| Function | Returns |
|---|---|
| `logic.add_service(name, dept, price)` | `(bool, str)` |
| `logic.update_service(s_id, name, dept, price)` | `(bool, str)` |
| `logic.delete_service(s_id)` | `(bool, str)` |

### Dress Operations
| Function | Returns |
|---|---|
| `logic.add_dress(code, d_type, date_buy, status, desc, image_contents)` | `(bool, str)` |
| `logic.update_dress(old_code, new_code, d_type, date_buy, status, desc, image_contents)` | `(bool, str)` |
| `logic.delete_dress(d_code)` | `(bool, str)` |
| `logic.save_image(image_contents, dress_code)` | None |

### Booking Operations
| Function | Returns |
|---|---|
| `logic.add_booking(customer_name, dept, service, dress_code, event_date, price, paid, status, notes, reg_date)` | `(bool, str)` |
| `logic.update_booking(b_id, customer_name, dept, service, dress_code, event_date, price, paid, status, notes)` | `(bool, str)` |
| `logic.delete_booking(b_id)` | `(bool, str)` |

### Payment Operations
| Function | Returns |
|---|---|
| `logic.add_payment(booking_id, amount, bride_name, groom_name, notes, date_val, session, commit)` | `(bool, str)` |
| `logic.update_payment(p_id, booking_id, amount, notes, date_val)` | `(bool, str)` |
| `logic.delete_payment(p_id)` | `(bool, str)` |

### Department Operations
| Function | Returns |
|---|---|
| `logic.check_departments()` | `pd.DataFrame` |
| `logic.add_department(name)` | `(bool, str)` |
| `logic.update_department(old_name, new_name)` | `(bool, str)` |
| `logic.delete_department(name)` | `(bool, str)` |

### Auth Operations
| Function | Returns |
|---|---|
| `logic.check_users()` | `pd.DataFrame` |
| `logic.list_visible_users(actor_username, actor_role)` | `pd.DataFrame` |
| `logic.create_user(username, full_name, password, role)` | `(bool, str)` |
| `logic.admin_update_user(target_username, new_username, full_name, role, password=None)` | `(bool, str, str \| None)` |
| `logic.update_own_profile(current_username, full_name, password=None)` | `(bool, str, str \| None)` |
| `logic.verify_password(password, password_hash)` | `bool` |
| `logic.hash_password(password)` | `str` |

### Settings
| Function | Returns |
|---|---|
| `logic.get_company_name()` | `str` |
| `logic.set_company_name(name)` | `(bool, str)` |

### Cache
| Function | Purpose |
|---|---|
| `logic.invalidate_data_cache(file_name=None)` | Clear cache for one or all entities |
| `logic.get_data_cache_stats()` | Get hit/miss statistics |

---

## 5. Return Value Convention

All CRUD operations return a tuple `(success: bool, message: str)`.

```python
ok, msg = logic.add_customer(...)
if ok:
    # show success alert with msg
else:
    # show error alert with msg
```

---

## 6. Callback Patterns

### Standard CRUD Pattern

Every form callback follows this structure:
```python
@app.callback(
    [Output("alert-id", "children"),
     Output("table-container-id", "children"),
     Output("modal-id", "is_open")],
    Input("btn-save", "n_clicks"),
    [State("input-field", "value"), ...],
    prevent_initial_call=True,
)
def save_entity(n_clicks, value, ...):
    if not n_clicks:
        return no_update, no_update, no_update
    
    ok, msg = logic.add_entity(value, ...)
    alert = dbc.Alert(msg, color="success" if ok else "danger")
    table = get_table_content() if ok else no_update
    is_open = False if ok else True
    return alert, table, is_open
```

### Search Dropdown Pattern

```python
@app.callback(
    Output("entity-search", "options"),
    Input("entity-search", "search_value"),
)
def search_entities(search_value):
    df = load_data("entities.csv", cols)
    if search_value:
        df = df[df["name_col"].str.contains(search_value, na=False)]
    return [{"label": row["name"], "value": row["id"]} for _, row in df.iterrows()]
```

---

## 7. Password Hashing Details

The system uses PBKDF2-HMAC-SHA256 for hashing:

```
Format: pbkdf2_sha256$<iterations>$<salt>$<hex_digest>
Example: pbkdf2_sha256$260000$a1b2c3d4e5f6....$abcdef1234...
```

Legacy SHA-256 plain hashes (64-char hex) are automatically upgraded to PBKDF2 on successful login.

---

## 8. Image Upload Flow

1. User selects image in dcc.Upload component
2. Callback receives base64-encoded image content
3. `logic.save_image(image_contents, dress_code)` is called
4. Image is saved to `dress_images/<dress_code>.jpg` using Pillow
5. The path is stored in `dresses.image_path`
6. Images are served via Flask route: `/dress_images/<filename>`

---

## 9. Environment Variable Checklist for Deployment

| Variable | Required in Prod | Notes |
|---|---|---|
| `APP_SECRET_KEY` | ✅ Yes | Strong random string, min 32 chars |
| `APP_ENV` | ✅ Yes | Set to `production` |
| `APP_DEBUG` | ✅ Yes | Set to `0` |
| `APP_RELOADER` | Optional | `0` in production |
| `DATABASE_URL` | Optional | If using PostgreSQL instead of SQLite |
| `APP_BOOTSTRAP_ADMIN` | Optional | Only for automated first-run admin creation |

---

## 10. Constitution Lint / Architecture Invariants

The file `scripts/constitution_lint.py` enforces architectural rules:
- Callbacks must not import directly from `app/domain` (must go through `logic.py`)
- No circular imports between layers
- Message strings must come from `app/constants.py`

Run with:
```bash
python scripts/constitution_lint.py
```

Also available as a pytest test:
```bash
pytest tests/test_constitution_lint.py -v
```

---

## 11. Testing Guide

Test files in `tests/`:

| Test File | What It Tests |
|---|---|
| `conftest.py` | Pytest fixtures: temp DB, test SessionLocal |
| `test_auth_logic.py` | Password hashing, default admin seeding, visible-users filtering, admin/self account updates |
| `test_customers_logic.py` | Add/update/delete customer, phone validation |
| `test_payments_logic.py` | Payment limits, remaining calculation |
| `test_booking_payment_integration.py` | Full booking → payment flow |
| `test_constitution_lint.py` | Architecture invariant enforcement |
| `test_root_feedback_policy.py` | Message format conventions |

Tests use a temporary SQLite DB (`:memory:` or temp file) — they never touch the production `atelier.db`.

---

## 12. Scripts Reference

| Script | Purpose |
|---|---|
| `scripts/health_check.py` | Comprehensive DB health + data integrity check |
| `scripts/e2e_playwright.py` | Full browser end-to-end tests |
| `scripts/backup_restore_smoke.py` | Test backup creation and restore |
| `scripts/repair_data.py` | Data repair utilities |
| `scripts/constitution_lint.py` | Architecture rules linter |
| `scripts/cleanup_test_artifacts.py` | Remove test artifacts |
| `scripts/run_backup_restore_smoke.cmd` | Windows command wrapper for backup smoke test |

---

## 13. Key Design Decisions

| Decision | Rationale |
|---|---|
| `logic.py` as single facade | Prevents domain layer from being imported directly by UI; enables testability; single point for session sync |
| In-memory dict cache with 2s TTL | Reduces DB hits on rapid navigation without needing Redis; safe because writes always invalidate |
| All tabs rendered at login | Avoids lazy-loading complexity; CSS show/hide gives instant switching; acceptable for small datasets |
| Denormalized customer_name in bookings | Maintained for display performance; proper FK (`customer_id`) also stored for relational integrity |
| Strings as dates | Dates stored as VARCHAR `YYYY-MM-DD` strings for simplicity; Pandas converts when needed |
| Arabic-first constants | All user-facing strings in `constants.py` as Arabic; no translation layer needed for current scope |
