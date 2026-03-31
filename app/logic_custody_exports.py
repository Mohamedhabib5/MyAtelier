def build_custody_exports(context):
    dress_custody_domain = context["dress_custody_domain"]
    _with_synced_sessionlocal = context["_with_synced_sessionlocal"]
    _invalidate_after_write = context["_invalidate_after_write"]
    _invalidate_many = context["_invalidate_many"]
    _money = context["_money"]
    _money_float = context["_money_float"]
    add_payment_typed = context["add_payment_typed"]

    def create_dress_custody(booking_id, deposit_amount, guarantee_type="", guarantee_reference="", notes="", handled_by="", created_date=None):
        result = _with_synced_sessionlocal(
            dress_custody_domain.create_custody,
            booking_id,
            deposit_amount,
            guarantee_type=guarantee_type,
            guarantee_reference=guarantee_reference,
            notes=notes,
            handled_by=handled_by,
            created_date=created_date,
            money_fn=_money,
            money_float_fn=_money_float,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["dresses.csv", "bookings.csv"])
        return result

    def handover_dress_custody(custody_id, handover_date=None, condition_out="", notes="", handled_by=""):
        result = _with_synced_sessionlocal(
            dress_custody_domain.handover_to_customer,
            custody_id,
            handover_date=handover_date,
            condition_out=condition_out,
            notes=notes,
            handled_by=handled_by,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["dresses.csv"])
        return result

    def receive_dress_from_customer(
        custody_id,
        return_date=None,
        condition_in="",
        damage_notes="",
        handled_by="",
        *,
        has_damage=False,
        compensation_amount=0,
        guarantee_returned=True,
        guarantee_return_date=None,
    ):
        result = _with_synced_sessionlocal(
            dress_custody_domain.complete_customer_return,
            custody_id,
            return_date=return_date,
            condition_in=condition_in,
            notes=damage_notes,
            has_damage=has_damage,
            compensation_amount=compensation_amount,
            guarantee_returned=guarantee_returned,
            guarantee_return_date=guarantee_return_date,
            handled_by=handled_by,
            payment_date=return_date,
            money_fn=_money,
            money_float_fn=_money_float,
            add_payment_fn=add_payment_typed,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["dresses.csv", "payments.csv", "bookings.csv"])
        return result

    def update_dress_custody_service_status(custody_id, service_status, action_date=None, notes="", handled_by=""):
        result = _with_synced_sessionlocal(
            dress_custody_domain.update_service_status,
            custody_id,
            service_status,
            action_date=action_date,
            notes=notes,
            handled_by=handled_by,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["dresses.csv"])
        return result

    def send_dress_to_laundry(custody_id, laundry_sent_date=None, notes="", handled_by=""):
        return update_dress_custody_service_status(
            custody_id,
            dress_custody_domain.SERVICE_STATUS_LAUNDRY,
            action_date=laundry_sent_date,
            notes=notes,
            handled_by=handled_by,
        )

    def receive_dress_from_laundry(custody_id, laundry_return_date=None, notes="", handled_by=""):
        return update_dress_custody_service_status(
            custody_id,
            dress_custody_domain.SERVICE_STATUS_MAINTENANCE,
            action_date=laundry_return_date,
            notes=notes,
            handled_by=handled_by,
        )

    def settle_dress_custody(
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
    ):
        result = _with_synced_sessionlocal(
            dress_custody_domain.settle_custody,
            custody_id,
            deposit_used_for_damage,
            deposit_refunded_amount,
            extra_compensation_due,
            extra_compensation_paid,
            settlement_notes=settlement_notes,
            guarantee_returned=guarantee_returned,
            guarantee_return_date=guarantee_return_date,
            handled_by=handled_by,
            settlement_date=settlement_date,
            money_fn=_money,
            money_float_fn=_money_float,
            add_payment_fn=add_payment_typed,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["payments.csv", "bookings.csv", "dresses.csv"])
        return result

    def collect_dress_extra_compensation(custody_id, amount, payment_date=None, notes="", handled_by=""):
        result = _with_synced_sessionlocal(
            dress_custody_domain.collect_extra_compensation,
            custody_id,
            amount,
            payment_date=payment_date,
            notes=notes,
            handled_by=handled_by,
            money_fn=_money,
            money_float_fn=_money_float,
            add_payment_fn=add_payment_typed,
        )
        result = _invalidate_after_write(result, file_name="dress_custody.csv")
        if isinstance(result, tuple) and result and result[0]:
            _invalidate_many(["payments.csv", "bookings.csv"])
        return result

    return {
        "DRESS_CUSTODY_STATUS_READY": dress_custody_domain.STATUS_READY,
        "DRESS_CUSTODY_STATUS_HANDED_OVER": dress_custody_domain.STATUS_HANDED_OVER,
        "DRESS_CUSTODY_STATUS_IN_SERVICE": dress_custody_domain.STATUS_IN_SERVICE,
        "DRESS_CUSTODY_STATUS_AVAILABLE": dress_custody_domain.STATUS_AVAILABLE,
        "DRESS_CUSTODY_STATUS_RETURNED_FROM_CUSTOMER": dress_custody_domain.STATUS_RETURNED_FROM_CUSTOMER,
        "DRESS_CUSTODY_STATUS_IN_LAUNDRY": dress_custody_domain.STATUS_IN_LAUNDRY,
        "DRESS_CUSTODY_STATUS_AWAITING_SETTLEMENT": dress_custody_domain.STATUS_AWAITING_SETTLEMENT,
        "DRESS_CUSTODY_STATUS_AWAITING_EXTRA": dress_custody_domain.STATUS_AWAITING_EXTRA,
        "DRESS_CUSTODY_STATUS_CLOSED": dress_custody_domain.STATUS_CLOSED,
        "DRESS_CUSTODY_SERVICE_STATUS_LAUNDRY": dress_custody_domain.SERVICE_STATUS_LAUNDRY,
        "DRESS_CUSTODY_SERVICE_STATUS_MAINTENANCE": dress_custody_domain.SERVICE_STATUS_MAINTENANCE,
        "DRESS_CUSTODY_SERVICE_STATUS_AVAILABLE": dress_custody_domain.SERVICE_STATUS_AVAILABLE,
        "create_dress_custody": create_dress_custody,
        "handover_dress_custody": handover_dress_custody,
        "receive_dress_from_customer": receive_dress_from_customer,
        "update_dress_custody_service_status": update_dress_custody_service_status,
        "send_dress_to_laundry": send_dress_to_laundry,
        "receive_dress_from_laundry": receive_dress_from_laundry,
        "settle_dress_custody": settle_dress_custody,
        "collect_dress_extra_compensation": collect_dress_extra_compensation,
    }
