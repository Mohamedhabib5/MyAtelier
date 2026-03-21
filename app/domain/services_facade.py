def add_service(
    run_synced_fn,
    services_domain,
    invalidate_after_write_fn,
    *,
    name,
    dept,
    price,
    money_float_fn,
    msg_missing_info,
    msg_added,
):
    result = run_synced_fn(
        services_domain.add_service,
        name,
        dept,
        price,
        money_float_fn=money_float_fn,
        msg_missing_info=msg_missing_info,
        msg_added=msg_added,
    )
    return invalidate_after_write_fn(result, file_name="services.csv")


def update_service(
    run_synced_fn,
    services_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    s_id,
    name,
    dept,
    price,
    money_float_fn,
    msg_updated,
    msg_not_found,
):
    result = run_synced_fn(
        services_domain.update_service,
        s_id,
        name,
        dept,
        price,
        money_float_fn=money_float_fn,
        msg_updated=msg_updated,
        msg_not_found=msg_not_found,
    )
    ok = invalidate_after_write_fn(result, file_name="services.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok


def delete_service(
    run_synced_fn,
    services_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    s_id,
    msg_not_found,
    msg_has_bookings,
    msg_deleted,
):
    result = run_synced_fn(
        services_domain.delete_service,
        s_id,
        msg_not_found=msg_not_found,
        msg_has_bookings=msg_has_bookings,
        msg_deleted=msg_deleted,
    )
    ok = invalidate_after_write_fn(result, file_name="services.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok
