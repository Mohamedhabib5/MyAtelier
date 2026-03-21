from dash import ALL, Input, Output, ctx, no_update


def register_mobile_card_callbacks(app):
    @app.callback(
        [
            Output("b-search", "value", allow_duplicate=True),
            Output("c-search", "value", allow_duplicate=True),
            Output("s-search", "value", allow_duplicate=True),
            Output("d-search", "value", allow_duplicate=True),
            Output("p-search", "value", allow_duplicate=True),
            Output("dept-search", "value", allow_duplicate=True),
        ],
        Input({"type": "mobile-select-row", "target": ALL, "value": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_mobile_row(_n_clicks):
        triggered_id = ctx.triggered_id
        if not isinstance(triggered_id, dict):
            return (no_update,) * 6

        target = triggered_id.get("target")
        value = triggered_id.get("value")
        outputs = {
            "b-search": no_update,
            "c-search": no_update,
            "s-search": no_update,
            "d-search": no_update,
            "p-search": no_update,
            "dept-search": no_update,
        }
        if target in outputs:
            outputs[target] = value

        return (
            outputs["b-search"],
            outputs["c-search"],
            outputs["s-search"],
            outputs["d-search"],
            outputs["p-search"],
            outputs["dept-search"],
        )
