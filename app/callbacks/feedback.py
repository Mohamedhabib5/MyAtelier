from dash import no_update


def success_toast(message):
    return message, True


def no_toast():
    return no_update, no_update
