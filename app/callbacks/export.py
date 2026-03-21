from dash import Input, Output, MATCH


def register_export_callbacks(app):
    @app.callback(
        Output({"type": "grid", "index": MATCH}, "exportDataAsCsv"),
        Input({"type": "export-btn", "index": MATCH}, "n_clicks"),
        prevent_initial_call=True,
    )
    def export_table_as_csv(_n_clicks):
        return True
