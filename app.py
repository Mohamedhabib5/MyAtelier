import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="نظام الأتيليه المحاسبي", layout="wide")

# دالة ذكية لإدارة البيانات
def load_data(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return pd.DataFrame(columns=columns)

# تحميل الجداول
customers = load_data("customers.csv", ["الاسم", "التليفون"])
bookings = load_data("bookings.csv", ["ID", "الاسم", "الخدمة", "السعر"])
payments = load_data("payments.csv", ["booking_id", "المبلغ", "التاريخ"])

st.title("🎨 إدارة حسابات الأتيليه")

tab1, tab2, tab3, tab4 = st.tabs(["👰 عروسة جديدة", "📝 حجز خدمة", "💰 تحصيل مبلغ", "📊 كشوف الحسابات"])

# 1. تسجيل العرائس
with tab1:
    with st.form("c_form"):
        name = st.text_input("اسم العروسة")
        phone = st.text_input("رقم التليفون")
        if st.form_submit_button("حفظ"):
            new_c = pd.DataFrame([[name, phone]], columns=["الاسم", "التليفون"])
            pd.concat([customers, new_c], ignore_index=True).to_csv("customers.csv", index=False)
            st.success("تم التسجيل")
            st.rerun()

# 2. تسجيل الحجوزات
with tab2:
    if customers.empty: st.info("سجل عروسة الأول")
    else:
        with st.form("b_form"):
            c_name = st.selectbox("اختار العروسة", customers["الاسم"])
            service = st.selectbox("الخدمة", ["ميكب زفاف", "فستان زفاف", "ميكب حنة", "جلسة شعر"])
            price = st.number_input("السعر المتفق عليه", min_value=0)
            if st.form_submit_button("تأكيد الحجز"):
                b_id = int(datetime.now().timestamp()) # كود فريد
                new_b = pd.DataFrame([[b_id, c_name, service, price]], columns=["ID", "الاسم", "الخدمة", "السعر"])
                pd.concat([bookings, new_b], ignore_index=True).to_csv("bookings.csv", index=False)
                st.success("تم الحجز")

# 3. تحصيل الفلوس (تخصيص يدوي)
with tab3:
    if bookings.empty: st.info("لا يوجد حجوزات")
    else:
        client = st.selectbox("العروسة اللي هتدفع:", bookings["الاسم"].unique())
        client_b = bookings[bookings["الاسم"] == client]
        target = st.selectbox("هتدفع لانهي خدمة؟", client_b.apply(lambda x: f"{x['الخدمة']} (سعرها {x['السعر']})", axis=1))
        b_id = client_b[client_b.apply(lambda x: f"{x['الخدمة']} (سعرها {x['السعر']})", axis=1) == target]["ID"].values[0]
        amount = st.number_input("المبلغ المدفوع", min_value=0)
        if st.button("تأكيد الدفع"):
            new_p = pd.DataFrame([[b_id, amount, datetime.now().strftime("%Y-%m-%d")]], columns=["booking_id", "المبلغ", "التاريخ"])
            pd.concat([payments, new_p], ignore_index=True).to_csv("payments.csv", index=False)
            st.success("تم التسجيل بنجاح")

# 4. التقارير (شغل المحاسب)
with tab4:
    if not bookings.empty:
        pay_sum = payments.groupby("booking_id")["المبلغ"].sum().reset_index()
        report = pd.merge(bookings, pay_sum, left_on="ID", right_on="booking_id", how="left").fillna(0)
        report["المتبقي"] = report["السعر"] - report["المبلغ"]
        st.table(report[["الاسم", "الخدمة", "السعر", "المبلغ", "المتبقي"]])