from gi.repository import Gtk, Gdk, GnomeDesktop
from ui.gtk.main_window_button import MainWindowButton
from ui.gtk.pages.page import Page
from egg.user_management import UserManagement


class FieldsEntry(Gtk.Entry):
    entry_id = None
    entry_text = None
    entry_placeholder = None

    def __init__(self, entry_id, text, placeholder, hidden, callback=None):
        Gtk.Entry.__init__(self)
        self.entry_id = entry_id
        self.entry_text = text
        self.entry_placeholder = placeholder

        if hidden is True:
            self.set_visibility(False)
        if callback is not None:
            self.connect("changed", callback)
        self.set_hexpand(True)
        self.set_placeholder_text(self.entry_placeholder)
        self.set_text(self.entry_text)
    
    def update_text(self, textupdate):
        self.set_text(textupdate)


class Components():
    _components = {}

    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self._components["general_grid"] = Gtk.Grid()
        self._components["general_root_label"] = Gtk.Label()
        self._components["general_username_label"] = Gtk.Label()

        self._components["root_password_entry_label"] = Gtk.Label()
        self._components["root_validation_password_entry_label"] = Gtk.Label()

        self._components["username_real_name_entry_label"] = Gtk.Label()
        self._components["username_entry_label"] = Gtk.Label()
        self._components["username_password_entry_label"] = Gtk.Label()
        self._components["username_validation_password_entry_label"] = Gtk.Label()

    def get_component(self, component_name):
        return self._components[component_name]

    def add_component(self, component_name, component):
        self._components[component_name] = component


