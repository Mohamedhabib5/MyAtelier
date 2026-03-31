from app.callbacks.dress_custody_state import register_dress_custody_state_callbacks
from app.callbacks.dress_custody_ui import register_dress_custody_ui_callbacks


def register_dress_custody_callbacks(app, load_data, b_cols, dc_cols, get_dress_custody_table_content, logic_module):
    register_dress_custody_state_callbacks(
        app,
        load_data,
        b_cols,
        dc_cols,
        get_dress_custody_table_content,
        logic_module,
    )
    register_dress_custody_ui_callbacks(app, load_data, dc_cols, logic_module)
