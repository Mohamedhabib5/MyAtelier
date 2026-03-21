# MyAtelier — User Guide (دليل المستخدم)

This guide explains how to use each module of the MyAtelier system.

---

## 1. Logging In (تسجيل الدخول)

1. Open your browser and go to **http://localhost:8050**
2. Enter your **username** (اسم المستخدم)
3. Enter your **password** (كلمة المرور)
4. Click **دخول 🚀**

If your credentials are correct, you are taken to the main dashboard.
If incorrect, a red alert appears: ❌ بيانات غير صحيحة

**Default admin credentials** (first-time only, on a new empty database):
- Username: `admin`
- Password: `admin123`

> ⚠️ Change the default password immediately after first login. After you change the admin username or password, the system does not recreate `admin` again.

---

## 2. Navigation

### Desktop Navigation (Sidebar)
The left sidebar contains navigation links for all modules. Click any link to switch views instantly.

| Icon | Section | Arabic |
|---|---|---|
| 🏠 | Finance Dashboard | الرئيسية |
| 📅 | Bookings | الحجوزات |
| 👥 | Customers | العملاء |
| ✂️ | Services | الخدمات |
| 💎 | Dresses | الفساتين |
| 💰 | Payments | المدفوعات |
| ⚙️ | Settings | الإعدادات |
| 👤 | Users / My Account | المستخدمين / حسابي |

At the bottom of the sidebar your name and a **Logout** button (خروج) are shown.

### Mobile Navigation (Bottom Bar)
On small screens, a bottom bar appears with quick access to:
- Finance (الرئيسية)
- Bookings (الحجوزات)
- Customers (العملاء)
- Logout (خروج)
- Menu (القائمة) — toggles sidebar

---

## 3. Finance Dashboard (التقارير المالية)

This is the home screen after login. It displays:

### KPI Cards (3 metrics)
| Card | Description |
|---|---|
| إجمالي الدخل | Total income collected (sum of all payments) |
| المستحقات (متبقي) | Total remaining balance across all bookings |
| إجمالي الحجوزات | Total number of bookings |

### Charts (3 charts)
1. **الدخل اليومي** — Bar chart of daily income from payments
2. **توزيع الدخل حسب القسم** — Pie chart of income by department
3. **أكثر الخدمات طلباً** — Horizontal bar chart of top 5 most-booked services

Charts load when you first navigate to this tab.

---

## 4. Bookings Module (إدارة الحجوزات)

### Searching for a Booking
Use the search bar at the top to find bookings. You can search by:
- Bride's name (اسم العروسة)
- Booking code (الكود)

Select a result from the dropdown to load that booking. The **Edit** (تعديل) and **Delete** (حذف) buttons become active.

### Adding a New Booking (حجز جديد)
1. Click **حجز جديد** (top right)
2. Fill in the form:
   - **القسم** — Select department (Makeup, Hair, Photography, Skin, Dresses)
   - **العروسة** — Select or search for an existing customer. Click **+** to add a new customer without leaving the form.
   - **الخدمة** — Select service (filtered by selected department)
   - **كود الفستان** — Only shown when department is "الفساتين" — select a dress
   - **تاريخ الحجز** — Booking creation date (default: today)
   - **تاريخ المناسبة** — The actual event date
   - **السعر المتفق** — Agreed total price
   - **العربون** — Down payment (optional)
   - **حالة الحجز** — Status: نشط (Active) / مكتمل (Complete) / ملغي (Cancelled)
   - **ملاحظات** — Free text notes
3. Click **تأكيد الحجز**

> A payment record is automatically created for the down payment with note "عربون حجز".

> ⚠️ The system prevents booking the same dress on the same event date twice.

### Editing a Booking
1. Search and select the booking
2. Click **تعديل**
3. Modify fields in the form
4. Click **تأكيد الحجز**

### Deleting a Booking
1. Search and select the booking
2. Click **حذف**
3. A confirmation dialog appears — click **حذف** to confirm or **تراجع** to cancel

### Booking Table
Shows all bookings in a paginated grid (10 rows per page) with columns:
كود الحجز، تاريخ الحجز، اسم العروسه، القسم، الخدمة، كود الفستان، تاريخ المناسبة، السعر المتفق، المدفوع، المتبقي، ملاحظات الحجز، حالة الحجز

Click **تفاصيل الدفعات** action button in a row to view payment details for that booking.

---

## 5. Customers Module (إدارة العملاء)

