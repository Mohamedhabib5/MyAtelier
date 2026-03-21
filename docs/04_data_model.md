# MyAtelier — Database & Data Model

---

## 1. Database Configuration

- **Default DB**: SQLite file `atelier.db` in the project root
- **ORM**: SQLAlchemy with `declarative_base`
- **Connection**: Configured via `DATABASE_URL` environment variable
- **Session factory**: `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`

```python
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///atelier.db")
engine = create_engine(DATABASE_URL, echo=False)
```

---

## 2. Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────────┐
│    customers    │       │        bookings          │
├─────────────────┤       ├─────────────────────────┤
│ customer_id PK  │◄──┐   │ booking_id PK           │
│ reg_date        │   └───│ customer_id FK           │
│ name            │       │ customer_name            │
│ groom_name      │       │ department               │
│ address         │       │ service_id FK (nullable) │
│ phone1          │       │ service                  │
│ phone2          │       │ dress_code (nullable)    │
│ notes           │       │ booking_date             │
└─────────────────┘       │ event_date               │
                          │ price                    │
┌─────────────────┐       │ paid                     │
│    services     │       │ remaining                │
├─────────────────┤       │ status                   │
│ service_id PK   │◄──────│ notes                    │
│ department      │       └─────────────────────────┘
│ name            │                  │
│ price           │                  │ 1:N
└─────────────────┘                  ▼
                          ┌─────────────────────────┐
┌─────────────────┐       │        payments         │
│    dresses      │       ├─────────────────────────┤
├─────────────────┤       │ payment_id PK           │
│ dress_code PK   │       │ booking_id FK           │
│ d_type          │       │ payment_date            │
│ buy_date        │       │ amount                  │
│ description     │       │ customer_name           │
│ image_path      │       │ groom_name              │
│ status          │       │ remaining_after         │
└─────────────────┘       │ notes                   │
                          └─────────────────────────┘

┌─────────────────┐       ┌─────────────────────────┐
│   departments   │       │       app_settings       │
├─────────────────┤       ├─────────────────────────┤
│ department_name │       │ key PK                  │
│   (PK)          │       │ value                   │
└─────────────────┘       └─────────────────────────┘

