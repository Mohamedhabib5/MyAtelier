def save_image(run_synced_fn, dresses_domain, *, image_contents, dress_code, image_folder):
    return run_synced_fn(
        dresses_domain.save_image,
        image_contents,
        dress_code,
        image_folder=image_folder,
    )


def add_dress(
    run_synced_fn,
    dresses_domain,
    invalidate_after_write_fn,
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
    result = run_synced_fn(
        dresses_domain.add_dress,
        code,
        d_type,
        date_buy,
        status,
        desc,
        image_contents=image_contents,
        image_folder=image_folder,
        msg_missing_info=msg_missing_info,
        msg_code_exists=msg_code_exists,
        msg_added=msg_added,
    )
    return invalidate_after_write_fn(result, file_name="dresses.csv")


def update_dress(
    run_synced_fn,
    dresses_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
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
    result = run_synced_fn(
        dresses_domain.update_dress,
        old_code,
        new_code,
        d_type,
        date_buy,
        status,
        desc,
        image_contents=image_contents,
        image_folder=image_folder,
        msg_not_found=msg_not_found,
        msg_new_code_exists=msg_new_code_exists,
        msg_updated=msg_updated,
    )
    ok = invalidate_after_write_fn(result, file_name="dresses.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok


def delete_dress(
    run_synced_fn,
    dresses_domain,
    invalidate_after_write_fn,
    invalidate_cache_fn,
    *,
    d_code,
    image_folder,
    msg_not_found,
    msg_has_bookings,
    msg_deleted,
):
    result = run_synced_fn(
        dresses_domain.delete_dress,
        d_code,
        image_folder=image_folder,
        msg_not_found=msg_not_found,
        msg_has_bookings=msg_has_bookings,
        msg_deleted=msg_deleted,
    )
    ok = invalidate_after_write_fn(result, file_name="dresses.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_cache_fn(file_name="bookings.csv")
    return ok
