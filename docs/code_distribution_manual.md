# دليل توزيع الكود في MyAtelier (Manual)
آخر تحديث: 2026-02-17

## 1) نظرة سريعة على المعمارية
البرنامج مبني على طبقات واضحة:
1. `app_dash.py`  
   Entry Point فقط (تشغيل التطبيق وربط الطبقات).
2. `app/composition/*`  
   تجميع المكونات وربط الاعتماديات (Wiring).
3. `app/layouts/*`  
   بناء الواجهات (UI Structure).
4. `app/table_content/*` + `app/ui/grid.py`  
   بناء جداول العرض ومحتواها.
5. `app/callbacks/*`  
   منطق التفاعل مع الواجهة (الأزرار/النوافذ/الحفظ/الحذف).
6. `logic.py` + `models.py`  
   منطق الأعمال + طبقة البيانات وقاعدة البيانات.

---

## 2) دور كل ملف أساسي

### `app_dash.py`
- إنشاء التطبيق عبر `app/bootstrap.py`.
- تعريف route الصور.
- بناء wiring عبر `app/composition/wiring.py`.
- تعيين `root layout`.
- تسجيل جميع callbacks.
- تشغيل السيرفر.

ممنوع وضع منطق CRUD أو business rules داخله.

### `app/composition/wiring.py`
- يبني دالة `create_dt`.
- يربط table content factories.
- يخرج `main_layout` وجميع دوال محتوى الجداول.

### `app/composition/layout_factory.py`
- طبقة تمرير اعتماديات إلى `layout_main`.

### `app/layouts/main.py`
- الهيكل العام للوحة بعد تسجيل الدخول (sidebar, tabs, stores, modals shared).

### `app/layouts/<feature>.py`
- كل شاشة Feature لها layout مستقل:
  - `customers.py`, `services.py`, `bookings.py`, `dresses.py`, `payments.py`, `settings.py`, `users.py`, `finance.py`.

### `app/callbacks/register_all.py`
- نقطة التسجيل الموحدة لكل callbacks.
- أي callback جديد يجب أن يُسجّل هنا (أو عبر ملف وسيط واضح).

### `app/callbacks/<feature>_*.py`
- منطق التفاعل الخاص بكل ميزة.
- أمثلة:
  - `customers_form.py` لإضافة/تعديل/حذف العملاء.
  - `customers_search.py` للبحث.
  - `bookings_form.py` لنوافذ وإجراءات الحجز.

### `app/table_content/*`
- توليد محتوى الجداول لكل ميزة.
- لا يحتوي منطق حفظ/تعديل، فقط العرض.

### `logic.py`
- API الداخلية لكل العمليات:
  - add/update/delete/load/check.
- يحتوي business validations وقواعد منع/سماح العمليات.

### `models.py`
- تعريف ORM models والاتصال بقاعدة البيانات.

---

## 3) أين تعدّل حسب نوع الطلب

### تعديل شكل واجهة فقط
- عدّل `app/layouts/<feature>.py`
- وربما `assets/custom.css`

### تعديل سلوك زر/نافذة/تفاعل
- عدّل `app/callbacks/<feature>_*.py`
- لا تنقل CRUD إلى callback مباشرة، استدعِ `logic.py`.

### تعديل قواعد العمل (Business Rules)
- عدّل `logic.py` (أو service domain عند اكتمال التفكيك).
- مثال: منع حذف عنصر مرتبط، تحقق من المبالغ، قواعد الحجز.

### تعديل أعمدة/كيانات قاعدة البيانات
- عدّل `models.py`
- ثم حدّث `logic.py` + `health_check.py` + callbacks المتأثرة.

### إضافة شاشة جديدة
1. `app/layouts/<new_feature>.py`
2. `app/table_content/<new_feature>.py` (لو يوجد جدول)
3. `app/callbacks/<new_feature>_form.py` و`<new_feature>_search.py` حسب الحاجة
4. تسجيلها في `app/callbacks/register_all.py`
5. ربطها في `app/layouts/main.py` + `app/composition/wiring.py` عند الحاجة

---

## 4) تدفق العمل الداخلي (مختصر)
1. المستخدم يضغط زر في الواجهة.
2. callback داخل `app/callbacks/*` يستقبل الحدث.
3. callback يستدعي `logic.py` لتنفيذ العملية.
4. `logic.py` يتعامل مع `models.py`/DB.
5. callback يعيد تحديث الجدول عبر `get_*_table_content()`.

---

## 5) قواعد تنظيم تمنع التعارضات مستقبلًا
1. لا تضف feature logic داخل `app_dash.py`.
2. لا تضع SQL/ORM داخل `layouts`.
3. لا تكرر نفس helper في أكثر من callback؛ ضعه في ملف helper مشترك.
4. أي تغيير cross-feature يمر عبر `composition`.
5. لا تعدّل `backups/` ولا `releases/`.

---

## 6) checklist قبل إنهاء أي تعديل
1. `python -m py_compile app_dash.py logic.py models.py`
2. `python app_dash.py` ثم تأكد أن `http://127.0.0.1:8050` يعمل
3. `python scripts/health_check.py`
4. إذا غيرت واجهة/تدفق:
   - شغّل التحقق الواجهي المستهدف أو `python scripts/e2e_playwright.py`

---

## 7) أهداف الوظائف الرئيسية (Functional Intent)
- **Customers**: إدارة بيانات العميل الأساسية والهواتف والملاحظات.
- **Services**: إدارة الخدمات والأسعار والأقسام.
- **Dresses**: إدارة الفساتين والحالة والصور.
- **Bookings**: ربط العميل بالخدمة/الفستان/تاريخ المناسبة مع حسابات السعر.
- **Payments**: تسجيل الدفعات وربطها بالحجز وتحديث المتبقي.
- **Finance**: مؤشرات ورسوم الأداء المالي.
- **Settings**: النسخ الاحتياطي وإدارة الأقسام.
- **Users**: عرض/إدارة مستخدمي النظام وصلاحياتهم.

---

## 8) مسار التطوير الصحيح لأي تعديل جديد
1. حدد نوع التعديل (UI / Callback / Business / Data).
2. عدّل في مكان واحد واضح أولًا.
3. اختبر.
4. ثم نفذ التعديل التالي.

القاعدة الذهبية:
- "Small Step, Verified Step, Documented Step"
