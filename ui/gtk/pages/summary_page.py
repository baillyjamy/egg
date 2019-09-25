from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
from ui.gtk.pages.page import Page
from ui.gtk.main_window_button import MainWindowButton
import threading


class SummaryRow(Gtk.Frame):
    vbox = None
    titleLabel = None
    def __init__(self, icon, title):
        Gtk.Frame.__init__(self)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon, 50, 50, False)
        image.set_from_pixbuf(pixbuf)
        image.set_property("margin", 10)
        image.set_valign(Gtk.Align.START)
        box.pack_start(image, False, False, 0)

        self.titleLabel = Gtk.Label("<big>{}</big>".format(title))
        self.titleLabel.set_use_markup(True)
        box.pack_start(self.titleLabel, False, False, 0)
        self.titleLabel.set_halign(Gtk.Align.START)
        self.titleLabel.set_valign(Gtk.Align.START)
        self.titleLabel.set_property("margin", 10)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.pack_end(self.vbox, False, False, 0)
        self.vbox.set_property("margin", 10)

        self.add(box)

    def update_title(self, title):
        self.titleLabel.set_markup("<big>{}</big>".format(title))

    def add_label(self, label):
        self.vbox.pack_start(label, False, False, 2)
        label.show_all()

    def clean_label(self):
        for current in self.vbox.get_children():
            current.destroy()

class ContentLabel(Gtk.Label):
    
    def __init__(self, title):
        Gtk.Label.__init__(self, title)
        
        self.set_halign(Gtk.Align.END)


class Components():
    _components = {}
    
    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["general_scroll"] = Gtk.ScrolledWindow(None, None)
        self._components["items_box"] = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

    def get_component(self, component_name):
        return self._components[component_name]

