from egg.tz import Database
from ui.gtk.main_window_button import MainWindowButton
from ui.gtk.pages.page import Page

from gi.repository import TimezoneMap, Gtk, Gdk, GLib
import urllib.request
import geoip2.database
import json
import threading

class Components():
    _components = {}
    
    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["frame_window"] = Gtk.Frame()
        self._components["tz_map"] = TimezoneMap.TimezoneMap()
        self._components["city_entry"] = Gtk.Entry()
        self._components["tz_completion"] = TimezoneMap.TimezoneCompletion()

    def get_component(self, component_name):
        return self._components[component_name]

class TimezonePage(Page):
    db = None
    timeout = 10
    _components = None

    def __init__(self, language_manager, config_general):
        super(TimezonePage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._components = Components()
        self._win_parent = None
        self._config_general["timezone_page"] = {}

        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        self._components.get_component("frame_window").set_shadow_type(Gtk.ShadowType.NONE)
        self._components.get_component("general_box").pack_start(self._components.get_component("frame_window"), True, True, 0)
        self._components.get_component("frame_window").set_margin_end(0)
        self._components.get_component("frame_window").set_margin_start(0)
        self._components.get_component("frame_window").add(self._components.get_component("tz_map"))

        self._components.get_component("city_entry").set_property("margin-right", 30)
        self._components.get_component("city_entry").set_property("margin-start", 30)
        self._components.get_component("city_entry").set_property("margin-top", 10)
        self._components.get_component("general_box").pack_end(self._components.get_component("city_entry"), False, False, 0)


        self._components.get_component("tz_completion").set_text_column(0)
        self._components.get_component("tz_completion").set_inline_completion(True)
        self._components.get_component("tz_completion").set_inline_selection(True)
        self._components.get_component("tz_completion").connect("match-selected", self.change_timezone)
        self._components.get_component("city_entry").set_completion(self._components.get_component("tz_completion"))
        self._components.get_component("tz_map").connect("location-changed", self.changed)

    def load_win(self, win):
        self._win_parent = win

    def refresh_ui_language(self):
        self._components.get_component("city_entry").set_placeholder_text(self._language_manager.translate_msg("timezone_page", "timezone_placeholder_search_entry") + u"…")

    def long_task(self):
        self.db = Database()

        tz_model = Gtk.ListStore(str, str, str, str, float, float, str)

        for item in self.db.locations:
            tz_model.append([item.human_zone, item.human_country,  None,
                             item.country, item.longitude, item.latitude,
                             item.zone])

        Gdk.threads_enter()
        self._components.get_component("city_entry").get_completion().set_model(tz_model)
        self.schedule_lookup()
        Gdk.threads_leave()

    def change_timezone(self, completion, model, selection):
        item = model[selection]
        zone = item[6]
        self._components.get_component("tz_map").set_timezone(zone)

    def changed(self, map, location):
        zone = location.get_property("zone")
        nice_loc = self.db.tz_to_loc[zone]

        self.timezone_human = "{} ({})".format(nice_loc.human_zone,
                                               nice_loc.human_country)
        self._components.get_component("tz_map").set_watermark(self.timezone_human)
        self._components.get_component("city_entry").set_text(nice_loc.human_zone)

        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        self._config_general["timezone_page"]["timezone_zone"] = zone
        self._config_general["timezone_page"]["timezone_country"] = location.get_property("country")

    def load_page(self):

        if "timezone_zone" in self._config_general["timezone_page"]:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        else:
            if "timezone_zone" in self._config_general["timezone_page"]:
                self._components.get_component("tz_map").set_timezone(self._config_general["timezone_page"]["timezone_zone"])
                self.timezone = self._config_general["timezone_page"]["timezone_zone"]
                self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
            else:
                self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
    
    def schedule_lookup(self):
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
        self._win_parent.set_button_action_visibility(MainWindowButton.PREV, False)
        GLib.idle_add(self.begin_thread)

    def begin_thread(self):
        t = threading.Thread(target=self.perform_lookup)
        t.start()
        return False

    def get_ip_info(self):
        try:
            with urllib.request.urlopen(self._config_general["url_check_ip"], None, self.timeout) as response:
               contents = json.loads(response.read())
            return str(contents["query"]), str(contents["countryCode"]), str(contents["timezone"])
        except Exception as e:
            pass
        return None

    def perform_lookup(self):
        try:
            ip, iso_code, timezone = self.get_ip_info()
            if ip is None or iso_code is None or timezone is None:
                self._win_parent.set_button_action_visibility(MainWindowButton.PREV, True)
                self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
                return

            self._config_general["timezone_page"]["timezone_country"] = iso_code # FR
            self._config_general["timezone_page"]["timezone_zone"] = timezone # EUROPE/PARIS
            self._components.get_component("tz_map").set_timezone(self._config_general["timezone_page"]["timezone_zone"])
            self._win_parent.set_button_action_visibility(MainWindowButton.PREV, True)
        except Exception as e:
            self._win_parent.set_button_action_visibility(MainWindowButton.PREV, True)
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)


    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("timezone_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("timezone_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["timezone"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["timezone"]["icon"]