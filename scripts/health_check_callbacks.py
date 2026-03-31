from health_check_context import *

def _export_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "exportDataAsCsv" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for exportDataAsCsv"
    except Exception as e:
        result["error"] = str(e)
    return result

def _details_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "modal-details-viewer.is_open" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for modal-details-viewer.is_open"
    except Exception as e:
        result["error"] = str(e)
    return result

def _bookings_callback_registered_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = [k for k in cb_map.keys() if "modal-booking.is_open" in str(k)]
        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No callback output found for modal-booking.is_open"
    except Exception as e:
        result["error"] = str(e)
    return result

def _reactive_dropdown_wiring_smoke():
    result = {"ok": False, "missing": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        keys = list(cb_map.keys())
        required_outputs = [
            "s-dept.options",
            "c-search.options",
            "c-search.value",
            "s-search.options",
            "s-search.value",
            "d-search.options",
            "d-search.value",
            "b-search.options",
            "b-search.value",
            "p-search.options",
            "p-search.value",
            "dept-search.options",
            "dept-search.value",
            "b-dept.options",
            "b-customer.options",
            "b-customer.value",
            "b-service.options",
            "b-service.value",
            "b-dress.options",
            "dress-section.style",
            "p-booking.options",
            "p-booking.value",
        ]
        missing = [needle for needle in required_outputs if not any(needle in str(k) for k in keys)]
        result["missing"] = missing
        result["ok"] = len(missing) == 0
    except Exception as e:
        result["error"] = str(e)
    return result

def _quick_add_customer_wiring_smoke():
    result = {"ok": False, "matches": [], "error": None}
    try:
        import app_dash

        cb_map = getattr(app_dash.app, "callback_map", {}) or {}
        matches = []
        for output_key, meta in cb_map.items():
            out_str = str(output_key)
            if "b-customer.options" not in out_str and "b-customer.value" not in out_str:
                continue
            inputs = meta.get("inputs", []) or []
            has_quick_add_input = any(
                str(i.get("id")) == "last-added-customer" and str(i.get("property")) == "data"
                for i in inputs
            )
            if has_quick_add_input:
                matches.append(out_str)

        result["matches"] = matches
        result["ok"] = len(matches) > 0
        if not result["ok"]:
            result["error"] = "No b-customer callback wired to last-added-customer.data"
    except Exception as e:
        result["error"] = str(e)
    return result
