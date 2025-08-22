from gi.repository import Adw


def show_about(parent):
    dialog = Adw.AboutDialog()
    dialog.set_application_name("lean")
    dialog.present(parent)
