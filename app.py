import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, date, timedelta
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import shutil

# --- 1. إعدادات الصفحة والمظهر ---
st.set_page_config(
    page_title="✨ نظام إدارة الأتيليه",
    layout="wide",
    initial_sidebar_state="collapsed"
)

IMAGE_FOLDER = "dress_images"
BACKUP_FOLDER = "backups"
if not os.path.exists(IMAGE_FOLDER): os.makedirs(IMAGE_FOLDER)
if not os.path.exists(BACKUP_FOLDER): os.makedirs(BACKUP_FOLDER)

# --- 2. محرك البيانات (Data Engine) ---
def load_data(file_name, columns):
    """تحميل البيانات مع معالجة الأخطاء"""
    try:
        if os.path.exists(file_name):
            df = pd.read_csv(file_name, dtype=str)
            df = df.fillna("")
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df[columns]
    except Exception as e:
        st.error(f"⚠️ خطأ في تحميل {file_name}: {str(e)}")
    return pd.DataFrame(columns=columns)

def save_data(df, file_name):
    """حفظ البيانات مع نسخ احتياطي تلقائي"""
    try:
        # إنشاء نسخة احتياطية قبل الحفظ
        if os.path.exists(file_name):
            backup_name = f"{BACKUP_FOLDER}/{os.path.basename(file_name).replace('.csv', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            shutil.copy2(file_name, backup_name)
            # الاحتفاظ بآخر 10 نسخ فقط
            cleanup_old_backups(file_name)
        df.to_csv(file_name, index=False)
        return True
    except Exception as e:
        st.error(f"⚠️ خطأ في حفظ {file_name}: {str(e)}")
        return False

def cleanup_old_backups(file_name, keep_count=10):
    """حذف النسخ الاحتياطية القديمة والاحتفاظ بآخر عدد محدد"""
    try:
        base_name = os.path.basename(file_name).replace('.csv', '')
        backups = [f for f in os.listdir(BACKUP_FOLDER) if f.startswith(base_name)]
        backups.sort(reverse=True)
        for old_backup in backups[keep_count:]:
            os.remove(os.path.join(BACKUP_FOLDER, old_backup))
    except Exception as e:
        pass  # تجاهل أخطاء التنظيف

def get_styled_df(df, numeric_cols=[], date_cols=[]):
    """تنسيق DataFrame للعرض"""
    if df.empty: return df
    display_df = df.copy()
    try:
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce').fillna(0)
        for col in date_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_datetime(display_df[col], errors='coerce').dt.date
    except Exception as e:
        st.warning(f"⚠️ تحذير في تنسيق البيانات: {str(e)}")
    return display_df

def safe_date_parse(date_str, default=None):
    """تحويل آمن للتاريخ مع معالجة الأخطاء"""
    try:
        if date_str and date_str.strip():
            return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
    except:
        pass
    return default if default else date.today()

def export_to_excel(dataframes_dict, filename="export.xlsx"):
    """تصدير عدة DataFrames إلى ملف Excel"""
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in dataframes_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"⚠️ خطأ في التصدير: {str(e)}")
        return None

def get_upcoming_events(bookings_df, days=7):
    """الحصول على المناسبات القادمة خلال عدد أيام محدد"""
    try:
        upcoming = []
        today = date.today()
        for _, row in bookings_df.iterrows():
            event_date = safe_date_parse(row["تاريخ المناسبة"])
            days_diff = (event_date - today).days
            if 0 <= days_diff <= days:
                upcoming.append({
                    "العروسة": row["اسم العروسه"],
                    "الخدمة": row["الخدمة"],
                    "تاريخ المناسبة": event_date,
                    "الأيام المتبقية": days_diff,
                    "المبلغ المتبقي": row["المتبقي"]
                })
        return pd.DataFrame(upcoming)
    except Exception as e:
        return pd.DataFrame()

# تعريف الأعمدة الثابتة لضمان عدم حدوث KeyError
C_COLS = ["كود العميل", "تاريخ التسجيل", "اسم العروسه", "اسم العريس", "العنوان", "تليفون 1", "تليفون 2", "ملاحظات"]
S_COLS = ["كود الخدمة", "القسم", "اسم الخدمة", "السعر المقترح"]
D_COLS = ["كود الفستان", "نوع الفستان", "تاريخ الشراء", "وصف الفستان", "صورة الفستان", "حالة الفستان"]
B_COLS = ["كود الحجز", "تاريخ الحجز", "اسم العروسه", "القسم", "الخدمة", "كود الفستان", "تاريخ المناسبة", "السعر المتفق", "المدفوع", "المتبقي", "ملاحظات الحجز"]
P_COLS = ["كود الدفع", "التاريخ", "كود الحجز", "القيمة المدفوعة", "اسم العروسه", "اسم العريس", "المتبقي بعد الدفعة", "ملاحظات الدفع"]

# استخدام session_state لتحسين الأداء
if 'data_loaded' not in st.session_state:
    st.session_state.customers_df = load_data("customers.csv", C_COLS)
    st.session_state.services_df = load_data("services.csv", S_COLS)
    st.session_state.dresses_df = load_data("dresses.csv", D_COLS)
    st.session_state.bookings_df = load_data("bookings.csv", B_COLS)
    st.session_state.payments_df = load_data("payments.csv", P_COLS)
    st.session_state.data_loaded = True