class SummarryPage(Page):
    _components = None
    _language_page = None
    _timezone_page = None
    _disk_page = None
    _partition_page = None
    _user_page = None

    def __init__(self, language_manager, config_general):
        super(SummarryPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._components = Components()
        self._win_parent = None

        self.init_components(language_manager, config_general)
        self.refresh_ui_language()

    def init_components(self, language_manager, config_general):
        self._components.get_component("general_scroll").set_border_width(40)
        self._components.get_component("general_scroll").set_margin_top(20)
        self._components.get_component("general_scroll").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("general_scroll").add(self._components.get_component("items_box"))
        self._components.get_component("general_scroll").set_overlay_scrolling(False)
        self._components.get_component("general_box").pack_start(self._components.get_component("general_scroll"), True, True, 0)

        self._language_page = SummaryRow(config_general["config_page"]["language_installation"]["icon"],
            language_manager.translate_msg("language_installation_page", "sidebar_title"))
        self._components.get_component("items_box").pack_start(self._language_page, False, False, 2)
        
        self._timezone_page = SummaryRow(config_general["config_page"]["timezone"]["icon"],
            language_manager.translate_msg("timezone_page", "sidebar_title"))
        self._components.get_component("items_box").pack_start(self._timezone_page, False, False, 2)

        self._disk_page = SummaryRow(config_general["config_page"]["selection_disk"]["icon"],
            language_manager.translate_msg("selection_disk_page", "sidebar_title"))
        self._components.get_component("items_box").pack_start(self._disk_page, False, False, 2)

        self._partition_page = SummaryRow(config_general["config_page"]["partition_disk"]["icon"],
            language_manager.translate_msg("partition_disk_page", "sidebar_title"))
        self._components.get_component("items_box").pack_start(self._partition_page, False, False, 2)

        self._user_page = SummaryRow(config_general["config_page"]["user"]["icon"],
            language_manager.translate_msg("user_page", "sidebar_title"))
        #self._components.get_component("items_box").pack_start(self._user_page, False, False, 2)


    def load_win(self, win):
        self._win_parent = win

    def refresh_ui_language(self):
        self._language_page.update_title(self._language_manager.translate_msg("language_installation_page", "sidebar_title"))
        self._timezone_page.update_title(self._language_manager.translate_msg("timezone_page", "sidebar_title"))
        self._disk_page.update_title(self._language_manager.translate_msg("selection_disk_page", "sidebar_title"))
        self._partition_page.update_title(self._language_manager.translate_msg("partition_disk_page", "sidebar_title"))
        self._user_page.update_title(self._language_manager.translate_msg("user_page", "sidebar_title"))
        self.set_pages_content()

    def long_task(self):
        Gdk.threads_enter()
        Gdk.threads_leave()

    def set_pages_content(self):
        locale = ""
        locale_sz = ""
        keyboard = ""
        keyboard_sz = ""
        timezone_zone = ""
        timezone_country = ""
        selection_disk_page = ""
        selection_partition_page = ""

        if "language_installation_page" in self._config_general and "locale" in self._config_general["language_installation_page"] and self._config_general["language_installation_page"]["locale"] is not None: # changer ici installation
            locale = self._config_general["language_installation_page"]["locale"]
        if "language_installation_page" in self._config_general and "locale_sz" in self._config_general["language_installation_page"] and self._config_general["language_installation_page"]["locale_sz"] is not None:
            locale_sz = self._config_general["language_installation_page"]["locale_sz"]
        if "language_installation_page" in self._config_general and "keyboard" in self._config_general["language_installation_page"] and self._config_general["language_installation_page"]["keyboard"] is not None:
            keyboard = self._config_general["language_installation_page"]["keyboard"]
        if "language_installation_page" in self._config_general and "keyboard_sz" in self._config_general["language_installation_page"] and self._config_general["language_installation_page"]["keyboard_sz"] is not None:
            keyboard_sz = self._config_general["language_installation_page"]["keyboard_sz"]

        if "timezone_page" in self._config_general and "timezone_zone" in self._config_general["timezone_page"] and self._config_general["timezone_page"]["timezone_zone"] is not None:
            timezone_zone = self._config_general["timezone_page"]["timezone_zone"]
        if "timezone_page" in self._config_general and "timezone_country" in self._config_general["timezone_page"] and self._config_general["timezone_page"]["timezone_country"] is not None:
            timezone_country = self._config_general["timezone_page"]["timezone_country"]

        if "selection_disk_page" in self._config_general and "current_disk" in self._config_general["selection_disk_page"] and self._config_general["selection_disk_page"]["current_disk"] is not None:
            selection_disk_page = self._config_general["selection_disk_page"]["current_disk"].get_disk_name()

        if "partition_disk" in self._config_general and "partitions" in self._config_general["partition_disk"] and self._config_general["partition_disk"]["partitions"] is not None:
            selection_partition_page = self._config_general["partition_disk"]["partitions"]        

        self._language_page.clean_label()
        self._language_page.add_label(ContentLabel(self._language_manager.translate_msg("summary_page", "installation_language") + " " + locale_sz + " (" + locale + ")"))
        self._language_page.add_label(ContentLabel(self._language_manager.translate_msg("summary_page", "installation_keyboard") + " " + keyboard_sz + " (" + keyboard + ")" ))

        self._timezone_page.clean_label()
        self._timezone_page.add_label(ContentLabel(self._language_manager.translate_msg("summary_page", "installation_timezone")))
        self._timezone_page.add_label(ContentLabel(timezone_zone + " (" + timezone_country + ")"))

        self._disk_page.clean_label()
        self._disk_page.add_label(ContentLabel(self._language_manager.translate_msg("summary_page", "installation_disk")))
        self._disk_page.add_label(ContentLabel(selection_disk_page))

        self._partition_page.clean_label()
        self._partition_page.add_label(ContentLabel(self._language_manager.translate_msg("summary_page", "installation_partition")))
        if selection_partition_page is not "":
            for current in selection_partition_page:
                self._partition_page.add_label(ContentLabel(current.get_partition_desc()))

        self._user_page.clean_label()


    def load_page(self):
        self.set_pages_content()
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
    
    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("summary_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("summary_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["summary"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["summary"]["icon"]