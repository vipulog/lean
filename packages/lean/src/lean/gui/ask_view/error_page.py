from gi.repository import Adw, GObject, Gtk


class ErrorPage(Gtk.Box):
    __gsignals__ = {
        "back-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "retry-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        back_button = Gtk.Button(label="Go Back")
        back_button.add_css_class("pill")
        back_button.connect("clicked", self._on_back_clicked)

        retry_button = Gtk.Button(label="Retry")
        retry_button.add_css_class("suggested-action")
        retry_button.add_css_class("pill")
        retry_button.connect("clicked", self._on_retry_clicked)

        button_box = Gtk.Box(spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.append(retry_button)
        button_box.append(back_button)

        self._status_page = Adw.StatusPage(vexpand=True, hexpand=True)
        self._status_page.set_title("Unknown Error Occurred")
        self._status_page.set_icon_name("dialog-error-symbolic")
        self._status_page.set_child(button_box)

        clamp = Adw.Clamp()
        clamp.set_child(self._status_page)
        clamp.set_maximum_size(400)

        self.set_spacing(12)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.append(clamp)

    def set_description_text(self, description):
        self._status_page.set_description(description)

    def _on_back_clicked(self, _):
        self.emit("back-clicked")

    def _on_retry_clicked(self, _):
        self.emit("retry-clicked")
