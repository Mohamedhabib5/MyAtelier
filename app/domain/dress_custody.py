from datetime import date
import time

from models import Booking, Dress, DressCustody, Payment, SessionLocal
from app.domain.dress_custody_helpers import (
    _append_note,
    _has_dress,
    _has_existing_compensation,
    _load_dress,
    _money,
    _money_float,
    receive_from_customer,
    receive_from_laundry,
    send_to_laundry,
)


STATUS_READY = "جاهز للتسليم"
STATUS_HANDED_OVER = "عند العميل"
STATUS_IN_SERVICE = "في المغسلة والصيانة"
STATUS_AVAILABLE = "متاح للإيجار"
STATUS_CLOSED = "مغلق"

SERVICE_STATUS_LAUNDRY = "في المغسلة"
SERVICE_STATUS_MAINTENANCE = "تحت الصيانة"
SERVICE_STATUS_AVAILABLE = "متاح للإيجار"

# Compatibility aliases for older UI/tests.
STATUS_RETURNED_FROM_CUSTOMER = STATUS_IN_SERVICE
STATUS_IN_LAUNDRY = STATUS_IN_SERVICE
STATUS_AWAITING_SETTLEMENT = STATUS_IN_SERVICE
STATUS_AWAITING_EXTRA = STATUS_IN_SERVICE

def create_custody(
    booking_id,
    deposit_amount,
    guarantee_type="",
    guarantee_reference="",
    notes="",
    handled_by="",
    created_date=None,
    *,
    money_fn,
    money_float_fn,
):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter_by(booking_id=booking_id).first()
        if not booking:
            return False, "الحجز غير موجود", None

        existing = session.query(DressCustody).filter_by(booking_id=booking_id).first()
        if existing:
            return False, "يوجد سجل تسليم واستلام لهذا الحجز بالفعل", None

        deposit = _money(deposit_amount, money_fn)
        if deposit < 0:
            return False, "قيمة التأمين غير صحيحة", None

        dress_code = str(getattr(booking, "dress_code", "") or "").strip()
        if dress_code in {"-", "None", "nan"}:
            dress_code = ""

        dress = None
        if dress_code:
            dress = session.query(Dress).filter_by(dress_code=dress_code).first()
            if not dress:
                return False, "الفستان المرتبط بالحجز غير موجود", None

        custody_id = f"CUST-{int(time.time() * 1000)}"
        custody = DressCustody(
            custody_id=custody_id,
            booking_id=booking_id,
            dress_code=dress_code,
            customer_name_snapshot=getattr(booking, "customer_name", ""),
            event_date_snapshot=getattr(booking, "event_date", ""),
            status=STATUS_READY,
            deposit_amount=_money_float(deposit, money_float_fn),
            deposit_refunded_amount=0,
            deposit_used_for_damage=0,
            extra_compensation_due=0,
            extra_compensation_paid=0,
            settlement_notes=(notes or "").strip(),
            guarantee_type=(guarantee_type or "").strip(),
            guarantee_reference=(guarantee_reference or "").strip(),
            handled_by=(handled_by or "").strip(),
            guarantee_received=bool((guarantee_type or "").strip() or (guarantee_reference or "").strip()),
            service_status="",
        )
        session.add(custody)

        if dress:
            dress.status = "محجوز"

        session.commit()
        return True, "تم فتح سجل التسليم والاستلام", custody_id
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}", None
    finally:
        session.close()


def handover_to_customer(custody_id, handover_date=None, condition_out="", notes="", handled_by=""):
    session = SessionLocal()
    try:
        custody = session.query(DressCustody).filter_by(custody_id=custody_id).first()
        if not custody:
            return False, "السجل غير موجود"
        if custody.status != STATUS_READY:
            return False, "لا يمكن تنفيذ التسليم في الحالة الحالية"

        custody.handover_date = str(handover_date or date.today())
        custody.condition_out = (condition_out or "").strip()
        custody.settlement_notes = _append_note(custody.settlement_notes, notes)
        if handled_by:
            custody.handled_by = handled_by.strip()
        custody.status = STATUS_HANDED_OVER

        dress = _load_dress(session, custody)
        if dress:
            dress.status = "عند العميل"

        session.commit()
        return True, "تم التسليم للعميل"
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()


