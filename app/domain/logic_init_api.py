def init_folders(
    *,
    os_module,
    image_folder,
    init_db_fn,
    ensure_booking_service_id_column_fn,
    migrate_money_columns_fn,
    ensure_booking_status_column_fn,
    backfill_booking_service_ids_fn,
    backfill_service_departments_fn,
    backfill_booking_departments_fn,
    normalize_money_precision_fn,
    session_local,
    ensure_release_default_admin_fn,
):
    if not os_module.path.exists(image_folder):
        os_module.makedirs(image_folder)

    init_db_fn()
    ensure_booking_service_id_column_fn()
    migrate_money_columns_fn()
    ensure_booking_status_column_fn()
    backfill_booking_service_ids_fn()
    backfill_service_departments_fn()
    backfill_booking_departments_fn()
    normalize_money_precision_fn()

    session = session_local()
    try:
        ensure_release_default_admin_fn(session)
    finally:
        session.close()
