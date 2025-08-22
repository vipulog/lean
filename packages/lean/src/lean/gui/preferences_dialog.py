from gi.repository import Adw, Gio, Gtk

from ..utils import secret_manager


def show_preferences(parent):
    dialog = PreferencesDialog()
    dialog.present(parent)
    return dialog


class PreferencesDialog(Adw.PreferencesDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._settings = Gio.Settings.new("dev.vipulog.lean")

        self._api_key_entry = Adw.EntryRow(title="Gemini API Key")
        self._api_key_entry.set_text(secret_manager.retrieve_api_key() or "")
        self._api_key_entry.connect("notify::text", self._on_api_key_changed)

        short_prompt_row = self._create_prompt_row(
            "short-question-prompt",
            "Short Question Prompt",
        )

        long_prompt_row = self._create_prompt_row(
            "long-question-prompt",
            "Long Question Prompt",
        )

        api_key_group = Adw.PreferencesGroup()
        api_key_group.add(self._api_key_entry)

        prompts_group = Adw.PreferencesGroup(title="Prompts")
        prompts_group.add(short_prompt_row)
        prompts_group.add(long_prompt_row)

        page = Adw.PreferencesPage()
        page.add(api_key_group)
        page.add(prompts_group)

        self.add(page)

    def _create_prompt_row(self, key, title):
        prompt_text = self._settings.get_string(key)

        buffer = Gtk.TextBuffer()
        buffer.set_text(prompt_text, -1)
        buffer.connect("changed", self._on_prompt_changed, key)

        text_view = Gtk.TextView(
            buffer=buffer,
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            height_request=120,
            margin_top=6,
            margin_bottom=6,
            margin_start=6,
            margin_end=6,
        )
        text_view.remove_css_class("view")

        row = Adw.ExpanderRow(title=title, expanded=True)
        row.add_row(text_view)
        return row

    def _on_api_key_changed(self, entry, _):
        secret_manager.store_api_key(entry.get_text())

    def _on_prompt_changed(self, buffer, key):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, True)
        self._settings.set_string(key, text)