### Adding a New Customer
1. Click **عميل جديد** (top right)
2. Fill in:
   - **اسم العروسة** (required)
   - **اسم العريس** (required)
   - **تليفون 1** (required, digits only, e.g. 01012345678)
   - **تليفون 2** (optional, digits only)
   - **العنوان** (optional)
   - **تاريخ التسجيل** (optional, defaults to today)
   - **ملاحظات** (optional)
3. Click **حفظ**

> Phone numbers must be numeric and unique across all customers.

### Editing / Deleting a Customer
Same pattern — search, select, then use Edit or Delete buttons.

> ⚠️ A customer cannot be deleted if they have active bookings.

### Customer Table Columns
كود العميل، تاريخ التسجيل، اسم العروسه، اسم العريس، العنوان، تليفون 1، تليفون 2، ملاحظات

Click **تفاصيل الحجوزات** to view all bookings for a customer.

---

## 6. Services Module (إدارة الخدمات)

### Adding a Service
1. Click **خدمة جديدة**
2. Fill in:
   - **اسم الخدمة** — Service name
   - **القسم** — Department
   - **السعر المقترح** — Suggested price
3. Click **حفظ**

### Service Table Columns
كود الخدمة، القسم، اسم الخدمة، السعر المقترح

> A service cannot be deleted if it is referenced by bookings.

---

## 7. Dresses Module (إدارة الفساتين)

### Adding a Dress
1. Click **إضافة فستان**
2. Fill in:
   - **كود الفستان** — Unique dress code (e.g. DR-001)
   - **نوع الفستان** — Type/Category
   - **تاريخ الشراء** — Purchase date
   - **حالة الفستان** — Status (Available, Rented, Maintenance)
   - **وصف الفستان** — Description
   - **صورة الفستان** — Upload a photo (JPEG/PNG)
3. Click **حفظ**

### Dress Status Values
| Value | Meaning |
|---|---|
| Available | الفستان جاهز للحجز |
| Rented | محجوز حالياً |
| Maintenance | في الصيانة |

### Dress Table Columns
كود الفستان، نوع الفستان، تاريخ الشراء، وصف الفستان، صورة الفستان، حالة الفستان

Click **تفاصيل الحجوزات** to see all bookings for a dress.

> A dress cannot be deleted if it has bookings.

---

## 8. Payments Module (إدارة المدفوعات)

### Adding a Payment
1. Click **دفعة جديدة**
2. Fill in:
   - **كود الحجز** — Select the booking
   - **المبلغ** — Payment amount
   - **التاريخ** — Payment date
   - **ملاحظات** — Notes
3. Click **حفظ**

> ⚠️ The payment amount cannot exceed the remaining balance on the booking.

### Payment Table Columns
كود الدفع، التاريخ، كود الحجز، القيمة المدفوعة، اسم العروسه، اسم العريس، المتبقي بعد الدفعة، ملاحظات الدفع

Click **تفاصيل الحجز** to view the related booking.

---

## 9. Settings Module (الإعدادات)

### Company Name (اسم الشركة)
Enter the business name and click **Save**. This name appears in the sidebar header.

### Backup (النسخ الاحتياطي)
- **إنشاء وتنزيل نسخة احتياطية**: Creates a backup snapshot, builds a ZIP archive, and starts downloading the ZIP file to your browser.
- **فتح مجلد النسخ الاحتياطية**: Opens the backups folder in the file manager.

The backup path is shown on screen. Snapshot folders are stored under `backups/`, while ZIP archives are stored under `releases/`.

### Department Management (إدارة الأقسام)
- Add new departments (✚ قسم جديد)
- Edit existing departments
- Delete departments (only if no services/bookings are linked)

---

## 10. Users Module (المستخدمين / حسابي)

This screen changes based on the logged-in role.

### Admin view
- The tab appears as **المستخدمين**
- Admin can see all users
- Admin can add a new user
- Admin can edit username, full name, password, and role for any user

### Regular user view
- The tab appears as **حسابي**
- Regular `user` accounts see only their own account
- They cannot see other users
- They can edit only their own full name and password
- They cannot add users or change roles

### Roles
| Role | Access |
|---|---|
| `admin` | Full access to the Users screen and all user accounts |
| `user` | Sees only own account and can update own full name/password |

---

## 11. Details Viewer (عارض التفاصيل)

A modal dialog appears when you click action buttons like **تفاصيل الحجوزات** or **تفاصيل الدفعات** in any table row. It shows related data for the selected record. Close it with the **إغلاق** button.

---

## 12. Logging Out

Click **خروج** in the:
- Desktop: Bottom of the sidebar
- Mobile: Bottom navigation bar or top-left of mobile header
