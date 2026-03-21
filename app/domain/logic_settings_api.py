def get_company_name(get_app_setting_fn, default_company_name):
    return get_app_setting_fn("company_name", default_company_name)


def set_company_name(
    with_synced_sessionlocal,
    settings_dept_domain,
    set_app_setting_fn,
    norm_text_fn,
    name,
):
    return with_synced_sessionlocal(
        settings_dept_domain.set_company_name,
        name,
        norm_text_fn=norm_text_fn,
        set_app_setting_fn=set_app_setting_fn,
    )