class UserPage(Page):
    _components = None
    _win_parent = None
    _user_management = None
    _username_changed = False

    def __init__(self, language_manager, config_general):
        super(UserPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._config_general["user_page"] = {}
        self._config_general["user_page"]["root_password"] = None
        self._config_general["user_page"]["user_username"] = None
        self._config_general["user_page"]["user_realfullname"] = None
        self._config_general["user_page"]["user_password"] = None

        # self._components.get_component("root_password_entry").add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._user_management = UserManagement()
        self._components = Components()
        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        # General grid
        self._components.get_component("general_box").pack_start(self._components.get_component("general_grid"), True,
                                                                 True, 1)
        self._components.get_component("general_grid").set_margin_start(10)
        self._components.get_component("general_grid").set_margin_end(10)
        self._components.get_component("general_grid").set_margin_top(10)
        self._components.get_component("general_grid").set_margin_bottom(10)
        self._components.get_component("general_grid").set_row_spacing(0)
        # Entry grid
        #         .entry {
        #     border-color: Red;
        # }
        # d = self._components.get_component("root_password_entry")
        # css = Gtk.CssProvider()
        # t = b'''
        # .popup {background-color: rgba(0,0,0,0); border: 0px rgba(255,255,255,0);  border-radius: 14px; border-width: 0;  }
        # '''
        # css.load_from_data(t)
        # self._components.get_component("root_password_entry").set_style(t)
        # self._components.get_component("root_password_entry").get_style_context().add_class('popup')

        self._components.get_component("general_root_label").set_markup(u"<span font-size='x-large'>{}</span>".format(
            self._language_manager.translate_msg("user_page", "root_configuration_title") + " :"))
        self._components.get_component("root_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "password_entry_label") + " :")
        self._components.get_component("root_validation_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "validation_password_entry_label") + " :")

        self._components.add_component("root_password_entry",
           FieldsEntry("root_password_entry", "", "", True, self.check_root_password))
        self._components.add_component("root_validation_password_entry",
           FieldsEntry("root_validation_password_entry", "", "", True, self.check_root_validation_password))

        self._components.get_component("general_username_label").set_markup(
            u"<span font-size='x-large'>{}</span>".format(
                self._language_manager.translate_msg("user_page", "user_configuration_title") + " :"))
        self._components.get_component("username_real_name_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "user_real_name_entry_label") + " :")
        self._components.get_component("username_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "user_entry_label") + " :")
        self._components.get_component("username_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "password_entry_label") + " :")
        self._components.get_component("username_validation_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "validation_password_entry_label") + " :")

        self._components.add_component("username_real_name_entry", FieldsEntry("username_real_name_entry", "",
           self._language_manager.translate_msg( "user_page",  "user_real_placeholder_entry"), False, self.check_user_fullname))
        self._components.add_component("username_entry", FieldsEntry("username_entry", "",
            self._language_manager.translate_msg("user_page", "user_placeholder_entry"), False, self.check_user_username))
        self._components.add_component("username_password_entry", FieldsEntry("username_password_entry", "", "", True, self.check_user_password))

        self._components.add_component("username_validation_password_entry",
                                       FieldsEntry("username_validation_password_entry", "",
                                                   "", True, self.check_user_validation_password))

        # Attach general grid
        self._components.get_component("general_grid").attach(self._components.get_component("general_root_label"), 0,
                                                              0, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("root_password_entry_label"), 0, 1, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("root_password_entry"), 0,
                                                              2, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("root_validation_password_entry_label"), 0, 3, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("root_validation_password_entry"), 0, 4, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("general_username_label"),
                                                              0, 5, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("username_real_name_entry_label"), 0, 6, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("username_real_name_entry"), 0, 7, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("username_entry_label"), 0,
                                                              8, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("username_entry"), 0, 9, 1,
                                                              1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("username_password_entry_label"), 0, 10, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("username_password_entry"),
                                                              0, 11, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("username_validation_password_entry_label"), 0, 12, 1, 1)
        self._components.get_component("general_grid").attach(
            self._components.get_component("username_validation_password_entry"), 0, 13, 1, 1)

    def set_button_visiblity_depending_config(self):
        if ("root_password" in self._config_general["user_page"]
                and self._config_general["user_page"]["root_password"] is not None
                and "user_username" in self._config_general["user_page"]
                and self._config_general["user_page"]["user_username"] is not None
                and "user_realfullname" in self._config_general["user_page"]
                and self._config_general["user_page"]["user_realfullname"] is not None
                and "user_password" in self._config_general["user_page"]
                and self._config_general["user_page"]["user_password"] is not None):
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)

    def check_root_password(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()
        root_validation_password = self._components.get_component("root_validation_password_entry").get_text()

        if self._user_management.check_validity_password(content) and content == root_validation_password:
            self._config_general["user_page"]["root_password"] = content
        else:
            self._config_general["user_page"]["root_password"] = None
            return
        self.set_button_visiblity_depending_config()

    def check_root_validation_password(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()
        root_password = self._components.get_component("root_password_entry").get_text()

        if self._user_management.check_validity_password(content) and content == root_password:
            self._config_general["user_page"]["root_password"] = content
        else:
            self._config_general["user_page"]["root_password"] = None
            return
        self.set_button_visiblity_depending_config()

    def check_user_fullname(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()

        if self._username_changed == False:
            username_component = self._components.get_component("username_entry") 
            username_component.update_text(self._user_management.get_recommanded_user_name(content))
        if self._user_management.check_validity_fullname(content):
            self._config_general["user_page"]["user_realfullname"] = content
        else:
            self._config_general["user_page"]["user_realfullname"] = None
            return
        self.set_button_visiblity_depending_config()

    def check_user_username(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()

        # self._username_changed = True
        if self._user_management.check_validity_user_name(content):
            self._config_general["user_page"]["user_username"] = content
        else:
            self._config_general["user_page"]["user_username"] = None
            return
        self.set_button_visiblity_depending_config()

    def check_user_password(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()
        root_validation_password = self._components.get_component("username_validation_password_entry").get_text()

        if self._user_management.check_validity_password(content) and content == root_validation_password:
            self._config_general["user_page"]["user_password"] = content
        else:
            self._config_general["user_page"]["user_password"] = None
            return
        self.set_button_visiblity_depending_config()

    def check_user_validation_password(self, data):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        content = data.get_text()
        root_password = self._components.get_component("username_password_entry").get_text()

        if self._user_management.check_validity_password(content) and root_password:
            self._config_general["user_page"]["user_password"] = content
        else:
            self._config_general["user_page"]["user_password"] = None
            return
        self.set_button_visiblity_depending_config()

        # uname_label = Gtk.Label("Username:")
        # self.uname_field = Gtk.Entry()
        # self.uname_field.set_hexpand(True)
        # self.uname_field.connect("changed", self.validator)
        # self.attach(uname_label, LABEL_COLUMN, row, 1, 1)
        # self.attach(self.uname_field, DATA_COLUMN, row, 1, 1)

    def long_task(self):
        pass

    def load_win(self, win):
        self._win_parent = win

    def load_page(self):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        self.set_button_visiblity_depending_config()

    def refresh_ui_language(self):
        # self._components.get_component("username_real_name_entry").set_placeholder_text(self._language_manager.translate_msg("user_page", "user_real_placeholder_entry"))
        self._components.get_component("general_root_label").set_markup(u"<span font-size='x-large'>{}</span>".format(
            self._language_manager.translate_msg("user_page", "root_configuration_title") + " :"))

        self._components.get_component("root_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "password_entry_label") + " :")
        self._components.get_component("root_validation_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "validation_password_entry_label") + " :")

        self._components.get_component("general_username_label").set_markup(
            u"<span font-size='x-large'>{}</span>".format(
                self._language_manager.translate_msg("user_page", "user_configuration_title") + " :"))
        self._components.get_component("username_real_name_entry").set_placeholder_text(
            self._language_manager.translate_msg("user_page", "user_real_placeholder_entry"))
        self._components.get_component("username_entry").set_placeholder_text(
            self._language_manager.translate_msg("user_page", "user_placeholder_entry"))

        self._components.get_component("username_real_name_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "user_real_name_entry_label") + " :")
        self._components.get_component("username_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "user_entry_label") + " :")
        self._components.get_component("username_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "password_entry_label") + " :")
        self._components.get_component("username_validation_password_entry_label").set_label(
            self._language_manager.translate_msg("user_page", "validation_password_entry_label") + " :")

    # page title
    def get_page_title(self):
        return self._language_manager.translate_msg("user_page", "title")

    # page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("user_page", "sidebar_title")

    # page id
    def get_page_id(self):
        return self._config_general["config_page"]["user"]["id"]

    # icon
    def get_page_icon(self):
        return self._config_general["config_page"]["user"]["icon"]
