from datetime import date

import dash_bootstrap_components as dbc
from dash import Input, Output, State, ctx, html, no_update
from app.callbacks.feedback import success_toast


def register_customers_form_callbacks(
    app,
    load_data,
    c_cols,
    get_customers_table_content,
    logic_module,
    delete_reason,
):
    @app.callback(
        [
            Output("modal-customer", "is_open"),
            Output("c-modal-title", "children"),
            Output("c-name", "value"),
            Output("c-groom", "value"),
            Output("c-addr", "value"),
            Output("c-phone1", "value"),
            Output("c-phone2", "value"),
            Output("c-reg-date", "value"),
            Output("c-notes", "value"),
            Output("c-edit-id", "data"),
            Output("modal-delete-customer", "is_open"),
            Output("c-add-alert", "children"),
            Output("customers-table-container", "children"),
            Output("c-search", "value", allow_duplicate=True),
            Output("last-added-customer", "data"),
            Output("app-success-toast", "children", allow_duplicate=True),
            Output("app-success-toast", "is_open", allow_duplicate=True),
        ],
        [
            Input("btn-add-customer-modal", "n_clicks"),
            Input("btn-edit-customer", "n_clicks"),
            Input("btn-save-customer", "n_clicks"),
            Input("btn-delete-customer", "n_clicks"),
            Input("btn-cancel-delete", "n_clicks"),
            Input("btn-confirm-delete", "n_clicks"),
            Input("btn-quick-add-customer", "n_clicks"),
        ],
        [
            State("modal-customer", "is_open"),
            State("c-search", "value"),
            State("modal-delete-customer", "is_open"),
            State("c-name", "value"),
            State("c-groom", "value"),
            State("c-addr", "value"),
            State("c-phone1", "value"),
            State("c-phone2", "value"),
            State("c-reg-date", "value"),
            State("c-notes", "value"),
            State("c-edit-id", "data"),
        ],
        prevent_initial_call=True,
    )
    def manage_customers(
        n_add,
        _n_edit,
        _n_save,
        _n_del,
        n_cancel_del,
        _n_confirm_del,
        n_quick,
        is_modal_open,
        search_val,
        is_del_open,
        name,
        groom,
        addr,
        p1,
        p2,
        reg_date,
        notes,
        edit_id,
    ):
        ctx_id = ctx.triggered_id

        # 1. Open Add Modal
        if (ctx_id == "btn-add-customer-modal" and n_add) or (
            ctx_id == "btn-quick-add-customer" and n_quick
        ):
            return (
                True,
                "\u0625\u0636\u0627\u0641\u0629 \u0639\u0645\u064a\u0644\u0629 \u062c\u062f\u064a\u062f\u0629",
                "",
                "",
                "",
                "",
                "",
                date.today().isoformat(),
                "",
                None,
                False,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 2. Open Edit Modal
        if ctx_id == "btn-edit-customer" and search_val:
            df = load_data("customers.csv", c_cols)
            row = df[df["\u0643\u0648\u062f \u0627\u0644\u0639\u0645\u064a\u0644"] == search_val]
            if not row.empty:
                r = row.iloc[0]
                return (
                    True,
                    "\u062a\u0639\u062f\u064a\u0644 \u0628\u064a\u0627\u0646\u0627\u062a: "
                    + str(r["\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0647"]),
                    r["\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u0648\u0633\u0647"],
                    r["\u0627\u0633\u0645 \u0627\u0644\u0639\u0631\u064a\u0633"],
                    r["\u0627\u0644\u0639\u0646\u0648\u0627\u0646"],
                    r["\u062a\u0644\u064a\u0641\u0648\u0646 1"],
                    r["\u062a\u0644\u064a\u0641\u0648\u0646 2"],
                    r["\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u062a\u0633\u062c\u064a\u0644"],
                    r["\u0645\u0644\u0627\u062d\u0638\u0627\u062a"],
                    search_val,
                    False,
                    "",
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

        # 3. Save Logic
        if ctx_id == "btn-save-customer":
            if not name or not groom or not p1:
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert(
                        "\u26a0\ufe0f \u064a\u0631\u062c\u0649 \u0645\u0644\u0621 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u0623\u0633\u0627\u0633\u064a\u0629 (\u0627\u0644\u0627\u0633\u0645\u060c \u0627\u0644\u0639\u0631\u064a\u0633\u060c \u0627\u0644\u0647\u0627\u062a\u0641)",
                        color="warning",
                    ),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Edit Mode
            if edit_id:
                success, msg = logic_module.update_customer(
                    edit_id, name, groom, p1, p2, addr, reg_date, notes
                )
                if success:
                    return (
                        False,
                        no_update,
                        "",
                        "",
                        "",
                        "",
                        "",
                        date.today().isoformat(),
                        "",
                        None,
                        False,
                        "",
                        get_customers_table_content(),
                        None,
                        no_update,
                        *success_toast(f"\u2705 {msg}"),
                    )
                return (
                    True,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    dbc.Alert(f"\u274c {msg}", color="danger"),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            # Add Mode
            success, msg, _new_id = logic_module.add_customer(
                name, groom, p1, p2, addr, reg_date, notes
            )
            if success:
                return (
                    False,
                    no_update,
                    "",
                    "",
                    "",
                    "",
                    "",
                    date.today().isoformat(),
                    "",
                    None,
                    False,
                    "",
                    get_customers_table_content(),
                    None,
                    name,
                    *success_toast(f"\u2705 {msg}"),
                )

            # Failure: Keep Open, Show Error
            return (
                True,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                dbc.Alert(f"\u274c {msg}", color="danger"),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 4. Open Delete Modal
        if ctx_id == "btn-delete-customer":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                True,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 5. Confirm Delete
        if ctx_id == "btn-confirm-delete":
            if search_val:
                ok, msg = logic_module.delete_customer(search_val)
                if ok:
                    return (
                        False,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                        False,
                        "",
                        get_customers_table_content(),
                        None,
                        no_update,
                        *success_toast("\u2705 \u062a\u0645 \u062d\u0630\u0641 \u0627\u0644\u0639\u0645\u064a\u0644 \u0628\u0646\u062c\u0627\u062d"),
                    )
                alert = dbc.Alert(
                    f"\u274c \u0644\u0627 \u064a\u0645\u0643\u0646 \u062d\u0630\u0641 \u0627\u0644\u0639\u0645\u064a\u0644: {delete_reason(msg)}",
                    color="danger",
                )
                return (
                    False,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    False,
                    "",
                    html.Div([alert, get_customers_table_content()]),
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # 6. Cancel Delete
        if ctx_id == "btn-cancel-delete":
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                False,
                "",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        return (
            is_modal_open,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            is_del_open,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )
