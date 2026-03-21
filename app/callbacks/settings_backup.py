import os
import subprocess

import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, no_update

from app.services.backup_service import create_backup_snapshot


def register_settings_backup_callbacks(app):
    @app.callback(
        Output("backup-alert", "children"),
        Output("backup-download", "data"),
        Input("btn-create-backup", "n_clicks"),
        prevent_initial_call=True,
    )
    def create_manual_backup(n_clicks):
        if not n_clicks:
            return no_update, no_update
        try:
            result = create_backup_snapshot(label="manual", include_zip=True)
            warning_line = []
            if result.get("warnings"):
                warning_line = [
                    html.Div(
                        f"\u062a\u062d\u0630\u064a\u0631\u0627\u062a \u0627\u0644\u0646\u0633\u062e: {len(result['warnings'])}"
                    )
                ]
            zip_path = result.get("zip_path")
            if not zip_path:
                return (
                    dbc.Alert(
                        [
                            html.Div("\u2705 \u062a\u0645\u062a \u0625\u0646\u0634\u0627\u0621 \u0646\u0633\u062e\u0629 \u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629 \u0628\u0646\u062c\u0627\u062d."),
                            html.Div(f"\u0627\u0644\u0645\u062c\u0644\u062f: {result['snapshot_dir']}"),
                            html.Div("\u062a\u0639\u0630\u0631 \u0625\u0646\u0634\u0627\u0621 \u0645\u0644\u0641 ZIP \u0644\u0644\u062a\u0646\u0632\u064a\u0644."),
                            *warning_line,
                        ],
                        color="warning",
                    ),
                    no_update,
                )
            return (
                dbc.Alert(
                    [
                        html.Div("\u2705 \u062a\u0645\u062a \u0625\u0646\u0634\u0627\u0621 \u0646\u0633\u062e\u0629 \u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629 \u0628\u0646\u062c\u0627\u062d."),
                        html.Div(f"\u0627\u0644\u0645\u062c\u0644\u062f: {result['snapshot_dir']}"),
                        html.Div(f"\u0627\u0644\u0645\u0644\u0641 \u0627\u0644\u0645\u0636\u063a\u0648\u0637: {zip_path}"),
                        html.Div("\u062c\u0627\u0631\u064a \u062a\u0646\u0632\u064a\u0644 \u0627\u0644\u0646\u0633\u062e\u0629 \u0627\u0644\u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629..."),
                        *warning_line,
                    ],
                    color="success",
                ),
                dcc.send_file(zip_path),
            )
        except Exception as e:
            return (
                dbc.Alert(
                    f"\u274c \u0641\u0634\u0644 \u0625\u0646\u0634\u0627\u0621 \u0627\u0644\u0646\u0633\u062e\u0629 \u0627\u0644\u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629: {e}",
                    color="danger",
                ),
                no_update,
            )

    @app.callback(
        Output("backup-open-alert", "children"),
        Input("btn-open-backups", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_backups_folder(n_clicks):
        if not n_clicks:
            return no_update
        try:
            backup_dir = os.path.abspath("backups")
            if os.name == "nt":
                os.startfile(backup_dir)  # type: ignore[attr-defined]
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", backup_dir])
            else:
                subprocess.Popen(["open", backup_dir])
            return dbc.Alert(
                f"\u062a\u0645 \u0641\u062a\u062d \u0645\u062c\u0644\u062f \u0627\u0644\u0646\u0633\u062e: {backup_dir}",
                color="success",
            )
        except Exception as e:
            return dbc.Alert(
                f"\u062a\u0639\u0630\u0631 \u0641\u062a\u062d \u0645\u062c\u0644\u062f \u0627\u0644\u0646\u0633\u062e: {e}",
                color="warning",
            )
