from models import Dress, Payment


def _money(value, money_fn):
    return money_fn(value or 0)


def _money_float(value, money_float_fn):
    return money_float_fn(value or 0)


def _append_note(existing_text, extra_text):
    existing = (existing_text or "").strip()
    extra = (extra_text or "").strip()
    if not extra:
        return existing
    if not existing:
        return extra
    return f"{existing}\n{extra}"


def _has_dress(custody):
    dress_code = str(getattr(custody, "dress_code", "") or "").strip()
    return dress_code not in {"", "-", "None", "nan"}


def _load_dress(session, custody):
    if not _has_dress(custody):
        return None
    return session.query(Dress).filter_by(dress_code=str(custody.dress_code).strip()).first()


def _has_existing_compensation(session, custody_id):
    return (
        session.query(Payment)
        .filter_by(source_custody_id=custody_id, payment_kind="custody_compensation")
        .first()
        is not None
    )


def receive_from_customer(custody_id, return_date=None, condition_in="", damage_notes="", handled_by=""):
    from app.domain import dress_custody as custody_domain

    has_damage = bool((damage_notes or "").strip())
    return custody_domain.complete_customer_return(
        custody_id,
        return_date=return_date,
        condition_in=condition_in,
        notes=damage_notes,
        has_damage=has_damage,
        compensation_amount=0,
        guarantee_returned=True,
        guarantee_return_date=return_date,
        handled_by=handled_by,
        payment_date=return_date,
        money_fn=lambda v: v,
        money_float_fn=lambda v: v,
        add_payment_fn=lambda *args, **kwargs: (True, "ok"),
    )


def send_to_laundry(custody_id, laundry_sent_date=None, notes="", handled_by=""):
    from app.domain import dress_custody as custody_domain

    return custody_domain.update_service_status(
        custody_id,
        custody_domain.SERVICE_STATUS_LAUNDRY,
        action_date=laundry_sent_date,
        notes=notes,
        handled_by=handled_by,
    )


def receive_from_laundry(custody_id, laundry_return_date=None, notes="", handled_by=""):
    from app.domain import dress_custody as custody_domain

    return custody_domain.update_service_status(
        custody_id,
        custody_domain.SERVICE_STATUS_MAINTENANCE,
        action_date=laundry_return_date,
        notes=notes,
        handled_by=handled_by,
    )