def complete_customer_return(
    custody_id,
    *,
    return_date=None,
    condition_in="",
    notes="",
    has_damage=False,
    compensation_amount=0,
    guarantee_returned=False,
    guarantee_return_date=None,
    handled_by="",
    payment_date=None,
    money_fn,
    money_float_fn,
    add_payment_fn,
):
    session = SessionLocal()
    try:
        custody = session.query(DressCustody).filter_by(custody_id=custody_id).first()
        if not custody:
            return False, "السجل غير موجود"
        if custody.status != STATUS_HANDED_OVER:
            return False, "لا يمكن الاستلام من العميل في الحالة الحالية"
        if not guarantee_returned:
            return False, "يجب رد وثيقة الضمان قبل تحويل العملية للمغسلة والصيانة أو إغلاقها"
        if _has_existing_compensation(session, custody_id):
            return False, "تم إنشاء سند تعويض لهذا السجل بالفعل"

        deposit_amount = _money(custody.deposit_amount, money_fn)
        compensation_total = _money(compensation_amount, money_fn) if has_damage else _money(0, money_fn)
        if compensation_total < 0:
            return False, "قيمة سند التعويض غير صحيحة"
        if has_damage and compensation_total <= 0:
            return False, "أدخل قيمة سند التعويض"

        deposit_used = min(compensation_total, deposit_amount)
        deposit_refunded = max(deposit_amount - deposit_used, _money(0, money_fn))
        extra_collected = max(compensation_total - deposit_used, _money(0, money_fn))

        custody.customer_return_date = str(return_date or date.today())
        custody.condition_in = (condition_in or "").strip()
        custody.damage_notes = (notes or "").strip() if has_damage else ""
        custody.settlement_notes = _append_note(
            custody.settlement_notes,
            f"استلام من العميل بتاريخ {custody.customer_return_date}" if not notes else notes,
        )
        custody.deposit_used_for_damage = _money_float(deposit_used, money_float_fn)
        custody.deposit_refunded_amount = _money_float(deposit_refunded, money_float_fn)
        custody.extra_compensation_due = _money_float(extra_collected, money_float_fn)
        custody.extra_compensation_paid = _money_float(extra_collected, money_float_fn)
        custody.guarantee_returned = True
        custody.guarantee_return_date = str(guarantee_return_date or return_date or date.today())
        if handled_by:
            custody.handled_by = handled_by.strip()

        booking = session.query(Booking).filter_by(booking_id=custody.booking_id).first()
        customer_name = getattr(booking, "customer_name", custody.customer_name_snapshot or "")

        # Accounting rule: only the cash extra collected from the customer
        # should create a compensation payment voucher.
        if extra_collected > 0:
            has_dress = _has_dress(custody)
            label = "سند تعويض فستان" if has_dress else "سند تعويض عهدة"
            payment_notes = f"{label} - من سجل التسليم والاستلام"
            ok, msg = add_payment_fn(
                custody.booking_id,
                money_float_fn(extra_collected),
                customer_name,
                "",
                payment_notes,
                str(payment_date or return_date or date.today()),
                session=session,
                commit=False,
                payment_kind="custody_compensation",
                affects_booking_balance=False,
                source_module="dress_custody",
                source_custody_id=custody_id,
                display_label=label,
                allow_over_remaining=True,
            )
            if not ok:
                session.rollback()
                return False, msg

        dress = _load_dress(session, custody)
        if dress:
            custody.status = STATUS_IN_SERVICE
            custody.service_status = SERVICE_STATUS_LAUNDRY
            custody.laundry_sent_date = str(return_date or date.today())
            custody.closed_date = None
            dress.status = SERVICE_STATUS_LAUNDRY
            message = "تم الاستلام من العميل وتحويل الفستان إلى المغسلة والصيانة"
        else:
            custody.status = STATUS_CLOSED
            custody.service_status = ""
            custody.closed_date = str(return_date or date.today())
            message = "تم الاستلام من العميل وإغلاق العملية"

        session.commit()
        return True, message
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()


