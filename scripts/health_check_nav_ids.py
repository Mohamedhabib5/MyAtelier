from health_check_context import *

def _collect_component_ids(node, out_ids):
    if node is None:
        return
    if isinstance(node, (list, tuple)):
        for item in node:
            _collect_component_ids(item, out_ids)
        return

    comp_id = getattr(node, "id", None)
    if isinstance(comp_id, str) and comp_id:
        out_ids.add(comp_id)

    children = getattr(node, "children", None)
    if children is not None:
        _collect_component_ids(children, out_ids)
def _main_nav_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "nav-finance",
            "nav-bookings",
            "nav-customers",
            "nav-services",
            "nav-dresses",
            "nav-payments",
            "nav-settings",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _critical_action_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "btn-add-service-modal",
            "btn-save-service",
            "btn-add-customer-modal",
            "btn-save-customer",
            "btn-add-booking-modal",
            "btn-save-booking",
            "btn-add-payment-modal",
            "btn-save-payment",
            "btn-delete-booking",
            "btn-delete-service",
            "btn-delete-customer",
            "btn-delete-payment",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
def _table_ids_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        ids = set()
        _collect_component_ids(layout, ids)

        required_ids = [
            "customers-table-container",
            "services-table-container",
            "dresses-table-container",
            "bookings-table-container",
            "payments-table-container",
        ]
        missing = [rid for rid in required_ids if rid not in ids]
        result["missing"] = missing
        result["ok"] = not missing
    except Exception as e:
        result["error"] = str(e)
    return result
