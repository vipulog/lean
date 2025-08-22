from gi.repository import Adw, Gtk

from ..utils import secret_manager
from .main_window import MainWindow


class WelcomeWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._api_key_entry = Gtk.Entry()
        self._api_key_entry.set_placeholder_text("Enter your Gemini API Key")
        self._api_key_entry.set_width_chars(30)
        self._api_key_entry.connect("changed", self._on_api_key_entry_changed)

        self._continue_button = Gtk.Button(label="Continue")
        self._continue_button.add_css_class("suggested-action")
        self._continue_button.add_css_class("pill")
        self._continue_button.set_halign(Gtk.Align.CENTER)
        self._continue_button.set_sensitive(False)
        self._continue_button.connect("clicked", self._on_continue_button_clicked)

        existing_key = secret_manager.retrieve_api_key()
        if existing_key:
            self._api_key_entry.set_text(existing_key)
            self._continue_button.set_sensitive(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        box.append(self._api_key_entry)
        box.append(self._continue_button)

        status_page = Adw.StatusPage(
            icon_name="dialog-information-symbolic",
            title="Welcome",
            description="Please enter your Gemini API key to continue.",
            vexpand=True,
            hexpand=True,
        )
        status_page.set_child(box)

        window_title = Adw.WindowTitle(title="lean")
        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(window_title)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header_bar)
        toolbar_view.set_content(status_page)

        self.set_title("lean")
        self.set_default_size(400, 500)
        self.set_size_request(400, 400)
        self.set_content(toolbar_view)

    def _on_api_key_entry_changed(self, entry):
        self._continue_button.set_sensitive(bool(entry.get_text()))

    def _on_continue_button_clicked(self, _):
        api_key = self._api_key_entry.get_text()
        if not api_key:
            return
        secret_manager.store_api_key(api_key)
        main_window = MainWindow(application=self.get_application())
        main_window.present()
        self.close()