┌─────────────────┐
│     users       │
├─────────────────┤
│ username PK     │
│ password_hash   │
│ full_name       │
│ role            │
│ created_date    │
└─────────────────┘
```

---

## 3. Table Definitions

### `customers`

Stores the bride (and optionally groom) information.

| Column | Type | Description |
|---|---|---|
| `customer_id` | String PK | Auto-generated, format `C-<number>` |
| `reg_date` | String | Registration date (YYYY-MM-DD) |
| `name` | String (indexed) | Bride's name |
| `groom_name` | String | Groom's name |
| `address` | String | Address |
| `phone1` | String (indexed) | Primary phone (must be unique) |
| `phone2` | String | Secondary phone |
| `notes` | String | Free text notes |

**Relationships**: One customer → many bookings

---

### `services`

Service catalog entries, organized by department.

| Column | Type | Description |
|---|---|---|
| `service_id` | String PK | Auto-generated, format `S-<number>` |
| `department` | String (indexed) | Department name (must exist in departments table) |
| `name` | String | Service name |
| `price` | Numeric(12,2) | Suggested price |

---

### `dresses`

Dress inventory items with optional photo.

| Column | Type | Description |
|---|---|---|
| `dress_code` | String PK | User-defined unique code |
| `d_type` | String | Dress type/category |
| `buy_date` | String | Purchase date (YYYY-MM-DD) |
| `description` | String | Description |
| `image_path` | String | Relative path to image in `dress_images/` |
| `status` | String | `Available` / `Rented` / `Maintenance` |

---

### `bookings`

The central table linking customers to services/dresses for an event.

| Column | Type | Description |
|---|---|---|
| `booking_id` | String PK | Auto-generated e.g. `HR-123456` |
| `booking_date` | String | Date booking was created |
| `customer_name` | String | Bride's name (denormalized for display) |
| `customer_id` | String FK (nullable) | Link to `customers.customer_id` |
| `department` | String | Department name |
| `service_id` | String FK (nullable) | Link to `services.service_id` |
| `service` | String | Service name (denormalized) |
| `dress_code` | String (nullable) | Dress code if applicable |
| `event_date` | String | Date of the event |
| `price` | Numeric(12,2) | Agreed total price |
| `paid` | Numeric(12,2) | Total amount paid so far |
| `remaining` | Numeric(12,2) | `price - paid` |
| `status` | String | `نشط` (Active) / `مكتمل` (Complete) / `ملغي` (Cancelled) |
| `notes` | String | Free text notes |

**Relationships**:
- Belongs to one `Customer`
- Has many `Payment`s

---

### `payments`

Individual payment transactions tied to a booking.

| Column | Type | Description |
|---|---|---|
| `payment_id` | String PK | Auto-generated e.g. `PAY-876543` |
| `payment_date` | String | Date of payment |
| `booking_id` | String FK | Link to `bookings.booking_id` |
| `amount` | Numeric(12,2) | Amount paid this transaction |
| `customer_name` | String | Bride's name (denormalized) |
| `groom_name` | String | Groom's name (denormalized) |
| `remaining_after` | Numeric(12,2) | Remaining on booking after this payment |
| `notes` | String | Payment notes |

---

### `departments`

Lookup table for service/booking departments.

| Column | Type | Description |
|---|---|---|
| `department_name` | String PK | Name of the department |

**Built-in default departments** (created on first run):
- المكياج (Makeup)
- التصوير (Photography)
- الفساتين (Dresses)
- الشعر (Hair)
- البشرة (Skin)

---

### `app_settings`

Key-value store for application configuration.

| Column | Type | Description |
|---|---|---|
| `key` | String PK | Setting key, e.g. `company_name` |
| `value` | String | Setting value |

Currently stores:
- `company_name` (displayed in sidebar header)
- `auth.default_admin_seeded` (marks that the release default admin was seeded once)

---

### `users`

Authentication records.

| Column | Type | Description |
|---|---|---|
| `username` | String PK | Login username |
| `password_hash` | String | PBKDF2-SHA256 hash (format: `pbkdf2_sha256$iters$salt$hexhash`) |
| `full_name` | String | Display name shown in sidebar |
| `role` | String | Application-supported values are `admin` and `user` |
| `created_date` | String | Account creation date |

---

## 4. Column Name Mapping (DB ↔ UI)

All database column names are in English. The app displays Arabic column headers using `*_COLS_MAP` dictionaries in `app/domain/data_access.py`:

**Customers (`C_COLS_MAP`)**:
```
customer_id   → كود العميل
reg_date      → تاريخ التسجيل
name          → اسم العروسه
groom_name    → اسم العريس
address       → العنوان
phone1        → تليفون 1
phone2        → تليفون 2
notes         → ملاحظات
```

**Bookings (`B_COLS_MAP`)**:
```
booking_id    → كود الحجز
booking_date  → تاريخ الحجز
customer_name → اسم العروسه
department    → القسم
service       → الخدمة
dress_code    → كود الفستان
event_date    → تاريخ المناسبة
price         → السعر المتفق
paid          → المدفوع
remaining     → المتبقي
notes         → ملاحظات الحجز
status        → حالة الحجز
```

---

## 5. Schema Migrations

The app includes automatic schema migration logic in `app/domain/migrations.py` that runs every time the app starts:

| Migration | What It Does |
|---|---|
| `ensure_booking_service_id_column` | Adds `service_id` column to bookings if missing (upgrade path) |
| `ensure_booking_status_column` | Adds `status` column to bookings if missing; backfills "نشط" |
| `migrate_sqlite_money_columns_to_numeric` | Converts TEXT money columns to NUMERIC(12,2) |
| `backfill_booking_service_ids` | Fills `service_id` from `service` name for existing bookings |
| `backfill_service_departments` | Ensures all services have a valid department |
| `backfill_booking_departments` | Ensures all bookings have a valid department |
| `normalize_money_precision` | Rounds all monetary values to 2 decimal places |

These migrations are **additive and idempotent** — safe to run repeatedly.

---

## 6. Financial Logic

### When a Booking Is Created
- `price` = agreed total
- `paid` = down payment (if any)
- `remaining` = `price - paid`
- If `paid > 0`, a Payment record is automatically created with `notes = "عربون حجز"`

### When a Payment Is Added
- New `Payment` is created with the `amount`
- `booking.paid` += `amount`
- `booking.remaining` -= `amount`
- `remaining_after` on the payment = booking's remaining after this payment

### Validation Rules
- `paid` cannot exceed `price` (MSG_PAID_GT_PRICE)
- New payment `amount` cannot exceed current `remaining` (MSG_PAYMENT_GT_REMAINING)
- A dress cannot be booked on the same `event_date` twice (MSG_DRESS_BOOKED_SAME_DATE)
