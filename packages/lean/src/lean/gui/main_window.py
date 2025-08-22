from gi.repository import Adw, Gio, Gtk

from ..utils.session_manager import SessionManager
from .about_dialog import show_about
from .long_question_page import LongQuestionPage
from .preferences_dialog import show_preferences
from .short_question_page import ShortQuestionPage


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._session_manager = SessionManager()

        menu = Gio.Menu.new()
        menu.append("Preferences", "app.preferences")
        menu.append("About lean", "app.about")
        popover = Gtk.PopoverMenu.new_from_model(menu)
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_popover(popover)

        self._short_page = ShortQuestionPage(session_manager=self._session_manager)
        self._long_page = LongQuestionPage(session_manager=self._session_manager)

        self._view_stack = self._setup_view_stack()
        self._view_switcher = Adw.ViewSwitcher()
        self._view_switcher.set_stack(self._view_stack)
        self._view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        self._window_title = Adw.WindowTitle(title="lean")
        self._header_bar = Adw.HeaderBar()
        self._header_bar.set_title_widget(self._view_switcher)
        self._header_bar.set_decoration_layout("icon:close")
        self._header_bar.pack_end(menu_button)

        view_switcher_bar = Adw.ViewSwitcherBar()
        view_switcher_bar.set_stack(self._view_stack)
        view_switcher_bar.set_reveal(False)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(self._header_bar)
        toolbar_view.set_content(self._view_stack)
        toolbar_view.add_bottom_bar(view_switcher_bar)

        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self._on_preferences_button_clicked)
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about_button_clicked)

        action_group = Gio.SimpleActionGroup()
        action_group.add_action(about_action)
        action_group.add_action(preferences_action)

        breakpoint = Adw.Breakpoint()
        breakpoint.set_condition(Adw.BreakpointCondition.parse("max-width: 520sp"))
        breakpoint.add_setter(view_switcher_bar, "reveal", True)
        breakpoint.connect("apply", self._on_breakpoint_apply)
        breakpoint.connect("unapply", self._on_breakpoint_unapply)

        self.set_default_size(540, 620)
        self.set_size_request(400, 400)
        self.set_title("lean")
        self.add_breakpoint(breakpoint)
        self.insert_action_group("app", action_group)
        self.set_content(toolbar_view)

    def _setup_view_stack(self):
        view_stack = Adw.ViewStack()
        short_icon = "view-list-symbolic"
        long_icon = "document-edit-symbolic"
        view_stack.add_titled_with_icon(self._short_page, "short", "Short", short_icon)
        view_stack.add_titled_with_icon(self._long_page, "long", "Long", long_icon)
        return view_stack

    def _on_preferences_button_clicked(self, _, __):
        show_preferences(self)

    def _on_about_button_clicked(self, _, __):
        show_about(self)

    def _on_breakpoint_apply(self, _):
        self._header_bar.set_title_widget(self._window_title)

    def _on_breakpoint_unapply(self, _):
        self._header_bar.set_title_widget(self._view_switcher)