def update_service_status(custody_id, service_status, action_date=None, notes="", handled_by=""):
    session = SessionLocal()
    try:
        custody = session.query(DressCustody).filter_by(custody_id=custody_id).first()
        if not custody:
            return False, "السجل غير موجود"
        if custody.status not in {STATUS_IN_SERVICE, STATUS_AVAILABLE}:
            return False, "لا يمكن تحديث حالة المغسلة والصيانة في الحالة الحالية"
        if not _has_dress(custody):
            return False, "هذه العملية غير مرتبطة بفستان"

        new_status = str(service_status or "").strip()
        if new_status not in {SERVICE_STATUS_LAUNDRY, SERVICE_STATUS_MAINTENANCE, SERVICE_STATUS_AVAILABLE}:
            return False, "حالة المغسلة والصيانة غير صحيحة"

        dress = _load_dress(session, custody)
        if not dress:
            return False, "الفستان المرتبط بالسجل غير موجود"

        custody.service_status = new_status
        custody.settlement_notes = _append_note(custody.settlement_notes, notes)
        if handled_by:
            custody.handled_by = handled_by.strip()

        if new_status == SERVICE_STATUS_AVAILABLE:
            custody.status = STATUS_AVAILABLE
            custody.laundry_return_date = str(action_date or date.today())
            custody.closed_date = str(action_date or date.today())
            dress.status = SERVICE_STATUS_AVAILABLE
            message = "تم تحديث الفستان إلى متاح للإيجار"
        else:
            custody.status = STATUS_IN_SERVICE
            if new_status == SERVICE_STATUS_LAUNDRY:
                custody.laundry_sent_date = str(action_date or date.today())
            dress.status = new_status
            message = "تم تحديث حالة المغسلة والصيانة"

        session.commit()
        return True, message
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()
def settle_custody(
    custody_id,
    deposit_used_for_damage,
    deposit_refunded_amount,
    extra_compensation_due,
    extra_compensation_paid,
    settlement_notes="",
    guarantee_returned=False,
    guarantee_return_date=None,
    handled_by="",
    settlement_date=None,
    *,
    money_fn,
    money_float_fn,
    add_payment_fn,
):
    compensation_amount = _money(deposit_used_for_damage, money_fn) + _money(extra_compensation_due, money_fn)
    return complete_customer_return(
        custody_id,
        return_date=settlement_date,
        condition_in="",
        notes=settlement_notes,
        has_damage=compensation_amount > 0,
        compensation_amount=compensation_amount,
        guarantee_returned=guarantee_returned,
        guarantee_return_date=guarantee_return_date,
        handled_by=handled_by,
        payment_date=settlement_date,
        money_fn=money_fn,
        money_float_fn=money_float_fn,
        add_payment_fn=add_payment_fn,
    )


def collect_extra_compensation(
    custody_id,
    amount,
    payment_date=None,
    notes="",
    handled_by="",
    *,
    money_fn,
    money_float_fn,
    add_payment_fn,
):
    session = SessionLocal()
    try:
        custody = session.query(DressCustody).filter_by(custody_id=custody_id).first()
        if not custody:
            return False, "السجل غير موجود"
        if custody.status not in {STATUS_IN_SERVICE, STATUS_AVAILABLE, STATUS_CLOSED}:
            return False, "لا توجد تحصيلات إضافية مطلوبة لهذا السجل"

        amt = _money(amount, money_fn)
        if amt <= 0:
            return False, "قيمة التحصيل غير صحيحة"

        booking = session.query(Booking).filter_by(booking_id=custody.booking_id).first()
        customer_name = getattr(booking, "customer_name", custody.customer_name_snapshot or "")
        ok, msg = add_payment_fn(
            custody.booking_id,
            money_float_fn(amt),
            customer_name,
            "",
            notes or "تحصيل تعويض إضافي",
            str(payment_date or date.today()),
            session=session,
            commit=False,
            payment_kind="custody_compensation",
            affects_booking_balance=False,
            source_module="dress_custody",
            source_custody_id=custody_id,
            display_label="سند تعويض إضافي",
            allow_over_remaining=True,
        )
        if not ok:
            session.rollback()
            return False, msg

        custody.extra_compensation_due = _money_float(
            _money(custody.extra_compensation_due, money_fn) + amt,
            money_float_fn,
        )
        custody.extra_compensation_paid = _money_float(
            _money(custody.extra_compensation_paid, money_fn) + amt,
            money_float_fn,
        )
        if handled_by:
            custody.handled_by = handled_by.strip()
        session.commit()
        return True, "تم تسجيل تحصيل إضافي"
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()
