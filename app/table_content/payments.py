import dash_bootstrap_components as dbc
import logic


def build_payments_table_content(load_data, create_dt, p_cols, payment_booking_action_label, viewport_mode="responsive"):
    df = load_data("payments.csv", p_cols)
    if df.empty:
        return dbc.Alert("لا توجد دفعات.", color="info")

    # Normalize payment date for display.
    if len(p_cols) >= 2 and p_cols[1] in df.columns:
        df[p_cols[1]] = df[p_cols[1]].apply(logic.format_date_ddmmyyyy)
    if "وصف الدفعة" in df.columns:
        df["وصف الدفعة"] = df["وصف الدفعة"].replace("", "دفعة حجز")
    if {"وصف الدفعة", "نوع الدفعة"}.issubset(df.columns):
        compensation_mask = df["نوع الدفعة"].astype(str).str.strip() == "custody_compensation"
        missing_label_mask = df["وصف الدفعة"].astype(str).str.strip() == ""
        df.loc[compensation_mask & missing_label_mask, "وصف الدفعة"] = "سند تعويض"

    preferred_cols = [
        "كود الدفع",
        "التاريخ",
        "وصف الدفعة",
        "كود الحجز",
        "القيمة المدفوعة",
        "اسم العروسه",
        "المتبقي بعد الدفعة",
        "مرجع سجل التسليم",
        "ملاحظات الدفع",
    ]
    display_cols = [col for col in preferred_cols if col in df.columns]
    df_view = df[display_cols].iloc[::-1].copy() if display_cols else df.iloc[::-1].copy()

    return create_dt(
        df_view,
        "payments-table",
        "payments.csv",
        action_buttons={
            "field": "__action__",
            "col_id": "view-booking-action",
            "label": payment_booking_action_label,
            "mobile_type": "view-booking",
            "mobile_color": "info",
            "header": "",
            "minWidth": 140,
            "maxWidth": 170,
        },
        row_id_field=p_cols[0] if p_cols else None,
        mobile_card_fields=["وصف الدفعة", p_cols[1], p_cols[3], p_cols[6]] if "وصف الدفعة" in df.columns else p_cols[1:4],
        mobile_title_field=p_cols[4] if len(p_cols) > 4 else (p_cols[0] if p_cols else None),
        mobile_select_target="p-search",
        viewport_mode=viewport_mode,
    )
