import dash_bootstrap_components as dbc


NEXT_ACTION_LABEL = "الإجراء التالي"


def _to_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def _dress_label(value):
    text = str(value or "").strip()
    return text if text else "بدون فستان"


def _display_status(row):
    status = str(row.get("حالة الدورة", "") or "").strip()
    service_status = str(row.get("حالة المغسلة والصيانة", "") or "").strip()
    if status == "في المغسلة والصيانة" and service_status:
        return f"{status} - {service_status}"
    return status


def build_dress_custody_table_content(load_data, create_dt, dc_cols, viewport_mode="responsive"):
    df = load_data("dress_custody.csv", dc_cols)
    if df.empty:
        return dbc.Alert("لا توجد سجلات تسليم واستلام حتى الآن.", color="info")

    if {"قيمة التأمين", "التأمين المردود", "التأمين المعتمد للتعويض"}.issubset(df.columns):
        df["الالتزام المفتوح"] = df.apply(
            lambda row: _to_float(row["قيمة التأمين"]) - _to_float(row["التأمين المردود"]) - _to_float(row["التأمين المعتمد للتعويض"]),
            axis=1,
        )
    if {"التأمين المعتمد للتعويض", "تعويض إضافي محصل"}.issubset(df.columns):
        df["إجمالي سند التعويض"] = df.apply(
            lambda row: _to_float(row["التأمين المعتمد للتعويض"]) + _to_float(row["تعويض إضافي محصل"]),
            axis=1,
        )

    if "كود الفستان" in df.columns:
        df["الفستان / العهدة"] = df["كود الفستان"].apply(_dress_label)
    if "حالة الدورة" in df.columns:
        df["الحالة الحالية"] = df.apply(_display_status, axis=1)

    preferred_cols = [
        "كود السجل",
        "كود الحجز",
        "اسم العروسه",
        "الفستان / العهدة",
        "الحالة الحالية",
        "قيمة التأمين",
        "نوع الضمان",
        "مرجع الضمان",
        "إجمالي سند التعويض",
        "ملاحظات التسوية",
    ]
    display_cols = [col for col in preferred_cols if col in df.columns]
    df_view = df[display_cols].iloc[::-1].copy()

    return create_dt(
        df_view,
        "dress-custody-table",
        "dress_custody.csv",
        action_buttons={
            "field": "__action__",
            "col_id": "custody-next-action",
            "label": NEXT_ACTION_LABEL,
            "mobile_type": "custody-next-action",
            "mobile_color": "primary",
            "header": "",
            "minWidth": 140,
            "maxWidth": 170,
        },
        row_id_field="كود السجل",
        mobile_card_fields=[
            "الحالة الحالية",
            "قيمة التأمين",
            "إجمالي سند التعويض",
            "نوع الضمان",
        ],
        mobile_title_field="اسم العروسه",
        mobile_select_target="dc-search",
        viewport_mode=viewport_mode,
    )
