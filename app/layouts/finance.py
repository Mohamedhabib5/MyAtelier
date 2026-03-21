import dash_bootstrap_components as dbc
from dash import dcc, html


def layout_finance():
    return html.Div(
        [
            html.H3("\U0001F4CA \u0627\u0644\u062a\u0642\u0627\u0631\u064a\u0631 \u0627\u0644\u0645\u0627\u0644\u064a\u0629"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u062f\u062e\u0644",
                                            className="card-title",
                                        ),
                                        html.H2(id="kpi-income", className="text-success"),
                                    ]
                                )
                            ]
                        ),
                        xs=12,
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "\u0627\u0644\u0645\u0633\u062a\u062d\u0642\u0627\u062a (\u0645\u062a\u0628\u0642\u064a)",
                                            className="card-title",
                                        ),
                                        html.H2(id="kpi-remaining", className="text-warning"),
                                    ]
                                )
                            ]
                        ),
                        xs=12,
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "\u0625\u062c\u0645\u0627\u0644\u064a \u0627\u0644\u062d\u062c\u0648\u0632\u0627\u062a",
                                            className="card-title",
                                        ),
                                        html.H2(id="kpi-bookings", className="text-primary"),
                                    ]
                                )
                            ]
                        ),
                        xs=12,
                        lg=4,
                    ),
                ],
                className="g-3 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id="chart-income-daily", config={"responsive": True, "displayModeBar": False}))),
                        xs=12,
                        className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id="chart-dept-income", config={"responsive": True, "displayModeBar": False}))),
                        xs=12,
                        lg=6,
                        className="mb-4 mb-lg-0",
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id="chart-top-services", config={"responsive": True, "displayModeBar": False}))),
                        xs=12,
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
        ]
    )
