from gi.repository import Adw, GObject, Gtk


class InitialPage(Gtk.Box):
    __gsignals__ = {
        "ask-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "thinking-toggled": (GObject.SignalFlags.RUN_FIRST, None, (bool,)),
    }

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        self._thinking_switch = Adw.SwitchRow(title="Enable Thinking")
        self._thinking_switch.connect("notify::active", self._on_thinking_toggled)

        preference_group = Adw.PreferencesGroup()
        preference_group.add(self._thinking_switch)

        ask_button = Gtk.Button(label="Ask question")
        ask_button.add_css_class("pill")
        ask_button.connect("clicked", self._on_ask_clicked)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.append(preference_group)
        content_box.append(ask_button)

        title = "Ask a Question"
        description = "Press 'Ask question' to take a screenshot and get an answer."

        status_page = Adw.StatusPage(vexpand=True, hexpand=True)
        status_page.set_title(title)
        status_page.set_icon_name("camera-photo-symbolic")
        status_page.set_description(description)
        status_page.set_child(content_box)

        clamp = Adw.Clamp()
        clamp.set_child(status_page)
        clamp.set_maximum_size(400)

        self.set_spacing(12)
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.append(clamp)

    def set_thinking_active(self, active):
        self._thinking_switch.set_active(active)

    def _on_ask_clicked(self, _):
        self.emit("ask-clicked")

    def _on_thinking_toggled(self, switch, _):
        self.emit("thinking-toggled", switch.get_active())
