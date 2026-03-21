def add_payment(
    run_synced_fn,
    payments_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    booking_id,
    amount,
    bride_name,
    groom_name,
    notes,
    date_val,
    session,
    commit,
    money_fn,
    money_float_fn,
    msg_invalid_value,
    msg_payment_gt_remaining,
):
    result = run_synced_fn(
        payments_domain.add_payment,
        booking_id,
        amount,
        bride_name,
        groom_name,
        notes,
        date_val=date_val,
        session=session,
        commit=commit,
        money_fn=money_fn,
        money_float_fn=money_float_fn,
        msg_invalid_value=msg_invalid_value,
        msg_payment_gt_remaining=msg_payment_gt_remaining,
    )
    ok = invalidate_after_write_fn(result, file_name="payments.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok


def update_payment(
    run_synced_fn,
    payments_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    p_id,
    booking_id,
    amount,
    notes,
    date_val,
    money_fn,
    money_float_fn,
    msg_invalid_value,
    msg_payment_gt_remaining,
):
    result = run_synced_fn(
        payments_domain.update_payment,
        p_id,
        booking_id,
        amount,
        notes,
        date_val=date_val,
        money_fn=money_fn,
        money_float_fn=money_float_fn,
        msg_invalid_value=msg_invalid_value,
        msg_payment_gt_remaining=msg_payment_gt_remaining,
    )
    ok = invalidate_after_write_fn(result, file_name="payments.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok


def delete_payment(
    run_synced_fn,
    payments_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    p_id,
    money_fn,
    money_float_fn,
):
    result = run_synced_fn(
        payments_domain.delete_payment,
        p_id,
        money_fn=money_fn,
        money_float_fn=money_float_fn,
    )
    ok = invalidate_after_write_fn(result, file_name="payments.csv")
    if ok:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok
