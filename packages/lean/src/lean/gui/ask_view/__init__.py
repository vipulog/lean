from gi.repository import GLib, Gtk

from ...utils.ask_gemini import ask_gemini
from ...utils.logs import dump_error
from ...utils.screenshot import take_screenshot
from .error_page import ErrorPage
from .initial_page import InitialPage
from .loading_page import LoadingPage
from .result_page import ResultPage


class AskView(Gtk.Box):
    def __init__(self, session_manager, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self._prompt = (
            "You are an AI assistant that helps users by answering questions about "
            "their screen. Provide concise and helpful answers based on the provided "
            "screenshot."
        )
        self._think = False
        self._screenshot_path = None
        self._session_manager = session_manager

        self._initial_page = self._setup_initial_page()
        self._loading_page = LoadingPage()
        self._result_page = self._setup_result_page()
        self._error_page = self._setup_error_page()

        self._view_stack = Gtk.Stack()
        self._view_stack.add_named(self._initial_page, "initial")
        self._view_stack.add_named(self._loading_page, "loading")
        self._view_stack.add_named(self._result_page, "result")
        self._view_stack.add_named(self._error_page, "error")
        self._view_stack.set_visible_child_name("initial")

        self.set_spacing(12)
        self.append(self._view_stack)

    def set_prompt(self, prompt):
        self._prompt = prompt

    def _setup_initial_page(self):
        page = InitialPage()
        page.connect("ask-clicked", self._on_ask_clicked)
        page.connect("thinking-toggled", self._on_thinking_toggled)
        return page

    def _setup_result_page(self):
        page = ResultPage()
        page.connect("regenerate-clicked", self._on_regenerate_clicked)
        page.connect("next-clicked", self._on_ask_clicked)
        page.connect("thinking-toggled", self._on_thinking_toggled)
        return page

    def _setup_error_page(self):
        page = ErrorPage()
        page.connect("back-clicked", self._on_back_clicked)
        page.connect("retry-clicked", self._on_retry_clicked)
        return page

    def _on_ask_clicked(self, _):
        self._view_stack.set_visible_child_name("loading")
        take_screenshot(
            self._on_screenshot_success,
            self._on_screenshot_cancel,
            self._on_error,
        )

    def _on_regenerate_clicked(self, _):
        self._ask_ai(self._screenshot_path)

    def _on_back_clicked(self, _):
        self._view_stack.set_visible_child_name("initial")

    def _on_retry_clicked(self, _):
        if self._screenshot_path:
            self._ask_ai(self._screenshot_path)

    def _on_thinking_toggled(self, _, enabled):
        self._think = enabled
        self._initial_page.set_thinking_active(enabled)
        self._result_page.set_thinking_active(enabled)

    def _ask_ai(self, screenshot_path):
        self._view_stack.set_visible_child_name("loading")
        ask_gemini(
            self._prompt,
            screenshot_path,
            self._think,
            self._on_answer,
            self._on_error,
        )

    def _on_answer(self, response, in_tokens, out_tokens):
        self._session_manager.update_and_log(
            self._screenshot_path,
            in_tokens,
            out_tokens,
        )

        def _update():
            self._result_page.update_content(response, in_tokens, out_tokens)
            self._view_stack.set_visible_child_name("result")

        GLib.idle_add(_update)

    def _on_error(self, err):
        def _handle_error():
            log_path = dump_error(err)
            error_desc = GLib.markup_escape_text(str(err))
            description = (
                f"{error_desc}\n\n"
                "For more details, please check the log file at: "
                f"<b>{log_path}</b>"
            )
            self._error_page.set_description_text(description)
            self._view_stack.set_visible_child_name("error")

        GLib.idle_add(_handle_error)

    def _on_screenshot_success(self, screenshot_path):
        def _handle_success():
            self._screenshot_path = screenshot_path
            self._ask_ai(screenshot_path)

        GLib.idle_add(_handle_success)

    def _on_screenshot_cancel(self):
        GLib.idle_add(lambda: self._view_stack.set_visible_child_name("initial"))
