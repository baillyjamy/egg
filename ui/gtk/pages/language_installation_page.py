from gi.repository import Gtk, GnomeDesktop, Gdk
from ui.gtk.pages.page import Page
from ui.gtk.main_window_button import MainWindowButton
import subprocess
import locale

class KeyboardLabel(Gtk.Label):
    keyboard_name = None
    keyboard_id = None

    def __init__(self, keyboard_id, keyboard_name):
        Gtk.Label.__init__(self)
        self.keyboard_id = keyboard_id
        self.keyboard_name = keyboard_name

        self.set_property("margin", 10)
        self.set_halign(Gtk.Align.START)
        self.set_text(self.keyboard_name)
        self.show()

class LanguageLabel(Gtk.Label):
    language_code = None
    language_name = None

    def __init__(self, language_code, language_name):
        Gtk.Label.__init__(self)
        self.language_code = language_code
        self.language_name = language_name

        self.set_property("margin", 8)
        self.set_halign(Gtk.Align.START)
        self.set_text(self.language_name)
        self.show()

class Components():
    _components = {}
    
    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["general_grid"] = Gtk.Grid()
        self._components["scroll_language_win"] = Gtk.ScrolledWindow(None, None)
        self._components["scroll_keyboard_win"] = Gtk.ScrolledWindow(None, None)
        self._components["listbox_language_win"] = Gtk.ListBox()
        self._components["listbox_keyboard_win"] = Gtk.ListBox()
        self._components["more_button_language_win"] = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                        Gtk.IconSize.MENU)
        self._components["more_button_keyboard_win"] = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                        Gtk.IconSize.MENU)
        self._components["label_language_win"] = Gtk.Label()
        self._components["label_keyboard_win"] = Gtk.Label()
        self._components["grid_keyboard_win"] = Gtk.Grid()
        self._components["input_keyboard_win"] = Gtk.Entry()

    def get_component(self, component_name):
        return self._components[component_name]

