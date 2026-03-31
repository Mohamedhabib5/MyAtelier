# Codex Plan - MyAtelier

> STATUS: Historical working plan snapshot.
> This file reflects an in-progress planning state from an earlier session and should not be treated as the current source of truth for implemented behavior.
> For current behavior, refer to `docs/01_overview.md` through `docs/06_developer_reference.md`.
> Note: several items listed here were superseded later, including the responsive mobile/tablet implementation and the current targeted Playwright smoke modes.

Last Update: 2026-02-18
Owner: Codex
Status: Archived snapshot

## 1) الهدف العام
- تثبيت التطبيق بالكامل (تشغيل + صحة بيانات + E2E) مع كود نظيف وقابل للصيانة.
- منع الرجوع لنمط التعديلات العشوائي عبر خطة تنفيذية صغيرة الخطوات.

## 2) الحالة الحالية (Snapshot)
- التطبيق يعمل على `http://127.0.0.1:8050` (HTTP 200 في آخر فحوصات).
- فحوصات `py_compile` و `health_check` تمر بنجاح.
- التقسيم المعماري الأساسي تم (مجلد `app/` مع callbacks/layouts/composition).
- `app_dash.py` أصبح EntryPoint/Wiring بشكل جيد.
- العائق الرئيسي الحالي: E2E في `phase1b2b` يتوقف عند `step 3: dress image flow`.

## 3) ما تم إنجازه فعليًا
- مراجعة الخطة العامة عدة مرات وتحديث مسار التنفيذ إلى خطوات أصغر.
- حذف الخطة غير المعتمدة: `docs/execution_plan_final.md`.
- إصلاح فشل سابق في `phase1b1` (كان بسبب `Services export failed`) عبر تقوية `export_current_table` في:
  - `scripts/e2e_playwright.py`
- تأكيد نجاح:
  - `FULL_PHASE=phase1b1` بعد الإصلاح.
  - `FULL_PHASE=phase1b2a` (services + customers).
- إضافة مسار مستقل `phase1b2b` لعزل الجزء التالي من الفلو.

## 4) ما فشل حتى الآن
- `FULL_PHASE=phase1b2b` يفشل بالـ timeout.
- آخر نقطة مؤكدة قبل التوقف:
  - `[FULL_PHASE1B2] step 3: dress image flow`

## 5) التحديات الحالية والمتوقعة
- هشاشة E2E بسبب:
  - modals لا تُغلق دائمًا بنفس التوقيت.
  - selectors حساسة/غير ثابتة.
  - سلوك export/تحميل يعتمد أحيانًا على client-side events.
- ضغط تشغيلي من حجم السجلات والـ artifacts داخل `logs/`.
- استمرار backup-on-write في `logic.py` يبطئ دورة التجربة في بعض السيناريوهات.
- احتمال ظهور timeouts جديدة عند دمج مراحل E2E حتى بعد نجاحها منفصلة.

## 6) خطة التنفيذ القادمة (مرتبة)

### Phase A - إغلاق عطل E2E الحالي
1. تشخيص دقيق داخل `step 3` في `phase1b2b`:
   - checkpoints إضافية داخل dress image flow.
   - screenshots قبل/بعد كل action حساس.
2. إصلاح نقطة التعليق (modal/image upload/save) عبر retries + fail-fast واضح.
3. إعادة تشغيل `phase1b2b` حتى PASS.
4. إعادة تشغيل `phase1b2` الكامل حتى PASS.
5. تشغيل `phase2`.

Exit Criteria:
- `phase1b2b` PASS
- `phase1b2` PASS
- `phase2` PASS

### Phase B - أداء واستقرار دورة التطوير
1. إزالة الاستدعاءات التلقائية لـ `_backup_before_write()` من CRUD في `logic.py`.
2. الإبقاء على النسخ الاحتياطي اليدوي فقط.
3. التحقق أن CRUD أسرع وأن التطبيق مستقر.

Exit Criteria:
- لا backup تلقائي لكل عملية CRUD
- سلوك التطبيق دون تغيير وظيفي

### Phase C - النظافة المعمارية والـ repo hygiene
1. تقليل الضجيج في التتبع (generated artifacts) عبر إعدادات تجاهل مناسبة.
2. مواصلة تنظيف الحدود بين entrypoint / business logic.
3. توثيق أي خطوة مكتملة في هذا الملف مباشرة.

Exit Criteria:
- `git status` يركز على تغييرات المصدر الفعلية
- سهولة متابعة التعديلات القادمة بدون تعارض

## 7) بروتوكول التنفيذ الإجباري لكل خطوة
بعد أي تعديل:
1. `python -m py_compile app_dash.py logic.py models.py`
2. `python scripts/health_check.py`
3. تشغيل التطبيق والتحقق من `http://127.0.0.1:8050`
4. إذا تغير سلوك UI/flows:
   - تشغيل E2E المستهدف فقط (وليس full regression مباشرة)

## 8) سجل آخر تشغيلات مهمة
- PASS: `py_compile`
- PASS: `health_check`
- PASS: app run check (HTTP 200)
- PASS: `FULL_PHASE=phase1b1` (بعد إصلاح export)
- PASS: `FULL_PHASE=phase1b2a`
- FAIL: `FULL_PHASE=phase1b2b` (timeout عند dress image flow)

## 9) أين نكمل لاحقًا (Resume Point)
- الملف التالي للعمل: `scripts/e2e_playwright.py`
- نقطة البدء: `step 3: dress image flow` ضمن مسار `phase1b2b`
- الهدف المباشر عند الاستئناف:
  - تحديد السطر المعلق بدقة
  - إصلاحه
  - إثبات PASS لــ `phase1b2b` ثم `phase1b2`

## 10) ملاحظات حوكمة
- لا تنفيذ لخطوات كبيرة دفعة واحدة.
- كل خطوة صغيرة + تحقق + تقرير.
- أي فشل يجب تسجيله هنا مباشرة مع:
  - السبب
  - أسلوب الإصلاح
  - نتيجة إعادة الاختبار
