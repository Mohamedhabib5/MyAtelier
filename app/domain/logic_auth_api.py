def build_user_wrappers(make_synced_wrapper, auth_domain):
    return (
        make_synced_wrapper(auth_domain.check_users),
        make_synced_wrapper(auth_domain.save_users_data),
        make_synced_wrapper(auth_domain.update_user_password_hash),
        make_synced_wrapper(auth_domain.list_visible_users),
        make_synced_wrapper(auth_domain.create_user),
        make_synced_wrapper(auth_domain.admin_update_user),
        make_synced_wrapper(auth_domain.update_own_profile),
    )
