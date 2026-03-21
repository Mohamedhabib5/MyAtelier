def add_service(
    services_facade_domain,
    with_synced_sessionlocal,
    services_domain,
    invalidate_after_write,
    *,
    name,
    dept,
    price,
    money_float_fn,
    msg_missing_info,
    msg_added,
):
    return services_facade_domain.add_service(
        with_synced_sessionlocal,
        services_domain,
        invalidate_after_write,
        name=name,
        dept=dept,
        price=price,
        money_float_fn=money_float_fn,
        msg_missing_info=msg_missing_info,
        msg_added=msg_added,
    )


def update_service(
    services_facade_domain,
    with_synced_sessionlocal,
    services_domain,
    invalidate_after_write,
    invalidate_data_cache_fn,
    *,
    s_id,
    name,
    dept,
    price,
    money_float_fn,
    msg_updated,
    msg_not_found,
):
    return services_facade_domain.update_service(
        with_synced_sessionlocal,
        services_domain,
        invalidate_after_write,
        invalidate_data_cache_fn,
        s_id=s_id,
        name=name,
        dept=dept,
        price=price,
        money_float_fn=money_float_fn,
        msg_updated=msg_updated,
        msg_not_found=msg_not_found,
    )


def delete_service(
    services_facade_domain,
    with_synced_sessionlocal,
    services_domain,
    invalidate_after_write,
    invalidate_data_cache_fn,
    *,
    s_id,
    msg_not_found,
    msg_has_bookings,
    msg_deleted,
):
    return services_facade_domain.delete_service(
        with_synced_sessionlocal,
        services_domain,
        invalidate_after_write,
        invalidate_data_cache_fn,
        s_id=s_id,
        msg_not_found=msg_not_found,
        msg_has_bookings=msg_has_bookings,
        msg_deleted=msg_deleted,
    )
