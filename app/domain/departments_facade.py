def check_departments(run_synced_fn, settings_domain, default_departments):
    return run_synced_fn(settings_domain.check_departments, default_departments)


def add_department(
    run_synced_fn,
    settings_domain,
    invalidate_after_write_fn,
    invalidate_many_fn,
    *,
    name,
    msg_missing_info,
    msg_already_exists,
    msg_added,
):
    result = run_synced_fn(
        settings_domain.add_department,
        name,
        msg_missing_info=msg_missing_info,
        msg_already_exists=msg_already_exists,
        msg_added=msg_added,
    )
    ok = invalidate_after_write_fn(result, file_name="departments.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_many_fn(["services.csv", "bookings.csv"])
    return ok


def update_department(
    run_synced_fn,
    settings_domain,
    invalidate_after_write_fn,
    invalidate_many_fn,
    *,
    old_name,
    new_name,
    msg_not_found,
    msg_already_exists,
    msg_updated,
):
    result = run_synced_fn(
        settings_domain.update_department,
        old_name,
        new_name,
        msg_not_found=msg_not_found,
        msg_already_exists=msg_already_exists,
        msg_updated=msg_updated,
    )
    ok = invalidate_after_write_fn(result, file_name="departments.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_many_fn(["services.csv", "bookings.csv"])
    return ok


def delete_department(
    run_synced_fn,
    settings_domain,
    invalidate_after_write_fn,
    invalidate_many_fn,
    *,
    name,
    msg_not_found,
    msg_in_use,
    msg_deleted,
):
    result = run_synced_fn(
        settings_domain.delete_department,
        name,
        msg_not_found=msg_not_found,
        msg_in_use=msg_in_use,
        msg_deleted=msg_deleted,
    )
    ok = invalidate_after_write_fn(result, file_name="departments.csv")
    if isinstance(ok, tuple) and ok and ok[0]:
        invalidate_many_fn(["services.csv", "bookings.csv"])
    return ok


def save_department(add_department_fn, name):
    ok, _ = add_department_fn(name)
    return ok
