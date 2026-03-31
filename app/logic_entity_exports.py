from app.logic_entity_exports_bookings import build_booking_exports
from app.logic_entity_exports_catalog import build_catalog_exports
from app.logic_entity_exports_payments import build_payment_exports


def build_entity_exports(context):
    exports = {
        "load_data": context["_make_synced_wrapper"](context["data_access_domain"].load_data),
    }

    exports.update(build_catalog_exports(context))
    payment_exports = build_payment_exports(context)
    exports.update(payment_exports)
    exports.update(build_booking_exports(context, payment_exports["add_payment"]))
    return exports
