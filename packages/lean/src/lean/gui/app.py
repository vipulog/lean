import os

from gi.repository import Adw, Gdk, Gio, Gtk

from ..utils.secret_manager import retrieve_api_key
from .main_window import MainWindow
from .welcome_window import WelcomeWindow

GRESOURCE_PATH = os.environ.get("LEAN_RESOURCE_PATH")


class App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="dev.vipulog.lean", **kwargs)
        self.connect("activate", self.on_activate)

        res = Gio.Resource.load(GRESOURCE_PATH)
        Gio.resources_register(res)
        display = Gdk.Display.get_default()
        icon_theme = Gtk.IconTheme.get_for_display(display)
        icon_theme.add_resource_path("/dev/vipulog/lean/icons")

    def on_activate(self, app):
        if retrieve_api_key() is None:
            win = WelcomeWindow(application=app)
        else:
            win = MainWindow(application=app)
        win.present()
