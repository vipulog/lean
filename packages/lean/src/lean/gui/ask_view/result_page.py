from gi.repository import Adw, Gio, GLib, GObject, Gtk, Pango, WebKit


def _handle_resource_request(request):
    path = request.get_path()
    res_path = f"/dev/vipulog/lean{path}"

    data = Gio.resources_lookup_data(res_path, Gio.ResourceLookupFlags.NONE)
    stream = Gio.MemoryInputStream.new_from_bytes(data)

    mime_type = "application/octet-stream"
    if path.endswith(".html"):
        mime_type = "text/html"
    elif path.endswith(".js"):
        mime_type = "text/javascript"
    elif path.endswith(".css"):
        mime_type = "text/css"

    request.finish(stream, data.get_size(), mime_type)


class ResultPage(Gtk.Box):
    __gsignals__ = {
        "regenerate-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "next-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "thinking-toggled": (GObject.SignalFlags.RUN_FIRST, None, (bool,)),
    }

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        self._webview = self._setup_webview()

        # Left-aligned action buttons (Next, Regenerate, Thinking)
        next_button = Gtk.Button.new_from_icon_name("go-next-symbolic")
        next_button.set_tooltip_text("Ask a new question")
        next_button.add_css_class("suggested-action")
        next_button.connect("clicked", self._on_next_clicked)

        regenerate_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        regenerate_button.set_tooltip_text("Regenerate the answer")
        regenerate_button.connect("clicked", self._on_regenerate_clicked)

        self._thinking_check = Gtk.ToggleButton(icon_name="brain-symbolic")
        self._thinking_check.set_tooltip_text("Thinking mode (disabled)")
        self._thinking_check.connect("toggled", self._on_thinking_toggled)

        action_buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        action_buttons_box.append(next_button)
        action_buttons_box.append(regenerate_button)
        action_buttons_box.append(self._thinking_check)

        # Right-aligned counter
        self._counter_label = Gtk.Label(label="in: 0 out: 0", xalign=1.0, yalign=0.5)
        self._counter_label.set_ellipsize(Pango.EllipsizeMode.NONE)
        self._counter_label.add_css_class("caption")
        self._counter_label.add_css_class("monospace")
        self._counter_label.set_margin_start(12)

        # Main action bar layout: [Buttons] [Spacer] [Counter]
        action_bar_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_bar_content.set_halign(Gtk.Align.FILL)
        action_bar_content.set_margin_top(12)
        action_bar_content.set_margin_bottom(12)

        action_bar_content.append(action_buttons_box)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        action_bar_content.append(spacer)
        action_bar_content.set_homogeneous(False)
        action_bar_content.append(self._counter_label)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(600)
        clamp.set_child(action_bar_content)

        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.append(self._webview)
        self.append(clamp)

    def set_thinking_active(self, active):
        self._thinking_check.set_active(active)

    def update_content(self, content, in_tokens, out_tokens):
        self._counter_label.set_label(f"in: {in_tokens} out: {out_tokens}")
        self._webview.evaluate_javascript("window.scrollTo(0, 0);", -1)
        content = content.replace("\\", "\\\\")
        content = content.replace('"', '\\"').replace("\n", "\\n")
        content = content.replace("\n", "\\n")
        script = f'renderContent("{content}");'
        self._webview.evaluate_javascript(script, -1)

    def _setup_webview(self):
        webview = WebKit.WebView()
        webview.set_margin_top(12)
        webview.set_vexpand(True)
        webview.set_hexpand(True)
        webview.set_size_request(100, 100)

        context = webview.get_context()
        if not getattr(context, "_lean_app_scheme_registered", False):
            context._lean_app_scheme_registered = True
            context.register_uri_scheme("app", _handle_resource_request)

        base_uri = "app:///result_page/index.html"
        GLib.idle_add(webview.load_uri, base_uri)

        settings = webview.get_settings()
        settings.set_enable_developer_extras(True)
        settings.set_enable_developer_extras(True)
        settings.set_enable_back_forward_navigation_gestures(False)
        settings.set_enable_smooth_scrolling(False)

        return webview

    def _on_regenerate_clicked(self, _):
        self.emit("regenerate-clicked")

    def _on_next_clicked(self, _):
        self.emit("next-clicked")

    def _on_thinking_toggled(self, button):
        is_active = button.get_active()
        state_text = "enabled" if is_active else "disabled"
        button.set_tooltip_text(f"Thinking mode ({state_text})")
        self.emit("thinking-toggled", is_active)
