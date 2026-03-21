from app.layouts.root import layout_root


def test_global_success_toast_auto_dismiss_policy():
    root = layout_root()
    toast_container = root.children[4]
    toast = toast_container.children

    assert toast.id == "app-success-toast"
    assert toast.is_open is False
    assert toast.dismissable is True
    assert toast.duration == 3000
    assert toast.icon == "success"
