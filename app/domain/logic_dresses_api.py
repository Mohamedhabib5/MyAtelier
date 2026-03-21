def save_image(
    dresses_facade_domain,
    with_synced_sessionlocal,
    dresses_domain,
    *,
    image_contents,
    dress_code,
    image_folder,
):
    return dresses_facade_domain.save_image(
        with_synced_sessionlocal,
        dresses_domain,
        image_contents=image_contents,
        dress_code=dress_code,
        image_folder=image_folder,
    )


def add_dress(
    dresses_facade_domain,
    with_synced_sessionlocal,
    dresses_domain,
    invalidate_after_write,
    *,
    code,
    d_type,
    date_buy,
    status,
    desc,
    image_contents,
    image_folder,
    msg_missing_info,
    msg_code_exists,
    msg_added,
):
    return dresses_facade_domain.add_dress(
        with_synced_sessionlocal,
        dresses_domain,
        invalidate_after_write,
        code=code,
        d_type=d_type,
        date_buy=date_buy,
        status=status,
        desc=desc,
        image_contents=image_contents,
        image_folder=image_folder,
        msg_missing_info=msg_missing_info,
        msg_code_exists=msg_code_exists,
        msg_added=msg_added,
    )


def update_dress(
    dresses_facade_domain,
    with_synced_sessionlocal,
    dresses_domain,
    invalidate_after_write,
    invalidate_data_cache_fn,
    *,
    old_code,
    new_code,
    d_type,
    date_buy,
    status,
    desc,
    image_contents,
    image_folder,
    msg_not_found,
    msg_new_code_exists,
    msg_updated,
):
    return dresses_facade_domain.update_dress(
        with_synced_sessionlocal,
        dresses_domain,
        invalidate_after_write,
        invalidate_data_cache_fn,
        old_code=old_code,
        new_code=new_code,
        d_type=d_type,
        date_buy=date_buy,
        status=status,
        desc=desc,
        image_contents=image_contents,
        image_folder=image_folder,
        msg_not_found=msg_not_found,
        msg_new_code_exists=msg_new_code_exists,
        msg_updated=msg_updated,
    )


def delete_dress(
    dresses_facade_domain,
    with_synced_sessionlocal,
    dresses_domain,
    invalidate_after_write,
    invalidate_data_cache_fn,
    *,
    d_code,
    image_folder,
    msg_not_found,
    msg_has_bookings,
    msg_deleted,
):
    return dresses_facade_domain.delete_dress(
        with_synced_sessionlocal,
        dresses_domain,
        invalidate_after_write,
        invalidate_data_cache_fn,
        d_code=d_code,
        image_folder=image_folder,
        msg_not_found=msg_not_found,
        msg_has_bookings=msg_has_bookings,
        msg_deleted=msg_deleted,
    )
