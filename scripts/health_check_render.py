from health_check_context import *

def _layout_render_smoke():
    result = {"ok": False, "error": None}
    try:
        import app_dash

        app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        result["ok"] = True
    except Exception as e:
        result["error"] = str(e)
    return result

def _count_components(node):
    if node is None or isinstance(node, (str, int, float, bool)):
        return 0
    if isinstance(node, (list, tuple)):
        return sum(_count_components(item) for item in node)

    total = 1
    children = getattr(node, "children", None)
    if children is not None:
        total += _count_components(children)
    return total

def _performance_baseline_smoke():
    result = {"ok": False, "error": None}
    try:
        import app_dash

        start = time.perf_counter()
        layout = app_dash.main_layout(
            {
                "logged_in": True,
                "username": "admin",
                "full_name": "admin",
                "role": "admin",
            }
        )
        elapsed = time.perf_counter() - start
        payload = json.dumps(layout, cls=PlotlyJSONEncoder, ensure_ascii=False)
        callback_map = getattr(app_dash.app, "callback_map", {}) or {}
        active_tab_callbacks = sum(
            1
            for meta in callback_map.values()
            if any(
                str(item.get("id")) == "main-tabs" and str(item.get("property")) == "active_tab"
                for item in (meta.get("inputs", []) or [])
            )
        )
        result.update(
            {
                "ok": True,
                "main_layout_seconds": round(elapsed, 4),
                "payload_bytes": len(payload.encode("utf-8")),
                "component_count": _count_components(layout),
                "active_tab_callback_inputs": active_tab_callbacks,
            }
        )
    except Exception as e:
        result["error"] = str(e)
    return result
