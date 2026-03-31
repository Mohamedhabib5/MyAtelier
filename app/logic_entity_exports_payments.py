def build_payment_exports(context):
    c = context

    def add_payment(booking_id, amount, bride_name, groom_name, notes, date_val=None, session=None, commit=True):
        return c["logic_payments_api_domain"].add_payment(
            c["payments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["payments_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            booking_id=booking_id,
            amount=amount,
            bride_name=bride_name,
            groom_name=groom_name,
            notes=notes,
            date_val=date_val,
            session=session,
            commit=commit,
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
            msg_invalid_value=c["MSG_INVALID_VALUE"],
            msg_payment_gt_remaining=c["MSG_PAYMENT_GT_REMAINING"],
        )

    def add_payment_typed(
        booking_id,
        amount,
        bride_name,
        groom_name,
        notes,
        date_val=None,
        session=None,
        commit=True,
        *,
        payment_kind="booking_installment",
        affects_booking_balance=True,
        source_module="payments",
        source_custody_id=None,
        display_label="دفعة حجز",
        allow_over_remaining=False,
    ):
        return c["logic_payments_api_domain"].add_payment(
            c["payments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["payments_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            booking_id=booking_id,
            amount=amount,
            bride_name=bride_name,
            groom_name=groom_name,
            notes=notes,
            date_val=date_val,
            session=session,
            commit=commit,
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
            msg_invalid_value=c["MSG_INVALID_VALUE"],
            msg_payment_gt_remaining=c["MSG_PAYMENT_GT_REMAINING"],
            payment_kind=payment_kind,
            affects_booking_balance=affects_booking_balance,
            source_module=source_module,
            source_custody_id=source_custody_id,
            display_label=display_label,
            allow_over_remaining=allow_over_remaining,
        )

    def update_payment(p_id, booking_id, amount, notes, date_val=None):
        return c["logic_payments_api_domain"].update_payment(
            c["payments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["payments_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            p_id=p_id,
            booking_id=booking_id,
            amount=amount,
            notes=notes,
            date_val=date_val,
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
            msg_invalid_value=c["MSG_INVALID_VALUE"],
            msg_payment_gt_remaining=c["MSG_PAYMENT_GT_REMAINING"],
        )

    def delete_payment(p_id):
        return c["logic_payments_api_domain"].delete_payment(
            c["payments_facade_domain"],
            c["_with_synced_sessionlocal"],
            c["payments_domain"],
            c["_invalidate_after_write"],
            c["invalidate_data_cache"],
            p_id=p_id,
            money_fn=c["_money"],
            money_float_fn=c["_money_float"],
        )

    return {
        "add_payment": add_payment,
        "add_payment_typed": add_payment_typed,
        "update_payment": update_payment,
        "delete_payment": delete_payment,
    }