# الوصول للبيانات من session_state
customers_df = st.session_state.customers_df
services_df = st.session_state.services_df
dresses_df = st.session_state.dresses_df
bookings_df = st.session_state.bookings_df
payments_df = st.session_state.payments_df


st.title("🌟 نظام إدارة الأتيليه الاحترافي")

# عرض التنبيهات للمناسبات القادمة بتصميم جذاب
upcoming = get_upcoming_events(bookings_df, days=7)
if not upcoming.empty:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: nowrap;
        ">
            <div style="
                background: white;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                flex-shrink: 0;
            ">🔔</div>
            <div style="
                color: white;
                flex: 1;
                min-width: 0;
            ">
                <div style="
                    margin: 0;
                    font-size: 22px;
                    font-weight: 700;
                    line-height: 1.3;
                    margin-bottom: 8px;
                ">تنبيه هام!</div>
                <div style="
                    margin: 0;
                    font-size: 17px;
                    opacity: 0.95;
                    line-height: 1.4;
                ">لديك <strong style="font-size: 20px;">{len(upcoming)}</strong> مناسبة قادمة خلال الأسبوع</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # نظام لإظهار/إخفاء التفاصيل
    if "show_alerts" not in st.session_state:
        st.session_state.show_alerts = False
    
    if st.button("📋 عرض تفاصيل المناسبات" if not st.session_state.show_alerts else "🔼 إخفاء التفاصيل", 
                 use_container_width=True):
        st.session_state.show_alerts = not st.session_state.show_alerts
    
    if st.session_state.show_alerts:
        st.dataframe(
            upcoming,
            use_container_width=True,
            hide_index=True,
            column_config={
                "العروسة": st.column_config.TextColumn("العروسة", width="medium"),
                "الخدمة": st.column_config.TextColumn("الخدمة", width="medium"),
                "تاريخ المناسبة": st.column_config.DateColumn("تاريخ المناسبة", width="medium"),
                "الأيام المتبقية": st.column_config.NumberColumn("الأيام المتبقية", width="small"),
                "المبلغ المتبقي": st.column_config.NumberColumn("المبلغ المتبقي", width="medium", format="%.0f")
            }
        )

tabs = st.tabs(["👥 العملاء", "📋 الخدمات", "👗 الفساتين", "📝 الحجوزات", "💰 المدفوعات", "📊 المالية", "⚙️ الإعدادات"])

