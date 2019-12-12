from ui.gtk.main_window_button import MainWindowButton
from ui.gtk.pages.page import Page
from gi.repository import Gtk, Gdk

class FieldsEntry(Gtk.Entry):
    entry_id = None
    entry_text = None
    entry_placeholder = None

    def __init__(self, entry_id, text, placeholder, hidden, expand, callback=None):
        Gtk.Entry.__init__(self)
        self.entry_id = entry_id
        self.entry_text = text
        self.entry_placeholder = placeholder

        if hidden is True:
            self.set_visibility(False)
        if callback is not None:
            self.connect("changed", callback)
        if expand is True:
            self.set_hexpand(True)
        self.set_placeholder_text(self.entry_placeholder)
        self.set_text(self.entry_text)
    
    def update_text(self, textupdate):
        self.set_text(textupdate)

class Components():
    _components = {}
    
    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["general_grid"] = Gtk.Grid()
        self._components["label_hostname_right"] = Gtk.Label()

    def get_component(self, component_name):
        return self._components[component_name]

    def add_component(self, component_name, component):
        self._components[component_name] = component

class NetworkPart2Page(Page):
    _components = None
    _win_parent = None

    def __init__(self, language_manager, config_general):
        super(NetworkPart2Page, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        if "network_page" not in self._config_general:
            self._config_general["network_page"] = {}
        self._config_general["network_page"]["hostname"] = None

        self._components = Components()
        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        self._components.add_component("entry_hostname_right",
            FieldsEntry("entry_hostname_right", "raven.localdomain", "", False, True, self.entry_hostname))

        self._components.get_component("general_grid").set_margin_start(10)
        self._components.get_component("general_grid").set_margin_end(10)
        self._components.get_component("general_grid").set_margin_top(10)
        self._components.get_component("general_grid").set_margin_bottom(10)
        self._components.get_component("general_grid").set_row_spacing(40)

        # General grid
        self._components.get_component("general_grid").attach(self._components.get_component("label_hostname_right"), 0, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("entry_hostname_right"), 0, 1, 1, 1)
        self._components.get_component("general_box").pack_start(self._components.get_component("general_grid"), True, True, 1)

    def entry_hostname(self, data):
        value = data.get_text()
        if value is "":
            value = None
        self._config_general["network_page"]["hostname"] = value
        self.enable_next_step()

    def long_task(self):
        Gdk.threads_enter()
        Gdk.threads_leave()

    def load_win(self, win):
        self._win_parent = win

    def enable_next_step(self):
        if self._win_parent is not None and 'hostname' in self._config_general['network_page'] and self._config_general['network_page']['hostname'] != None:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        elif self._win_parent is not None:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)

    def load_page(self):
        self.enable_next_step()

    def refresh_ui_language(self):        
        self._components.get_component("label_hostname_right").set_text(self._language_manager.translate_msg("network_part2_page", "network_hostname"))

    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("network_part2_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("network_part2_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["networkpart2"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["networkpart2"]["icon"]