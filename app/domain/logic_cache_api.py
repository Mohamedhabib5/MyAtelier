def build_cache_wrappers(make_synced_wrapper, data_access_domain):
    invalidate_data_cache = make_synced_wrapper(data_access_domain.invalidate_data_cache)
    get_data_cache_stats = make_synced_wrapper(data_access_domain.get_cache_stats)
    reset_data_cache_stats = make_synced_wrapper(data_access_domain.reset_cache_stats)
    return invalidate_data_cache, get_data_cache_stats, reset_data_cache_stats


def invalidate_after_write(
    with_synced_sessionlocal,
    data_access_domain,
    invalidate_fn,
    result,
    *,
    file_name=None,
):
    return with_synced_sessionlocal(
        data_access_domain.invalidate_after_write,
        result,
        file_name=file_name,
        invalidate_fn=invalidate_fn,
    )


def invalidate_many(
    with_synced_sessionlocal,
    data_access_domain,
    invalidate_fn,
    file_names,
):
    return with_synced_sessionlocal(
        data_access_domain.invalidate_many,
        file_names,
        invalidate_fn=invalidate_fn,
    )
