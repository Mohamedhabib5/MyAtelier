import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Atelier Pro Accounting", layout="wide")

IMAGE_FOLDER = "dress_images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# --- 2. دوال إدارة البيانات ---
def load_data(file_name, columns):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, dtype=str)
        df = df.fillna("")
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]
    return pd.DataFrame(columns=columns)

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# تعريف الأعمدة
C_COLS = ["كود العميل", "تاريخ التسجيل", "اسم العروسه", "اسم العريس",
          "العنوان", "تليفون 1", "تليفون 2", "ملاحظات"]

S_COLS = ["كود الخدمة", "القسم", "اسم الخدمة", "السعر المقترح"]

D_COLS = ["كود الفستان", "نوع الفستان", "تاريخ الشراء",
          "وصف الفستان", "صورة الفستان", "حالة الفستان"]

B_COLS = ["كود الحجز", "تاريخ الحجز", "اسم العروسه", "القسم",
          "الخدمة", "كود الفستان", "تاريخ المناسبة",
          "السعر المتفق", "المدفوع", "المتبقي", "ملاحظات الحجز"]

P_COLS = ["كود الدفع", "التاريخ", "كود الحجز", "القيمة المدفوعة",
          "اسم العروسه", "اسم العريس", "المتبقي بعد الدفعة", "ملاحظات الدفع"]

# تحميل الجداول
customers_df = load_data("customers.csv", C_COLS)
services_df = load_data("services.csv", S_COLS)
dresses_df = load_data("dresses.csv", D_COLS)
bookings_df = load_data("bookings.csv", B_COLS)
payments_df = load_data("payments.csv", P_COLS)

# --- 3. تصميم الواجهة ---
st.title("Atelier Management System 👗")
tabs = st.tabs(["👥 العملاء", "📋 الخدمات", "👗 الفساتين",
                "📝 الحجوزات", "💰 المدفوعات", "📊 المالية"])