class LanguageInstallationPage(Page):
    _components = None
    _win_parent = None

    keyboard_already_showed = set()
    country_depending_keyboard = list()
    nb_default_languages = 7
    nb_default_keyboard = 7
    
    def __init__(self, language_manager, config_general):
        super(LanguageInstallationPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._config_general["language_installation_page"] = {}
        self._config_general["language_installation_page"]["locale"] = self._language_manager.current_language

        self._config_general["language_installation_page"]["language_next"] = False
        self._config_general["language_installation_page"]["keyboard_next"] = False
        self._win_parent = None

        self._components = Components()
        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        # General grid
        self._components.get_component("general_box").pack_start(self._components.get_component("general_grid"), True, True, 0)
        self._components.get_component("general_grid").set_margin_start(10)
        self._components.get_component("general_grid").set_margin_end(10)
        self._components.get_component("general_grid").set_margin_top(10)
        self._components.get_component("general_grid").set_margin_bottom(10)
        self._components.get_component("general_grid").set_column_spacing(50)
        self._components.get_component("general_grid").set_row_spacing(5)
        self._components.get_component("general_grid").set_halign(Gtk.Align.START)

        # Language box
        self._components.get_component("scroll_language_win").set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self._components.get_component("scroll_language_win").add(self._components.get_component("listbox_language_win"))

        self._components.get_component("scroll_language_win").set_halign(Gtk.Align.CENTER)
        self._components.get_component("listbox_language_win").set_size_request(60, -1)

        self._components.get_component("scroll_language_win").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self._components.get_component("more_button_language_win").set_property("margin", 8)
        self._components.get_component("more_button_language_win").show_all()
        self._components.get_component("listbox_language_win").connect_after("row-selected", self.on_row_click_language)

        # Title for box
        self._components.get_component("label_language_win").set_halign(Gtk.Align.START)
        self._components.get_component("label_language_win").set_line_wrap(True)

        self._components.get_component("label_keyboard_win").set_halign(Gtk.Align.START)
        self._components.get_component("label_keyboard_win").set_line_wrap(True)

        # Keyboard box
        self._components.get_component("grid_keyboard_win").set_row_spacing(6)
        self._components.get_component("grid_keyboard_win").set_halign(Gtk.Align.CENTER)

        self._components.get_component("listbox_keyboard_win").set_size_request(60, -1)

        self._components.get_component("scroll_keyboard_win").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("scroll_keyboard_win").add(self._components.get_component("listbox_keyboard_win"))
        self._components.get_component("scroll_keyboard_win").set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self._components.get_component("scroll_keyboard_win").set_vexpand(True)
        self._components.get_component("grid_keyboard_win").attach(self._components.get_component("scroll_keyboard_win"), 0, 0, 2, 1)

        # Input tester
        self._components.get_component("grid_keyboard_win").attach(self._components.get_component("input_keyboard_win"), 0, 1, 2, 1)
        self._components.get_component("more_button_keyboard_win").set_property("margin", 8)
        self._components.get_component("listbox_keyboard_win").connect_after("row-selected", self.on_row_click_keyboard)

        # Attach general grid
        self._components.get_component("general_grid").attach(self._components.get_component("scroll_language_win"), 0, 1, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("label_language_win"), 0, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("label_keyboard_win"), 1, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("grid_keyboard_win"), 1, 1, 1, 1)

    def on_row_click_language(self, list_box_language, current_row_language_clicked=None):

        if not current_row_language_clicked:
            self._config_general["language_installation_page"]["locale"] = None
            self._config_general["language_installation_page"]["locale_sz"] = None
            self._config_general["language_installation_page"]["language_next"] = False
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
            return

        row_elem = current_row_language_clicked.get_child()
        if row_elem != self._components.get_component("more_button_language_win"):
            self._config_general["language_installation_page"]["locale"] = row_elem.language_code
            self._config_general["language_installation_page"]["locale_sz"] = row_elem.language_name

            self._config_general["language_installation_page"]["language_next"] = True
            if self._config_general["language_installation_page"]["language_next"] and self._config_general["language_installation_page"]["keyboard_next"]:
                self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
            return

        self._components.get_component("scroll_language_win").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("scroll_language_win").set_vexpand(True)
        self._components.get_component("scroll_language_win").set_valign(Gtk.Align.FILL)
        self._components.get_component("more_button_language_win").get_parent().hide()
        languages = GnomeDesktop.get_all_locales()
        languages_keys = list(languages)[0:self.nb_default_languages]
        languages_extra = list()
        for lc in languages:
            if lc in languages_keys:
                continue
            language = GnomeDesktop.get_language_from_locale(lc)
            item = LanguageLabel(lc, language)
            languages_extra.append(item)
            
        languages_extra.sort(key=lambda sort: sort.language_name.lower())
        for current in languages_extra:
            self._components.get_component("listbox_language_win").add(current)

    def on_row_click_keyboard(self, list_box_keyboard, current_row_keyboard_clicked=None):
        if not current_row_keyboard_clicked:
            self._config_general["language_installation_page"]["keyboard"] = None
            self._config_general["language_installation_page"]["keyboard_sz"] = None
            self._config_general["language_installation_page"]["keyboard_next"] = False
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
            return

        row_elem = current_row_keyboard_clicked.get_child()
        if row_elem != self._components.get_component("more_button_keyboard_win"):
            self._config_general["language_installation_page"]["keyboard"] = row_elem.keyboard_id
            self._config_general["language_installation_page"]["keyboard_sz"] = row_elem.keyboard_name
            self.set_keyboard()
            self._config_general["language_installation_page"]["keyboard_next"] = True
            if self._config_general["language_installation_page"]["language_next"] and self._config_general["language_installation_page"]["keyboard_next"]:
                self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
            self._components.get_component("input_keyboard_win").set_text("")
            return

        self._components.get_component("more_button_keyboard_win").get_parent().hide()

        keyboardInfo = GnomeDesktop.XkbInfo()
        all_keyboard_code_info = keyboardInfo.get_all_layouts()
        all_expand_languages = list()


        for current in self.country_depending_keyboard:
            if not current.keyboard_id in self.keyboard_already_showed:
                self.keyboard_already_showed.add(current.keyboard_id)
                all_expand_languages.append(current)

        for current in all_keyboard_code_info:
            if not current in self.keyboard_already_showed:
                info = keyboardInfo.get_layout_info(current)
                if info[0]:
                    all_expand_languages.append(KeyboardLabel(current, info.display_name))

        all_expand_languages.sort(key=lambda sort: sort.keyboard_name.lower())
        for current in all_expand_languages:
            if not current.keyboard_id in self.keyboard_already_showed:
                self._components.get_component("listbox_keyboard_win").add(current)
        self.set_selected_keyboard_row()


    def init_view_keyboard(self):
        keyboardInfo = GnomeDesktop.XkbInfo()
        country = self._language_manager.get_detailed_locale_country(self._config_general["language_installation_page"]["locale"])
        country_lower = country.lower()
        input_locale = GnomeDesktop.get_input_source_from_locale(self._language_manager.get_detailed_locale(self._config_general["language_installation_page"]["locale"]))

        keyboard_depending_language = list([input_locale.id])
        keyboard_depending_language_after = list()
        all_keyboard_and_extra = list()

        all_keyboard = keyboardInfo.get_all_layouts()
        for current in all_keyboard:
            info = keyboardInfo.get_layout_info(current)
            if not info[0]:
                continue
            if info[3].lower() == country_lower:
                keyboard_depending_language_after.append(current)

        keyboard_depending_language_after.remove(input_locale.id)
        keyboard_depending_language_after = sorted(keyboard_depending_language_after)
        keyboard_depending_language.extend(keyboard_depending_language_after)

        for current in keyboard_depending_language:
            info = keyboardInfo.get_layout_info(current)
            if info[0]:
                all_keyboard_and_extra.append(KeyboardLabel(current, info.display_name))

        for current in all_keyboard_and_extra:
            if current.keyboard_id in self.keyboard_already_showed:
                continue
            if len(self.keyboard_already_showed) >= self.nb_default_keyboard:
                self.country_depending_keyboard.append(current)
                continue
            self.keyboard_already_showed.add(current.keyboard_id)
            self._components.get_component("listbox_keyboard_win").add(current)

        self._components.get_component("more_button_keyboard_win").show_all()
        self._components.get_component("listbox_keyboard_win").add(self._components.get_component("more_button_keyboard_win"))
        self.set_selected_keyboard_row()

    def set_keyboard(self):
        if "keyboard" in self._config_general["language_installation_page"] and self._config_general["language_installation_page"]["keyboard"] != None:
            try:
                subprocess.check_call("setxkbmap {}".format(self._config_general["language_installation_page"]["keyboard"]), shell=True)
            except Exception as e:
                pass

    def set_selected_keyboard_row(self):
        check_not_empty = self._components.get_component("listbox_keyboard_win").get_children()
        if not check_not_empty:
            return
        selected = self._components.get_component("listbox_keyboard_win").get_children()[0]
        self._components.get_component("listbox_keyboard_win").select_row(selected)

    def load_page(self):
        self.set_keyboard()
        self.set_selected_keyboard_row()

        if "locale" in self._config_general["language_installation_page"] and "keyboard" in self._config_general["language_installation_page"]:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        else:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)

    def long_task(self):
        Gdk.threads_enter()
        languages = self._language_manager.available_languages
        languages_keys = list(languages.keys())[0:self.nb_default_languages]
        languages_label = list()
        for key in languages_keys:
            languages_label.append(LanguageLabel(key, self._language_manager.translate_msg("language_installation_page", languages[key])))
        
        locales = GnomeDesktop.get_all_locales()
        locales.sort(key=lambda sort: sort.lower())
        languages = list(locales)[0:self.nb_default_languages]
        appends = list()
        for lc in languages:
            if lc in self._language_manager.available_languages:
                continue
            language = GnomeDesktop.get_language_from_locale(lc)
            item = LanguageLabel(lc, language)
            appends.append(item)
        appends.sort(key=lambda x: x.language_name.lower())
        for item in appends:
            self._components.get_component("listbox_language_win").add(item)

        self._components.get_component("listbox_language_win").add(self._components.get_component("more_button_language_win"))
        self.init_view_keyboard()
        Gdk.threads_leave()

    def load_win(self, win):
        self._win_parent = win

    def refresh_ui_language(self):
        self._components.get_component("label_language_win").set_markup(u"<span font-size='medium'>{}</span>".format(self._language_manager.translate_msg("language_live_page", "desc_language")))
        self._components.get_component("label_keyboard_win").set_markup(u"<span font-size='medium'>{}</span>".format(self._language_manager.translate_msg("language_live_page", "desc_keyboard")))
        self._components.get_component("input_keyboard_win").set_placeholder_text(self._language_manager.translate_msg("language_live_page", "input_keyboard"))

        languages = self._language_manager.available_languages
        keyboardInfo = GnomeDesktop.XkbInfo()

        # for current_row in self._components.get_component("listbox_language_win").get_children():
        #     label = current_row.get_child()
        #     if label != self._components.get_component("more_button_language_win"):
        #         label.language_name = self._language_manager.translate_msg("language_live_page", languages[label.language_code])
        #         label.set_text(label.language_name)

        for current_row in self._components.get_component("listbox_keyboard_win").get_children():
            label = current_row.get_child()
            if label != self._components.get_component("more_button_keyboard_win"):
                info = keyboardInfo.get_layout_info(label.keyboard_id)
                label.keyboard_name = info.display_name
                label.set_text(label.keyboard_name)        
    
    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("language_installation_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("language_installation_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["language_installation"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["language_installation"]["icon"]