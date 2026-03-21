def add_customer(
    run_synced_fn,
    customers_domain,
    invalidate_after_write_fn,
    *,
    name,
    groom,
    phone1,
    phone2,
    address,
    reg_date,
    notes,
    msg_missing_info,
    msg_invalid_phone,
    msg_added,
):
    result = run_synced_fn(
        customers_domain.add_customer,
        name,
        groom,
        phone1,
        phone2,
        address,
        reg_date=reg_date,
        notes=notes,
        msg_missing_info=msg_missing_info,
        msg_invalid_phone=msg_invalid_phone,
        msg_added=msg_added,
    )
    return invalidate_after_write_fn(result, file_name="customers.csv")


def update_customer(
    run_synced_fn,
    customers_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    c_id,
    name,
    groom,
    phone1,
    phone2,
    address,
    reg_date,
    notes,
    msg_missing_info,
    msg_not_found,
    msg_phone_used_by_another,
    msg_updated,
):
    result = run_synced_fn(
        customers_domain.update_customer,
        c_id,
        name,
        groom,
        phone1,
        phone2,
        address,
        reg_date=reg_date,
        notes=notes,
        msg_missing_info=msg_missing_info,
        msg_not_found=msg_not_found,
        msg_phone_used_by_another=msg_phone_used_by_another,
        msg_updated=msg_updated,
    )
    ok = invalidate_after_write_fn(result, file_name="customers.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok


def delete_customer(
    run_synced_fn,
    customers_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    c_id,
    msg_not_found,
    msg_has_bookings,
    msg_deleted,
):
    result = run_synced_fn(
        customers_domain.delete_customer,
        c_id,
        msg_not_found=msg_not_found,
        msg_has_bookings=msg_has_bookings,
        msg_deleted=msg_deleted,
    )
    ok = invalidate_after_write_fn(result, file_name="customers.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok
