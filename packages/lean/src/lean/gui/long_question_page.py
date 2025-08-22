from gi.repository import Gio

from .ask_view import AskView


class LongQuestionPage(AskView):
    def __init__(self, session_manager, **kwargs):
        super().__init__(session_manager=session_manager, **kwargs)
        self._settings = Gio.Settings.new("dev.vipulog.lean")
        self._settings.connect("changed::long-question-prompt", self._on_prompt_changed)
        self.set_prompt(self._settings.get_string("long-question-prompt"))

    def _on_prompt_changed(self, settings, key):
        self.set_prompt(settings.get_string(key))
