from gi.repository import Gtk


class LoadingPage(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        spinner = Gtk.Spinner(spinning=True, vexpand=True, hexpand=True)
        spinner.set_size_request(width=48, height=48)

        self.set_spacing(12)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.append(spinner)
