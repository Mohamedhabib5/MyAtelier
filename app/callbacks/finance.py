import pandas as pd
import plotly.express as px
from dash import Input, Output, no_update


def _apply_common_figure_style(fig, *, legend_horizontal=False):
    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin={"l": 16, "r": 16, "t": 56, "b": 40},
        font={"family": "Cairo, sans-serif"},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        title={"x": 0.98, "xanchor": "right"},
    )
    if legend_horizontal:
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5,
            }
        )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def register_finance_callbacks(app, load_data, p_cols, b_cols):
    @app.callback(
        [
            Output("kpi-income", "children"),
            Output("kpi-remaining", "children"),
            Output("kpi-bookings", "children"),
            Output("chart-income-daily", "figure"),
            Output("chart-dept-income", "figure"),
            Output("chart-top-services", "figure"),
        ],
        Input("main-tabs", "active_tab"),
    )
    def update_finance_dashboard(active_tab):
        if active_tab != "tab-finance":
            return no_update, no_update, no_update, no_update, no_update, no_update

        p_df = load_data("payments.csv", p_cols)
        b_df = load_data("bookings.csv", b_cols)

        total_income = (
            p_df["القيمة المدفوعة"].astype(float).sum()
            if not p_df.empty
            else 0
        )
        total_remaining = (
            b_df["المتبقي"].astype(float).sum()
            if not b_df.empty
            else 0
        )
        total_bookings = len(b_df)

        fig_daily = {}
        if not p_df.empty:
            p_df["التاريخ"] = pd.to_datetime(p_df["التاريخ"])
            p_df["القيمة المدفوعة"] = pd.to_numeric(
                p_df["القيمة المدفوعة"], errors="coerce"
            ).fillna(0)
            daily = p_df.groupby("التاريخ")["القيمة المدفوعة"].sum().reset_index()
            fig_daily = px.bar(
                daily,
                x="التاريخ",
                y="القيمة المدفوعة",
                title="الدخل اليومي",
            )
            _apply_common_figure_style(fig_daily)

        fig_dept = {}
        if not b_df.empty and not p_df.empty:
            merged = p_df.merge(b_df[["كود الحجز", "القسم"]], on="كود الحجز", how="left")
            if not merged.empty:
                merged["القيمة المدفوعة"] = pd.to_numeric(
                    merged["القيمة المدفوعة"], errors="coerce"
                ).fillna(0)
                dept_income = (
                    merged.groupby("القسم")["القيمة المدفوعة"].sum().reset_index()
                )
                fig_dept = px.pie(
                    dept_income,
                    values="القيمة المدفوعة",
                    names="القسم",
                    title="توزيع الدخل حسب القسم",
                    hole=0.4,
                )
                _apply_common_figure_style(fig_dept, legend_horizontal=True)

        fig_serv = {}
        if not b_df.empty:
            top_serv = b_df["الخدمة"].value_counts().head(5).reset_index()
            top_serv.columns = ["الخدمة", "عدد الحجوزات"]
            fig_serv = px.bar(
                top_serv,
                x="عدد الحجوزات",
                y="الخدمة",
                orientation="h",
                title="أكثر الخدمات طلباً",
            )
            _apply_common_figure_style(fig_serv)

        return (
            f"{total_income:,.0f} جم",
            f"{total_remaining:,.0f} جم",
            f"{total_bookings}",
            fig_daily,
            fig_dept,
            fig_serv,
        )
