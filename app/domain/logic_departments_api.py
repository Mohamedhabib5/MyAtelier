def check_departments(
    with_synced_sessionlocal,
    settings_dept_domain,
    default_departments,
):
    return settings_dept_domain.check_departments(default_departments)


def add_department(
    departments_facade_domain,
    with_synced_sessionlocal,
    settings_dept_domain,
    invalidate_after_write,
    invalidate_many,
    *,
    name,
    msg_missing_info,
    msg_already_exists,
    msg_added,
):
    return departments_facade_domain.add_department(
        with_synced_sessionlocal,
        settings_dept_domain,
        invalidate_after_write,
        invalidate_many,
        name=name,
        msg_missing_info=msg_missing_info,
        msg_already_exists=msg_already_exists,
        msg_added=msg_added,
    )


def update_department(
    departments_facade_domain,
    with_synced_sessionlocal,
    settings_dept_domain,
    invalidate_after_write,
    invalidate_many,
    *,
    old_name,
    new_name,
    msg_not_found,
    msg_already_exists,
    msg_updated,
):
    return departments_facade_domain.update_department(
        with_synced_sessionlocal,
        settings_dept_domain,
        invalidate_after_write,
        invalidate_many,
        old_name=old_name,
        new_name=new_name,
        msg_not_found=msg_not_found,
        msg_already_exists=msg_already_exists,
        msg_updated=msg_updated,
    )


def delete_department(
    departments_facade_domain,
    with_synced_sessionlocal,
    settings_dept_domain,
    invalidate_after_write,
    invalidate_many,
    *,
    name,
    msg_not_found,
    msg_in_use,
    msg_deleted,
):
    return departments_facade_domain.delete_department(
        with_synced_sessionlocal,
        settings_dept_domain,
        invalidate_after_write,
        invalidate_many,
        name=name,
        msg_not_found=msg_not_found,
        msg_in_use=msg_in_use,
        msg_deleted=msg_deleted,
    )


def save_department(departments_facade_domain, add_department_fn, name):
    return departments_facade_domain.save_department(add_department_fn, name)