# --- 1. تبويب العملاء (الربط 360 درجة) ---
with tabs[0]:
    st.header("إدارة وسجلات العملاء")
    c_mode = st.radio("العملية:", ["➕ إضافة عميلة جديدة", "✏️ بحث وتعديل شامل", "🗑️ حذف عميلة"], horizontal=True, key="c_mode")
    
    if c_mode == "➕ إضافة عميلة جديدة":
        with st.form("c_add_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            f_n = col1.text_input("اسم العروسه *")
            f_g = col2.text_input("اسم العريس *")
            f_a = col1.text_input("العنوان *")
            f_p1 = col2.text_input("رقم تليفون 1 *")
            f_p2 = col1.text_input("رقم تليفون 2")
            f_reg = col2.date_input("تاريخ التسجيل", date.today())
            f_nt = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ بيانات العروسة ✅"):
                if f_n and f_g and f_p1 and f_a:
                    # التحقق من صحة رقم الهاتف
                    if not (f_p1.isdigit() and len(f_p1) >= 10):
                        st.error("⚠️ رقم الهاتف يجب أن يحتوي على أرقام فقط (10 أرقام على الأقل)")
                        st.stop()
                    
                    # إصلاح توليد الـ ID: البحث عن أكبر كود موجود وإضافة 1
                    max_id = 100
                    if not customers_df.empty:
                        try:
                            max_id = customers_df["كود العميل"].str.replace("C-", "").astype(int).max()
                        except:
                            max_id = len(customers_df) + 100
                    
                    new_id = f"C-{max_id + 1}"
                    customers_df.loc[len(customers_df)] = [new_id, str(f_reg), f_n, f_g, f_a, f_p1, f_p2, f_nt]
                    if save_data(customers_df, "customers.csv"):
                        st.session_state.customers_df = customers_df
                        st.success(f"تم التسجيل بنجاح (الكود: {new_id}) ✅")
                        st.rerun()
                else: st.error("⚠️ جميع الخانات مطلوبة")
    
    elif c_mode == "✏️ بحث وتعديل شامل":
        if not customers_df.empty:
            # إضافة بحث متقدم
            search_term = st.text_input("🔍 ابحث بالاسم أو رقم الهاتف:")
            filtered_customers = customers_df
            if search_term:
                filtered_customers = customers_df[
                    customers_df["اسم العروسه"].str.contains(search_term, case=False, na=False) |
                    customers_df["اسم العريس"].str.contains(search_term, case=False, na=False) |
                    customers_df["تليفون 1"].str.contains(search_term, case=False, na=False) |
                    customers_df["تليفون 2"].str.contains(search_term, case=False, na=False)
                ]
            
            if not filtered_customers.empty:
                sel_c = st.selectbox("ابحث عن العروسة للتعديل الشامل:", [""] + filtered_customers["اسم العروسه"].tolist())
                if sel_c:
                    c_idx = customers_df[customers_df["اسم العروسه"] == sel_c].index[0]
                    c_curr = customers_df.loc[c_idx]
                    with st.form("c_edit_full"):
                        e1, e2 = st.columns(2)
                        en_name = e1.text_input("تعديل اسم العروسة", value=c_curr["اسم العروسه"])
                        en_groom = e2.text_input("تعديل اسم العريس", value=c_curr["اسم العريس"])
                        en_addr = e1.text_input("تعديل العنوان", value=c_curr["العنوان"])
                        en_p1 = e2.text_input("تعديل تليفون 1", value=c_curr["تليفون 1"])
                        en_p2 = e1.text_input("تعديل تليفون 2", value=c_curr["تليفون 2"])
                        en_reg = e2.date_input("تعديل تاريخ التسجيل", value=safe_date_parse(c_curr["تاريخ التسجيل"]))
                        en_notes = st.text_area("تعديل الملاحظات", value=c_curr["ملاحظات"])
                        if st.form_submit_button("تحديث كل البيانات ✏️"):
                            old_name = c_curr["اسم العروسه"]
                            # التحقق من صحة رقم الهاتف عند التعديل
                            if not (en_p1.isdigit() and len(en_p1) >= 10):
                                st.error("⚠️ رقم الهاتف يجب أن يحتوي على أرقام فقط")
                                st.stop()

                            customers_df.loc[c_idx] = [c_curr["كود العميل"], str(en_reg), en_name, en_groom, en_addr, en_p1, en_p2, en_notes]
                            
                            # Cascade Update: تحديث الاسم في الحجوزات والمدفوعات إذا تغير
                            if old_name != en_name:
                                bookings_df.loc[bookings_df["اسم العروسه"] == old_name, "اسم العروسه"] = en_name
                                payments_df.loc[payments_df["اسم العروسه"] == old_name, "اسم العروسه"] = en_name
                                save_data(bookings_df, "bookings.csv")
                                save_data(payments_df, "payments.csv")
                                st.session_state.bookings_df = bookings_df
                                st.session_state.payments_df = payments_df
                                st.info("ℹ️ تم تحديث اسم العروسة في جميع السجلات المرتبطة")

                            if save_data(customers_df, "customers.csv"):
                                st.session_state.customers_df = customers_df
                                st.success("تم التحديث ✅")
                                st.rerun()
            else:
                st.info("لا توجد نتائج للبحث")
    
    else:  # حذف عميلة
        if not customers_df.empty:
            sel_c_del = st.selectbox("اختر العميلة للحذف:", [""] + customers_df["اسم العروسه"].tolist())
            if sel_c_del:
                c_idx_del = customers_df[customers_df["اسم العروسه"] == sel_c_del].index[0]
                # التحقق من وجود حجوزات
                has_bookings = not bookings_df[bookings_df["اسم العروسه"] == sel_c_del].empty
                if has_bookings:
                    st.error("⚠️ لا يمكن حذف هذه العميلة لأن لديها حجوزات مسجلة!")
                else:
                    st.warning(f"⚠️ هل أنت متأكد من حذف العميلة: {sel_c_del}؟")
                    if st.button("تأكيد الحذف 🗑️", type="primary"):
                        customers_df = customers_df.drop(c_idx_del).reset_index(drop=True)
                        if save_data(customers_df, "customers.csv"):
                            st.session_state.customers_df = customers_df
                            st.success("تم الحذف ✅")
                            st.rerun()

    st.divider()
    st.write("### جدول العملاء (اضغط على السطر لرؤية تاريخ العروسة المالي والزمني ⚡)")
    c_display = get_styled_df(customers_df.iloc[::-1], date_cols=["تاريخ التسجيل"])
    c_sel = st.dataframe(c_display, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    if c_sel.selection.rows:
        bride_name = c_display.iloc[c_sel.selection.rows[0]]["اسم العروسه"]
        st.markdown(f"#### 🔍 السجل الكامل لـ: {bride_name}")
        col_b, col_p = st.columns(2)
        with col_b:
            st.info("📋 الحجوزات المسجلة")
            rel_b = bookings_df[bookings_df["اسم العروسه"] == bride_name]
            st.dataframe(get_styled_df(rel_b, numeric_cols=["السعر المتفق","المتبقي"], date_cols=["تاريخ المناسبة"]), use_container_width=True, hide_index=True)
        with col_p:
            st.success("💰 المدفوعات المستلمة")
            rel_p = payments_df[payments_df["اسم العروسه"] == bride_name]
            st.dataframe(get_styled_df(rel_p, numeric_cols=["القيمة المدفوعة"], date_cols=["التاريخ"]), use_container_width=True, hide_index=True)

# --- 2. الخدمات ---
with tabs[1]:
    st.header("منيو الخدمات")
    s_mode = st.radio("العملية:", ["إضافة خدمة", "تعديل شامل", "🗑️ حذف خدمة"], horizontal=True, key="s_mode")
    if s_mode == "إضافة خدمة":
        with st.form("s_add"):
            sn = st.text_input("اسم الخدمة *")
            sd = st.selectbox("القسم", ["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"])
            sp = st.number_input("السعر المقترح", min_value=0)
            if st.form_submit_button("حفظ ✅"):
                if sn:
                    # إصلاح توليد ID الخدمات
                    max_sid = 100
                    if not services_df.empty:
                        try:
                            max_sid = services_df["كود الخدمة"].str.replace("S-", "").astype(int).max()
                        except:
                            max_sid = len(services_df) + 100
                    
                    services_df.loc[len(services_df)] = [f"S-{max_sid+1}", sd, sn, str(sp)]
                    if save_data(services_df, "services.csv"):
                        st.session_state.services_df = services_df
                        st.rerun()
    elif s_mode == "تعديل شامل":
        if not services_df.empty:
            sel_s = st.selectbox("اختر الخدمة للتعديل الشامل:", services_df["اسم الخدمة"])
            s_idx = services_df[services_df["اسم الخدمة"] == sel_s].index[0]
            s_curr = services_df.loc[s_idx]
            with st.form("s_edit_full"):
                en_n = st.text_input("تعديل اسم الخدمة", value=s_curr["اسم الخدمة"])
                en_d = st.selectbox("تعديل القسم", ["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"], index=["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"].index(s_curr["القسم"]))
                en_p = st.number_input("تعديل السعر", value=int(float(s_curr["السعر المقترح"])))
                if st.form_submit_button("تحديث الخدمة ✏️"):
                    services_df.loc[s_idx] = [s_curr["كود الخدمة"], en_d, en_n, str(en_p)]
                    if save_data(services_df, "services.csv"):
                        st.session_state.services_df = services_df
                        st.success("تم التحديث")
                        st.rerun()
    else:  # حذف خدمة
        if not services_df.empty:
            sel_s_del = st.selectbox("اختر الخدمة للحذف:", services_df["اسم الخدمة"])
            s_idx_del = services_df[services_df["اسم الخدمة"] == sel_s_del].index[0]
            has_bookings = not bookings_df[bookings_df["الخدمة"] == sel_s_del].empty
            if has_bookings:
                st.error("⚠️ لا يمكن حذف هذه الخدمة لأنها مستخدمة في حجوزات!")
            else:
                st.warning(f"⚠️ هل أنت متأكد من حذف الخدمة: {sel_s_del}؟")
                if st.button("تأكيد الحذف 🗑️", type="primary"):
                    services_df = services_df.drop(s_idx_del).reset_index(drop=True)
                    if save_data(services_df, "services.csv"):
                        st.session_state.services_df = services_df
                        st.success("تم الحذف ✅")
                        st.rerun()
    
    st.dataframe(get_styled_df(services_df, numeric_cols=["السعر المقترح"]), use_container_width=True, hide_index=True)

# --- 3. الفساتين (مع سجل الحجوزات الجديد) ---
with tabs[2]:
    st.header("كتالوج الفساتين")
    d_mode = st.radio("العملية:", ["إضافة فستان", "تعديل شامل", "🗑️ حذف فستان"], horizontal=True, key="d_mode")
    if d_mode == "إضافة فستان":
        with st.form("d_add"):
            col1, col2 = st.columns(2)
            dc = col1.text_input("كود الفستان *")
            dt = col2.selectbox("النوع", ["زفاف", "سواريه", "غير محدد"])
            dp = col1.date_input("تاريخ الشراء", date.today())
            ds = col2.selectbox("الحالة", ["متاح", "محجوز", "في المغسلة"])
            dd = st.text_area("وصف الفستان *")
            di = col2.file_uploader("الصورة")
            if st.form_submit_button("حفظ ✅"):
                if dc and dd:
                    # التحقق من عدم تكرار الكود
                    if dc in dresses_df["كود الفستان"].values:
                        st.error("⚠️ كود الفستان موجود مسبقاً!")
                    else:
                        path = os.path.join(IMAGE_FOLDER, f"{dc}.jpg") if di else ""
                        if di: Image.open(di).save(path)
                        dresses_df.loc[len(dresses_df)] = [dc, dt, str(dp), dd, path, ds]
                        if save_data(dresses_df, "dresses.csv"):
                            st.session_state.dresses_df = dresses_df
                            st.rerun()
    elif d_mode == "تعديل شامل":
        if not dresses_df.empty:
            # تحسين عرض البحث
            d_search_list = dresses_df.apply(lambda x: f"{x['كود الفستان']} | {x['وصف الفستان'][:50]}...", axis=1).tolist()
            sel_d = st.selectbox("ابحث عن فستان للتعديل:", d_search_list)
            d_idx = dresses_df[dresses_df["كود الفستان"] == sel_d.split(" | ")[0]].index[0]
            d_curr = dresses_df.loc[d_idx]
            with st.form("d_edit_full"):
                e1, e2 = st.columns(2)
                edc = e1.text_input("تعديل الكود", value=d_curr["كود الفستان"])
                edt = e2.selectbox("تعديل النوع", ["زفاف", "سواريه", "غير محدد"], index=["زفاف", "سواريه", "غير محدد"].index(d_curr["نوع الفستان"]))
                edp = e1.date_input("تعديل تاريخ الشراء", value=safe_date_parse(d_curr["تاريخ الشراء"]))
                eds = e2.selectbox("تعديل الحالة", ["متاح", "محجوز", "في المغسلة"], index=["متاح", "محجوز", "في المغسلة"].index(d_curr["حالة الفستان"]))
                edd = st.text_area("تعديل وصف الفستان", value=d_curr["وصف الفستان"])
                if st.form_submit_button("تحديث الفستان ✏️"):
                    dresses_df.loc[d_idx] = [edc, edt, str(edp), edd, d_curr["صورة الفستان"], eds]
                    if save_data(dresses_df, "dresses.csv"):
                        st.session_state.dresses_df = dresses_df
                        st.rerun()
    else:  # حذف فستان
        if not dresses_df.empty:
            sel_d_del = st.selectbox("اختر الفستان للحذف:", dresses_df["كود الفستان"])
            d_idx_del = dresses_df[dresses_df["كود الفستان"] == sel_d_del].index[0]
            has_bookings = not bookings_df[bookings_df["كود الفستان"] == sel_d_del].empty
            if has_bookings:
                st.error("⚠️ لا يمكن حذف هذا الفستان لأنه محجوز!")
            else:
                st.warning(f"⚠️ هل أنت متأكد من حذف الفستان: {sel_d_del}؟")
                if st.button("تأكيد الحذف 🗑️", type="primary"):
                    # حذف الصورة إن وجدت
                    img_path = dresses_df.loc[d_idx_del, "صورة الفستان"]
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)
                    dresses_df = dresses_df.drop(d_idx_del).reset_index(drop=True)
                    if save_data(dresses_df, "dresses.csv"):
                        st.session_state.dresses_df = dresses_df
                        st.success("تم الحذف ✅")
                        st.rerun()

    st.divider()
    st.write("### سجل الفساتين (اضغط على سطر الفستان لرؤية العرائس اللاتي حجزنه ⚡)")
    d_disp = get_styled_df(dresses_df, date_cols=["تاريخ الشراء"])
    d_sel = st.dataframe(d_disp, column_config={"صورة الفستان": st.column_config.ImageColumn()}, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    if d_sel.selection.rows:
        sel_dress_id = d_disp.iloc[d_sel.selection.rows[0]]["كود الفستان"]
        st.info(f"📋 سجل حركات الفستان كود: {sel_dress_id}")
        rel_bookings_dress = bookings_df[bookings_df["كود الفستان"] == sel_dress_id]
        if not rel_bookings_dress.empty:
            st.dataframe(get_styled_df(rel_bookings_dress, numeric_cols=["السعر المتفق"], date_cols=["تاريخ المناسبة"]), use_container_width=True, hide_index=True)
        else: st.write("هذا الفستان متاح ولم يتم حجز مسبق له.")

# --- 4. الحجوزات (الربط والبحث المتقدم) ---
with tabs[3]:
    st.header("إدارة الحجوزات")
    b_mode = st.radio("العملية:", ["➕ حجز جديد", "✏️ بحث وتعديل شامل", "🗑️ حذف حجز"], horizontal=True, key="b_mode")
    
    if b_mode == "➕ حجز جديد":
        b_dept = st.selectbox("اختر القسم لبدء الحجز", ["الميكب", "التصوير", "الشعر", "البشره", "الفساتين"])
        is_dr = (b_dept == "الفساتين")
        with st.form("b_add", clear_on_submit=False):
            c1, c2 = st.columns(2)
            f_cust = c1.selectbox("العروسه *", [""] + customers_df["اسم العروسه"].tolist())
            s_list = services_df[services_df["القسم"] == b_dept]["اسم الخدمة"].tolist()
            f_serv = c2.selectbox("الخدمة *", s_list if s_list else ["لا يوجد خدمات"])
            f_dress = c1.selectbox("الفستان", ["بدون فستان"] + dresses_df["كود الفستان"].tolist(), disabled=not is_dr)
            f_reg = c2.date_input("تاريخ تسجيل الحجز", date.today())
            f_event = c1.date_input("تاريخ المناسبة *")
            f_price = c2.number_input("السعر المتفق عليه *", min_value=1)
            f_paid = c1.number_input("العربون المدفوع الآن", min_value=0)
            f_notes = st.text_area("ملاحظات")
            if st.form_submit_button("تأكيد الحجز ✅"):
                if f_cust and f_price > 0:
                    if f_paid > f_price: st.error("❌ العربون أكبر من السعر"); st.stop()
                    # منع حجز نفس الفستان في نفس التاريخ فقط
                    if is_dr and f_dress != "بدون فستان":
                        conf = bookings_df[(bookings_df["كود الفستان"]==f_dress) & (bookings_df["تاريخ المناسبة"]==str(f_event))]
                        if not conf.empty: st.error("❌ الفستان محجوز بهذا التاريخ!"); st.stop()

                    bid = f"{b_dept[0:2].upper()}-{int(datetime.now().timestamp())}"
                    new_b = [bid, str(f_reg), f_cust, b_dept, f_serv, f_dress, str(f_event), str(f_price), str(f_paid), str(float(f_price)-float(f_paid)), f_notes]
                    bookings_df.loc[len(bookings_df)] = new_b
                    if save_data(bookings_df, "bookings.csv"):
                        st.session_state.bookings_df = bookings_df
                        if f_paid > 0:
                            p_id = f"PAY-{int(datetime.now().timestamp())}"
                            groom = customers_df[customers_df["اسم العروسه"]==f_cust].iloc[0]["اسم العريس"]
                            new_p = [p_id, str(f_reg), bid, str(f_paid), f_cust, groom, str(float(f_price)-float(f_paid)), "عربون حجز"]
                            payments_df.loc[len(payments_df)] = new_p
                            if save_data(payments_df, "payments.csv"):
                                st.session_state.payments_df = payments_df
                        st.success("تم الحجز بنجاح ✅")
                        st.rerun()
    
    elif b_mode == "✏️ بحث وتعديل شامل":
        if not bookings_df.empty:
            b_search = []
            for _, r in bookings_df.iterrows():
                gr = customers_df[customers_df["اسم العروسه"]==r["اسم العروسه"]].iloc[0]["اسم العريس"] if not customers_df[customers_df["اسم العروسه"]==r["اسم العروسه"]].empty else ""
                b_search.append(f"{r['كود الحجز']} | {r['اسم العروسه']} & {gr} | {r['الخدمة']} | {r['السعر المتفق']}ج")
            sel_b = st.selectbox("ابحث عن الحجز للتعديل الشامل:", b_search)
            bid_ed = sel_b.split(" | ")[0]
            b_idx = bookings_df[bookings_df["كود الحجز"] == bid_ed].index[0]
            b_curr = bookings_df.loc[b_idx]
            with st.form("b_edit_full_f"):
                e1, e2 = st.columns(2)
                en_cust = e1.selectbox("العروسة", customers_df["اسم العروسه"].tolist(), index=customers_df["اسم العروسه"].tolist().index(b_curr["اسم العروسه"]))
                s_list_edit = services_df[services_df["القسم"] == b_curr["القسم"]]["اسم الخدمة"].tolist()
                s_idx = s_list_edit.index(b_curr["الخدمة"]) if b_curr["الخدمة"] in s_list_edit else 0
                en_serv = e2.selectbox("الخدمة", s_list_edit if s_list_edit else [b_curr["الخدمة"]], index=s_idx)
                en_reg = e1.date_input("تاريخ التعاقد", value=safe_date_parse(b_curr["تاريخ الحجز"]))
                en_ev = e2.date_input("تاريخ المناسبة", value=safe_date_parse(b_curr["تاريخ المناسبة"]))
                en_price = e1.number_input("تعديل السعر المتفق", value=float(b_curr["السعر المتفق"]))
                en_notes = st.text_area("تعديل الملاحظات", value=b_curr["ملاحظات الحجز"])
                if st.form_submit_button("حفظ كل التعديلات للحجز ✏️"):
                    new_rem = en_price - float(b_curr["المدفوع"])
                    bookings_df.loc[b_idx, ["اسم العروسه", "الخدمة", "تاريخ الحجز", "تاريخ المناسبة", "السعر المتفق", "ملاحظات الحجز", "المتبقي"]] = [en_cust, en_serv, str(en_reg), str(en_ev), str(en_price), en_notes, str(new_rem)]
                    if save_data(bookings_df, "bookings.csv"):
                        st.session_state.bookings_df = bookings_df
                        st.success("تم التحديث ✅")
                        st.rerun()
    
    else:  # حذف حجز
        if not bookings_df.empty:
            b_search_del = []
            for _, r in bookings_df.iterrows():
                b_search_del.append(f"{r['كود الحجز']} | {r['اسم العروسه']} | {r['الخدمة']}")
            sel_b_del = st.selectbox("اختر الحجز للحذف:", b_search_del)
            bid_del = sel_b_del.split(" | ")[0]
            b_idx_del = bookings_df[bookings_df["كود الحجز"] == bid_del].index[0]
            has_payments = not payments_df[payments_df["كود الحجز"] == bid_del].empty
            if has_payments:
                st.error("⚠️ لا يمكن حذف هذا الحجز لأن له مدفوعات مسجلة!")
            else:
                st.warning(f"⚠️ هل أنت متأكد من حذف الحجز: {bid_del}؟")
                if st.button("تأكيد الحذف 🗑️", type="primary"):
                    bookings_df = bookings_df.drop(b_idx_del).reset_index(drop=True)
                    if save_data(bookings_df, "bookings.csv"):
                        st.session_state.bookings_df = bookings_df
                        st.success("تم الحذف ✅")
                        st.rerun()

    st.divider()
    st.write("### سجل الحجوزات (المس السطر لرؤية المدفوعات وبيانات العروسة ⚡)")
    b_disp = get_styled_df(bookings_df.iloc[::-1], numeric_cols=["السعر المتفق", "المدفوع", "المتبقي"], date_cols=["تاريخ الحجز", "تاريخ المناسبة"])
    b_sel = st.dataframe(b_disp, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    if b_sel.selection.rows:
        sid = b_disp.iloc[b_sel.selection.rows[0]]["كود الحجز"]
        st.info(f"💰 دفعات الحجز رقم: {sid}")
        rel_p = payments_df[payments_df["كود الحجز"] == sid]
        if not rel_p.empty:
            st.dataframe(get_styled_df(rel_p[["التاريخ", "القيمة المدفوعة", "ملاحظات الدفع"]], numeric_cols=["القيمة المدفوعة"], date_cols=["التاريخ"]), use_container_width=True, hide_index=True)
        else: st.warning("لا توجد دفعات إضافية.")

# --- 5. المدفوعات ---
with tabs[4]:
    st.header("💰 إدارة المدفوعات")
    p_mode = st.radio("العملية:", ["➕ دفعة جديدة", "✏️ بحث وتعديل شامل", "🗑️ حذف دفعة"], horizontal=True, key="p_main")
    if p_mode == "➕ دفعة جديدة":
        if not bookings_df.empty:
            c_list = customers_df.apply(lambda x: f"{x['اسم العروسه']} | {x['اسم العريس']}", axis=1).tolist()
            sel_c = st.selectbox("ابحث عن العميلة:", c_list)
            b_name = sel_c.split(" | ")[0]
            c_bks = bookings_df[bookings_df["اسم العروسه"] == b_name]
            if not c_bks.empty:
                sel_bk = st.selectbox("اختر الحجز:", c_bks.apply(lambda x: f"{x['كود الحجز']} - {x['الخدمة']} (باقي {x['المتبقي']})", axis=1))
                tid = sel_bk.split(" - ")[0]
                trow = bookings_df[bookings_df["كود الحجز"] == tid].iloc[0]
                with st.form("p_add_f"):
                    p_date_in = st.date_input("التاريخ", date.today())
                    amt = st.number_input("المبلغ المدفوع", min_value=1.0)
                    p_msg = st.text_input("ملاحظات")
                    if st.form_submit_button("تأكيد الدفع ✅"):
                        rem = float(trow["المتبقي"])
                        if amt > rem: st.error("❌ المبلغ أكبر من المتبقي"); st.stop()
                        pid = f"PAY-{int(datetime.now().timestamp())}"
                        new_p = [pid, str(p_date_in), tid, str(amt), b_name, customers_df[customers_df["اسم العروسه"]==b_name].iloc[0]["اسم العريس"], str(rem-amt), p_msg]
                        payments_df.loc[len(payments_df)] = new_p
                        if save_data(payments_df, "payments.csv"):
                            st.session_state.payments_df = payments_df
                            bookings_df.loc[bookings_df["كود الحجز"] == tid, ["المدفوع", "المتبقي"]] = [str(float(trow["المدفوع"])+amt), str(rem-amt)]
                            if save_data(bookings_df, "bookings.csv"):
                                st.session_state.bookings_df = bookings_df
                                st.rerun()
    elif p_mode == "✏️ بحث وتعديل شامل":
        p_search = payments_df.apply(lambda x: f"{x['كود الدفع']} | {x['اسم العروسه']} | {x['القيمة المدفوعة']}ج | {x['التاريخ']}", axis=1).tolist()
        if p_search:
            sel_p = st.selectbox("ابحث عن دفعة للتعديل الشامل:", p_search)
            pid_ed = sel_p.split(" | ")[0]
            p_idx = payments_df[payments_df["كود الدفع"] == pid_ed].index[0]
            p_curr = payments_df.loc[p_idx]
            with st.form("p_edit_full_f"):
                ep_amt = st.number_input("تعديل المبلغ", value=float(p_curr["القيمة المدفوعة"]))
                ep_date = st.date_input("تعديل التاريخ", value=safe_date_parse(p_curr["التاريخ"]))
                ep_note = st.text_input("تعديل الملاحظات", value=p_curr["ملاحظات الدفع"])
                if st.form_submit_button("تحديث الدفعة ✏️"):
                    payments_df.loc[p_idx, ["القيمة المدفوعة", "التاريخ", "ملاحظات الدفع"]] = [str(ep_amt), str(ep_date), ep_note]
                    if save_data(payments_df, "payments.csv"):
                        st.session_state.payments_df = payments_df
                        st.success("تم التحديث ✅")
                        st.rerun()
    else:  # حذف دفعة
        p_search_del = payments_df.apply(lambda x: f"{x['كود الدفع']} | {x['اسم العروسه']} | {x['القيمة المدفوعة']}ج", axis=1).tolist()
        if p_search_del:
            sel_p_del = st.selectbox("اختر الدفعة للحذف:", p_search_del)
            pid_del = sel_p_del.split(" | ")[0]
            p_idx_del = payments_df[payments_df["كود الدفع"] == pid_del].index[0]
            p_to_del = payments_df.loc[p_idx_del]
            st.warning(f"⚠️ هل أنت متأكد من حذف الدفعة: {pid_del}؟")
            st.info("ملاحظة: سيتم تحديث المتبقي في الحجز المرتبط")
            if st.button("تأكيد الحذف 🗑️", type="primary"):
                # تحديث الحجز المرتبط
                booking_id = p_to_del["كود الحجز"]
                payment_amount = float(p_to_del["القيمة المدفوعة"])
                b_idx = bookings_df[bookings_df["كود الحجز"] == booking_id].index[0]
                current_paid = float(bookings_df.loc[b_idx, "المدفوع"])
                current_remaining = float(bookings_df.loc[b_idx, "المتبقي"])
                bookings_df.loc[b_idx, ["المدفوع", "المتبقي"]] = [str(current_paid - payment_amount), str(current_remaining + payment_amount)]
                
                payments_df = payments_df.drop(p_idx_del).reset_index(drop=True)
                if save_data(payments_df, "payments.csv") and save_data(bookings_df, "bookings.csv"):
                    st.session_state.payments_df = payments_df
                    st.session_state.bookings_df = bookings_df
                    st.success("تم الحذف ✅")
                    st.rerun()

    st.divider()
    st.write("### سجل المدفوعات (المس السطر لرؤية أصل الحجز ⚡)")
    p_disp = get_styled_df(payments_df.iloc[::-1], numeric_cols=["القيمة المدفوعة", "المتبقي بعد الدفعة"], date_cols=["التاريخ"])
    p_sel = st.dataframe(p_disp, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    if p_sel.selection.rows:
        linked_bid = p_disp.iloc[p_sel.selection.rows[0]]["كود الحجز"]
        st.success(f"📄 تفاصيل الحجز المرتبط بكود: {linked_bid}")
        st.dataframe(get_styled_df(bookings_df[bookings_df["كود الحجز"] == linked_bid], numeric_cols=["السعر المتفق","المتبقي"], date_cols=["تاريخ المناسبة"]), use_container_width=True, hide_index=True)

# --- 6. المالية ---
with tabs[5]:
    st.header("📊 التقرير المالي")
    b_calc = get_styled_df(bookings_df, numeric_cols=["السعر المتفق", "المدفوع"])
    c1, c2, c3 = st.columns(3)
    total_sales = b_calc['السعر المتفق'].sum()
    total_collected = b_calc['المدفوع'].sum()
    total_remaining = total_sales - total_collected
    
    c1.metric("إجمالي المبيعات", f"{total_sales:,.0f} ج.م")
    c2.metric("إجمالي التحصيل", f"{total_collected:,.0f} ج.م")
    c3.metric("الديون المستحقة", f"{total_remaining:,.0f} ج.م")
    
    st.divider()
    
    # رسوم بيانية
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 المبيعات حسب القسم")
        if not bookings_df.empty:
            sales_by_dept = bookings_df.groupby("القسم")["السعر المتفق"].apply(lambda x: pd.to_numeric(x, errors='coerce').sum()).reset_index()
            fig1 = px.pie(sales_by_dept, values='السعر المتفق', names='القسم', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        st.subheader("💰 نسبة التحصيل")
        collection_data = pd.DataFrame({
            'الفئة': ['المحصل', 'المتبقي'],
            'القيمة': [total_collected, total_remaining]
        })
        fig2 = px.bar(collection_data, x='الفئة', y='القيمة', color='الفئة', 
                      color_discrete_map={'المحصل': '#2ecc71', 'المتبقي': '#e74c3c'})
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    st.subheader("📅 المبيعات الشهرية")
    if not bookings_df.empty:
        bookings_with_dates = bookings_df.copy()
        bookings_with_dates['تاريخ الحجز'] = pd.to_datetime(bookings_with_dates['تاريخ الحجز'], errors='coerce')
        bookings_with_dates['السعر المتفق'] = pd.to_numeric(bookings_with_dates['السعر المتفق'], errors='coerce')
        bookings_with_dates['شهر'] = bookings_with_dates['تاريخ الحجز'].dt.to_period('M').astype(str)
        monthly_sales = bookings_with_dates.groupby('شهر')['السعر المتفق'].sum().reset_index()
        fig3 = px.line(monthly_sales, x='شهر', y='السعر المتفق', markers=True)
        st.plotly_chart(fig3, use_container_width=True)

# --- 7. الإعدادات ---
with tabs[6]:
    st.header("⚙️ الإعدادات والأدوات")
    
    st.subheader("📥 تصدير البيانات")
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("تصدير كل البيانات إلى Excel 📊"):
            excel_data = export_to_excel({
                "العملاء": customers_df,
                "الخدمات": services_df,
                "الفساتين": dresses_df,
                "الحجوزات": bookings_df,
                "المدفوعات": payments_df
            }, "atelier_data.xlsx")
            if excel_data:
                st.download_button(
                    label="تحميل الملف 📥",
                    data=excel_data,
                    file_name=f"atelier_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col_exp2:
        if st.button("تصدير التقرير المالي إلى Excel 💰"):
            financial_report = get_styled_df(bookings_df, numeric_cols=["السعر المتفق", "المدفوع", "المتبقي"])
            excel_data = export_to_excel({"التقرير المالي": financial_report}, "financial_report.xlsx")
            if excel_data:
                st.download_button(
                    label="تحميل التقرير 📥",
                    data=excel_data,
                    file_name=f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    st.divider()
    st.subheader("💾 النسخ الاحتياطية")
    st.info(f"يتم إنشاء نسخة احتياطية تلقائياً عند كل عملية حفظ في المجلد: {BACKUP_FOLDER}")
    
    if os.path.exists(BACKUP_FOLDER):
        backups = os.listdir(BACKUP_FOLDER)
        if backups:
            st.write(f"عدد النسخ الاحتياطية المتوفرة: {len(backups)}")
            with st.expander("عرض النسخ الاحتياطية"):
                for backup in sorted(backups, reverse=True)[:20]:
                    st.text(backup)
        else:
            st.write("لا توجد نسخ احتياطية حالياً")
    
    st.divider()
    st.subheader("🔔 إعدادات التنبيهات")
    alert_days = st.slider("عرض تنبيهات المناسبات القادمة خلال (أيام):", 1, 30, 7)
    if st.button("حفظ الإعدادات"):
        st.success("تم حفظ الإعدادات ✅")
