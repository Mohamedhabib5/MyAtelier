import flask
import os
from app.bootstrap import create_dash_app
import logic

# --- 1. App Bootstrap ---
app = create_dash_app(__name__)
server = app.server
_default_secret = "myatelier-dev-secret-change-me"
server.secret_key = os.environ.get("APP_SECRET_KEY", _default_secret)
_app_env = os.environ.get("APP_ENV", "development").strip().lower()
if _app_env in {"production", "prod"} and server.secret_key == _default_secret:
    raise RuntimeError("APP_SECRET_KEY must be set in production.")

# --- Flask Route for Images ---
@server.route('/dress_images/<path:filename>')
def serve_dress_image(filename):
    return flask.send_from_directory(logic.IMAGE_FOLDER, filename)

# --- 2. Runtime Wiring ---
from app.callbacks.register_all import register_all_callbacks
from app.layouts.finance import layout_finance
from app.layouts.customers import layout_customers
from app.layouts.bookings import layout_bookings
from app.layouts.payments import layout_payments
from app.layouts.services import layout_services
from app.layouts.settings import layout_settings
from app.layouts.users import layout_users
from app.layouts.dresses import layout_dresses
from app.layouts.login import layout_login
from app.layouts.root import layout_root
from app.composition.wiring import build_runtime_wiring
from app.callbacks.navigation import register_sidebar_clientside_callback
from app.constants import (
    IMAGE_FOLDER,
    BACKUP_FOLDER,
    PAYMENTS_ACTION_LABEL,
    CUSTOMER_BOOKINGS_ACTION_LABEL,
    DRESS_BOOKINGS_ACTION_LABEL,
    PAYMENT_BOOKING_ACTION_LABEL,
)
from app.text_utils import normalize_code, delete_reason

# Ensure folders exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# Initialize database and folders
logic.init_folders()

# Constants
C_COLS = logic.C_COLS
S_COLS = logic.S_COLS
D_COLS = logic.D_COLS
B_COLS = logic.B_COLS
P_COLS = logic.P_COLS


routing = build_runtime_wiring(
    load_data=logic.load_data,
    data_cache=logic.DATA_CACHE,
    check_departments=logic.check_departments,
    c_cols=C_COLS,
    s_cols=S_COLS,
    d_cols=D_COLS,
    b_cols=B_COLS,
    p_cols=P_COLS,
    normalize_code=normalize_code,
    payments_action_label=PAYMENTS_ACTION_LABEL,
    customer_bookings_action_label=CUSTOMER_BOOKINGS_ACTION_LABEL,
    dress_bookings_action_label=DRESS_BOOKINGS_ACTION_LABEL,
    payment_booking_action_label=PAYMENT_BOOKING_ACTION_LABEL,
    layout_finance=layout_finance,
    layout_bookings=layout_bookings,
    layout_customers=layout_customers,
    layout_services=layout_services,
    layout_dresses=layout_dresses,
    layout_payments=layout_payments,
    layout_settings=layout_settings,
    backup_folder=BACKUP_FOLDER,
    layout_users=layout_users,
)
create_dt = routing["create_dt"]
main_layout = routing["main_layout"]
get_customers_table_content = routing["get_customers_table_content"]
get_services_table_content = routing["get_services_table_content"]
get_bookings_table_content = routing["get_bookings_table_content"]
get_payments_table_content = routing["get_payments_table_content"]
get_dresses_table_content = routing["get_dresses_table_content"]
get_dept_table_content = routing["get_dept_table_content"]

# --- 3. Root Layouts ---
login_layout = layout_login()

app.layout = layout_root()

register_sidebar_clientside_callback(app)

# --- Callbacks Registration ---
register_all_callbacks(
    app=app,
    load_data=logic.load_data,
    login_layout=login_layout,
    main_layout=main_layout,
    verify_password=logic.verify_password,
    check_departments=logic.check_departments,
    check_users=logic.check_users,
    create_dt=create_dt,
    logic_module=logic,
    c_cols=C_COLS,
    s_cols=S_COLS,
    d_cols=D_COLS,
    b_cols=B_COLS,
    p_cols=P_COLS,
    normalize_code=normalize_code,
    delete_reason=delete_reason,
    payments_action_label=PAYMENTS_ACTION_LABEL,
    customer_bookings_action_label=CUSTOMER_BOOKINGS_ACTION_LABEL,
    dress_bookings_action_label=DRESS_BOOKINGS_ACTION_LABEL,
    payment_booking_action_label=PAYMENT_BOOKING_ACTION_LABEL,
    get_services_table_content=get_services_table_content,
    get_dresses_table_content=get_dresses_table_content,
    get_payments_table_content=get_payments_table_content,
    get_dept_table_content=get_dept_table_content,
    get_customers_table_content=get_customers_table_content,
    get_bookings_table_content=get_bookings_table_content,
)

if __name__ == '__main__':
    debug_mode = os.environ.get("APP_DEBUG", "1").strip().lower() in ("1", "true", "yes")
    use_reloader = os.environ.get("APP_RELOADER", "0").strip().lower() in ("1", "true", "yes")
    app.run(debug=debug_mode, use_reloader=use_reloader, port=8050)