# --- 1. تبويب العملاء ---
with tabs[0]:
    st.header("سجل العملاء")

    with st.expander("➕ إضافة عميلة جديدة"):
        with st.form("c_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            reg_date = col1.date_input("تاريخ التسجيل", date.today())
            name = col2.text_input("اسم العروسه *")
            groom = col1.text_input("اسم العريس *")
            addr = col2.text_input("العنوان *")
            phone = col1.text_input("رقم تليفون 1 *")
            phone2 = col2.text_input("رقم تليفون 2 *")
            notes = st.text_area("ملاحظات")

            if st.form_submit_button("حفظ العميلة"):
                if name and groom and phone and addr:
                    new_id = f"C-{len(customers_df)+101}"
                    new_row = [new_id, str(reg_date), name, groom,
                               addr, phone, phone2, notes]
                    customers_df.loc[len(customers_df)] = new_row
                    save_data(customers_df, "customers.csv")
                    st.success("تم تسجيل العميلة بنجاح ✅")
                    st.rerun()
                else:
                    st.error("جميع الخانات التي تحتوي على * مطلوبة")

    st.dataframe(
        customers_df.iloc[::-1],
        use_container_width=True,
        hide_index=True
    )

# --- 2. الخدمات ---
with tabs[1]:
    st.header("منيو الخدمات")

    with st.expander("➕ إضافة خدمة"):
        with st.form("s_form", clear_on_submit=True):
            s_dept = st.selectbox(
                "القسم",
                ["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"]
            )
            s_name = st.text_input("اسم الخدمة")
            s_price = st.number_input("السعر المقترح", min_value=0)

            if st.form_submit_button("حفظ"):
                new_s = [f"S-{len(services_df)+101}", s_dept, s_name, s_price]
                services_df.loc[len(services_df)] = new_s
                save_data(services_df, "services.csv")
                st.rerun()

    st.table(services_df)

# --- 3. الفساتين ---
with tabs[2]:
    st.header("كتالوج الفساتين المصور")

    with st.expander("➕ إضافة فستان جديد"):
        with st.form("dress_form", clear_on_submit=True):
            col_d1, col_d2 = st.columns(2)

            with col_d1:
                d_code = st.text_input("كود الفستان *")
                d_category = st.selectbox(
                    "نوع الفستان",
                    ["زفاف", "سواريه", "غير محدد"]
                )
                d_purchase_date = st.date_input("تاريخ الشراء *", date.today())

            with col_d2:
                d_status = st.selectbox(
                    "حالة الفستان",
                    ["متاح", "محجوز", "في المغسلة", "تحت التصليح"]
                )

            uploaded_file = st.file_uploader(
                "صورة الفستان (اختياري)",
                type=["png", "jpg", "jpeg"]
            )
            d_desc = st.text_area("وصف الفستان *")

            if st.form_submit_button("حفظ الفستان"):
                if d_code and d_desc and d_purchase_date:
                    img_path = ""
                    if uploaded_file:
                        img_path = os.path.join(IMAGE_FOLDER, f"{d_code}.jpg")
                        Image.open(uploaded_file).save(img_path)

                    new_dress = [
                        d_code,
                        d_category,
                        str(d_purchase_date),
                        d_desc,
                        img_path,
                        d_status,
                    ]
                    dresses_df.loc[len(dresses_df)] = new_dress
                    save_data(dresses_df, "dresses.csv")
                    st.success(f"✅ تم حفظ الفستان {d_code}!")
                    st.rerun()
                else:
                    st.error("الكود والوصف وتاريخ الشراء مطلوبين")

    st.dataframe(
        dresses_df,
        column_config={
            "صورة الفستان": st.column_config.ImageColumn(),
            "تاريخ الشراء": st.column_config.DateColumn(),
        },
        use_container_width=True,
        hide_index=True,
    )

# --- 4. الحجوزات ---
with tabs[3]:
    st.header("📝 تسجيل حجز جديد")

    b_dept_choice = st.selectbox(
        "اختر القسم لبدء الحجز",
        ["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"],
        key="booking_dept",
    )
    is_dress = b_dept_choice == "الفساتين"

    with st.form("booking_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        b_cust = c1.selectbox(
            "العروسه",
            customers_df["اسم العروسه"].tolist() if not customers_df.empty else [""],
        )

        filtered_services = services_df[
            services_df["القسم"] == b_dept_choice
        ]["اسم الخدمة"].tolist()
        b_service = c2.selectbox(
            "الخدمة",
            filtered_services if filtered_services else ["لا يوجد خدمات"],
        )

        b_dress = c1.selectbox(
            "الفستان",
            ["بدون فستان"] + dresses_df["كود الفستان"].tolist(),
            disabled=not is_dress,
        )

        b_reg_date = c2.date_input("تاريخ تسجيل الحجز", date.today())
        b_event_date = c1.date_input("تاريخ المناسبة (يوم التنفيذ)")
        b_price = c2.number_input("السعر المتفق عليه", min_value=0)
        b_paid = c1.number_input("العربون المدفوع الآن", min_value=0)
        b_notes = st.text_area("ملاحظات الحجز")

        if st.form_submit_button("تأكيد الحجز"):
            errors = []

            # التحقق من الخانات الإلزامية (كلها ما عدا ملاحظات الحجز)
            if not b_cust:
                errors.append("حقل 'العروسه' مطلوب.")
            if not b_service or b_service == "لا يوجد خدمات":
                errors.append("حقل 'الخدمة' مطلوب.")
            if is_dress and (not b_dress or b_dress == "بدون فستان"):
                errors.append("يجب اختيار فستان عند اختيار قسم الفساتين.")
            if not b_reg_date:
                errors.append("حقل 'تاريخ تسجيل الحجز' مطلوب.")
            if not b_event_date:
                errors.append("حقل 'تاريخ المناسبة (يوم التنفيذ)' مطلوب.")
            if b_price is None or b_price <= 0:
                errors.append("حقل 'السعر المتفق عليه' يجب أن يكون أكبر من صفر.")
            if b_paid is None or b_paid < 0:
                errors.append("حقل 'العربون المدفوع الآن' لا يمكن أن يكون سالب.")

            # قيود محاسبية
            if b_paid is not None and b_price is not None:
                if b_paid > b_price:
                    errors.append(
                        f"لا يمكن دفع عربون ({b_paid}) أكبر من السعر الكلي ({b_price})."
                    )

            # تعارض الفستان مع حجز آخر في نفس التاريخ
            if is_dress and b_dress and b_dress != "بدون فستان":
                conflict = bookings_df[
                    (bookings_df["كود الفستان"] == b_dress)
                    & (bookings_df["تاريخ المناسبة"] == str(b_event_date))
                ]
                if not conflict.empty:
                    errors.append("الفستان محجوز في هذا التاريخ.")

            # عرض الأخطاء بدون مسح المدخلات
            if errors:
                for e in errors:
                    st.error(e)
            else:
                prefix = {
                    "الميكب": "MK",
                    "الفساتين": "D",
                    "الشعر": "H",
                    "التصوير": "PH",
                    "البشره": "S",
                }[b_dept_choice]

                b_id = f"{prefix}-{int(datetime.now().timestamp())}"
                rem = float(b_price) - float(b_paid)

                new_booking = [
                    b_id,
                    str(b_reg_date),
                    b_cust,
                    b_dept_choice,
                    b_service,
                    b_dress,
                    str(b_event_date),
                    b_price,
                    b_paid,
                    rem,
                    b_notes,
                ]
                bookings_df.loc[len(bookings_df)] = new_booking
                save_data(bookings_df, "bookings.csv")

                if b_paid > 0:
                    p_id = f"PAY-{int(datetime.now().timestamp())}"
                    cust_row = customers_df[
                        customers_df["اسم العروسه"] == b_cust
                    ].iloc[0]
                    new_pay = [
                        p_id,
                        str(b_reg_date),
                        b_id,
                        b_paid,
                        b_cust,
                        cust_row["اسم العريس"],
                        rem,
                        "عربون حجز",
                    ]
                    payments_df.loc[len(payments_df)] = new_pay
                    save_data(payments_df, "payments.csv")

                st.success("تم الحجز بنجاح ✅")
                st.rerun()

    st.dataframe(
        bookings_df.iloc[::-1],
        column_config={
            "تاريخ الحجز": st.column_config.DateColumn(),
            "تاريخ المناسبة": st.column_config.DateColumn(),
        },
        use_container_width=True,
        hide_index=True,
    )

# --- 5. المدفوعات ---
with tabs[4]:
    st.header("💰 تسجيل وتتبع المدفوعات")

    if not bookings_df.empty:
        with st.expander("💵 إضافة دفعة مالية جديدة"):
            cust_list = customers_df.apply(
                lambda x: f"{x['اسم العروسه']} | {x['اسم العريس']}",
                axis=1,
            ).tolist()

            selected_cust_full = st.selectbox(
                "ابحث عن العروسة أو العريس",
                cust_list,
            )
            bride_name_only = selected_cust_full.split(" | ")[0]

            client_b = bookings_df[
                bookings_df["اسم العروسه"] == bride_name_only
            ]

            if not client_b.empty:
                b_options = client_b.apply(
                    lambda x: f"{x['كود الحجز']} - {x['الخدمة']} (باقي: {x['المتبقي']})",
                    axis=1,
                ).tolist()

                selected_b_str = st.selectbox(
                    "اختر الخدمة للدفع",
                    b_options,
                )
                target_b_id = selected_b_str.split(" - ")[0]
                target_b_row = bookings_df[
                    bookings_df["كود الحجز"] == target_b_id
                ].iloc[0]

                with st.form("pay_form"):
                    p_date = st.date_input(
                        "تاريخ استلام الدفعة",
                        date.today(),
                    )
                    p_amt = st.number_input(
                        "المبلغ المدفوع الآن",
                        min_value=0,
                    )
                    p_msg = st.text_input("ملاحظات الدفع")

                    if st.form_submit_button("تأكيد الدفع"):
                        remaining_on_booking = float(target_b_row["المتبقي"])

                        errors = []
                        if p_amt > remaining_on_booking:
                            errors.append(
                                f"المبلغ المدفوع ({p_amt}) أكبر من المبلغ المتبقي على هذا الحجز ({remaining_on_booking})."
                            )
                        if p_amt <= 0:
                            errors.append(
                                "يجب إدخال مبلغ أكبر من الصفر."
                            )

                        if errors:
                            for e in errors:
                                st.error(e)
                        else:
                            p_id = f"PAY-{int(datetime.now().timestamp())}"
                            new_rem = remaining_on_booking - p_amt

                            groom_name = customers_df[
                                customers_df["اسم العروسه"]
                                == bride_name_only
                            ].iloc[0]["اسم العريس"]

                            new_p = [
                                p_id,
                                str(p_date),
                                target_b_id,
                                p_amt,
                                bride_name_only,
                                groom_name,
                                new_rem,
                                p_msg,
                            ]
                            payments_df.loc[len(payments_df)] = new_p
                            save_data(payments_df, "payments.csv")

                            bookings_df.loc[
                                bookings_df["كود الحجز"] == target_b_id,
                                "المدفوع",
                            ] = str(
                                float(target_b_row["المدفوع"]) + p_amt
                            )
                            bookings_df.loc[
                                bookings_df["كود الحجز"] == target_b_id,
                                "المتبقي",
                            ] = str(new_rem)
                            save_data(bookings_df, "bookings.csv")

                            st.success("تم تسجيل الدفعة بنجاح ✅")
                            st.rerun()

    st.dataframe(
        payments_df.iloc[::-1],
        column_config={"التاريخ": st.column_config.DateColumn()},
        use_container_width=True,
        hide_index=True,
    )

# --- 6. المالية ---
with tabs[5]:
    st.header("📊 التقرير المالي")

    if not bookings_df.empty:
        b_calc = bookings_df.copy()
        b_calc["السعر المتفق"] = pd.to_numeric(b_calc["السعر المتفق"])
        b_calc["المدفوع"] = pd.to_numeric(b_calc["المدفوع"])

        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المبيعات", f"{b_calc['السعر المتفق'].sum():,.0f}")
        c2.metric("إجمالي التحصيل", f"{b_calc['المدفوع'].sum():,.0f}")
        c3.metric(
            "الديون المستحقة",
            f"{(b_calc['السعر المتفق'].sum() - b_calc['المدفوع'].sum()):,.0f}",
        )
