from datetime import date
import time

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_bookings(check_departments, get_bookings_table_content):
    nonce = str(time.time_ns())
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3("\u0625\u062f\u0627\u0631\u0629 \u0627\u0644\u062d\u062c\u0648\u0632\u0627\u062a"), xs=12, md=6),
                    dbc.Col(
                        dbc.Button("\u062d\u062c\u0632 \u062c\u062f\u064a\u062f", id="btn-add-booking-modal", color="primary", className="page-action-btn", n_clicks=0, key=f"btn-add-booking-modal-{nonce}"),
                        xs=12,
                        md=6,
                        className="text-md-end",
                    ),
                ],
                className="align-items-center g-3 mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id="b-search",
                                            placeholder="\u0627\u0628\u062d\u062b \u0639\u0646 \u062d\u062c\u0632 (\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0629 / \u0627\u0644\u0643\u0648\u062f)...",
                                            options=[],
                                            searchable=True,
                                        ),
                                        xs=12,
                                        md=8,
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            [
                                            dbc.Button(
                                                "\u062a\u0639\u062f\u064a\u0644",
                                                id="btn-edit-booking",
                                                color="warning",
                                                className="me-2",
                                                disabled=True,
                                                n_clicks=0,
                                                key=f"btn-edit-booking-{nonce}",
                                            ),
                                            dbc.Button(
                                                "\u062d\u0630\u0641",
                                                id="btn-delete-booking",
                                                color="danger",
                                                disabled=True,
                                                n_clicks=0,
                                                key=f"btn-delete-booking-{nonce}",
                                            ),
                                            ],
                                            className="toolbar-actions",
                                        ),
                                        xs=12,
                                        md=4,
                                    ),
                                ],
                                className="g-3 align-items-start",
                            )
                        ]
                    )
                ],
                className="mb-4 dropdown-card",
            ),
            dcc.Store(id="b-edit-id", data=None),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("\u062a\u0623\u0643\u064a\u062f \u0627\u0644\u062d\u0630\u0641")),
                    dbc.ModalBody("\u0647\u0644 \u0623\u0646\u062a \u0645\u062a\u0623\u0643\u062f \u0645\u0646 \u0625\u0644\u063a\u0627\u0621 \u0647\u0630\u0627 \u0627\u0644\u062d\u062c\u0632\u061f"),
                    dbc.ModalFooter(
                        [
                            dbc.Button("\u062a\u0631\u0627\u062c\u0639", id="btn-cancel-delete-b", className="ms-auto", n_clicks=0, key=f"btn-cancel-delete-b-{nonce}"),
                            dbc.Button("\u062d\u0630\u0641", id="btn-confirm-delete-b", color="danger", n_clicks=0, key=f"btn-confirm-delete-b-{nonce}"),
                        ]
                    ),
                ],
                id="modal-delete-booking",
                is_open=False,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="b-modal-title", children="\u062a\u0633\u062c\u064a\u0644 \u062d\u062c\u0632 \u062c\u062f\u064a\u062f")),
                    dbc.ModalBody(
                        [
                            # Keep booking alerts at top so rejection reason is always visible.
                            html.Div(id="b-alert", className="mb-3"),
                            dbc.Label("\u0627\u0644\u0642\u0633\u0645"),
                            dcc.Dropdown(
                                id="b-dept",
                                options=[{"label": d, "value": d} for d in check_departments()["department_name"]],
                                placeholder="\u0627\u062e\u062a\u0631 \u0627\u0644\u0642\u0633\u0645...",
                                className="mb-3",
                                searchable=True,
                            ),
                            dbc.Label("\u0627\u0644\u0639\u0631\u0648\u0633\u0629"),
                            dbc.InputGroup(
                                [
                                    dcc.Dropdown(
                                        id="b-customer",
                                        placeholder="\u0627\u062e\u062a\u0631 \u0627\u0644\u0639\u0631\u0648\u0633\u0629...",
                                        style={"flex": "1"},
                                        searchable=True,
                                    ),
                                    dbc.Button("+", id="btn-quick-add-customer", color="success", outline=True),
                                ],
                                className="mb-3 d-flex",
                            ),
                            dbc.Label("\u0627\u0644\u062e\u062f\u0645\u0629"),
                            dcc.Dropdown(
                                id="b-service",
                                placeholder="\u0627\u062e\u062a\u0631 \u0627\u0644\u062e\u062f\u0645\u0629...",
                                className="mb-3",
                                searchable=True,
                            ),
                            html.Div(
                                [
                                    dbc.Label("\u0643\u0648\u062f \u0627\u0644\u0641\u0633\u062a\u0627\u0646"),
                                    dcc.Dropdown(
                                        id="b-dress",
                                        placeholder="\u0627\u062e\u062a\u0631 \u0627\u0644\u0641\u0633\u062a\u0627\u0646...",
                                        className="mb-3",
                                        searchable=True,
                                    ),
                                ],
                                id="dress-section",
                                style={"display": "none"},
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [dbc.Label("\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u062d\u062c\u0632"), dcc.DatePickerSingle(id="b-date", date=date.today().isoformat(), display_format="YYYY-MM-DD")],
                                        xs=12,
                                        md=6,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0645\u0646\u0627\u0633\u0628\u0629"),
                                            dcc.DatePickerSingle(id="b-event-date", date=date.today().isoformat(), display_format="YYYY-MM-DD"),
                                        ],
                                        xs=12,
                                        md=6,
                                    ),
                                ],
                                className="g-3 mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col([dbc.Label("\u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0645\u062a\u0641\u0642"), dbc.Input(id="b-price", type="number")], xs=12, md=6),
                                    dbc.Col(
                                        [
                                            dbc.Label("\u0627\u0644\u0639\u0631\u0628\u0648\u0646"),
                                            dbc.Input(id="b-paid", type="number", placeholder="\u0627\u0644\u0639\u0631\u0628\u0648\u0646 \u0627\u0644\u0645\u062f\u0641\u0648\u0639"),
                                        ],
                                        xs=12,
                                        md=6,
                                    ),
                                ],
                                className="g-3 mb-3",
                            ),
                            dbc.Label("\u062d\u0627\u0644\u0629 \u0627\u0644\u062d\u062c\u0632"),
                            dcc.Dropdown(
                                id="b-status",
                                options=[
                                    {"label": "\u0646\u0634\u0637", "value": "\u0646\u0634\u0637"},
                                    {"label": "\u0645\u0643\u062a\u0645\u0644", "value": "\u0645\u0643\u062a\u0645\u0644"},
                                    {"label": "\u0645\u0644\u063a\u064a", "value": "\u0645\u0644\u063a\u064a"},
                                ],
                                value="\u0646\u0634\u0637",
                                className="mb-3",
                            ),
                            dbc.Textarea(id="b-notes", placeholder="\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u0644\u062d\u062c\u0632"),
                        ]
                    ),
                    dbc.ModalFooter(dbc.Button("\u062a\u0623\u0643\u064a\u062f \u0627\u0644\u062d\u062c\u0632", id="btn-save-booking", color="success", className="page-action-btn", n_clicks=0, key=f"btn-save-booking-{nonce}")),
                ],
                id="modal-booking",
                is_open=False,
                fullscreen="md-down",
                scrollable=True,
                className="form-modal",
            ),
            html.Div(id="bookings-table-container", children=get_bookings_table_content()),
        ]
    )
