from ui.gtk.main_window_button import MainWindowButton
from ui.gtk.pages.page import Page
from egg.disk_management.diskservice import DiskService
from egg.network_management.wifi_service import WifiService
from egg.network_management.interfaces_service import NetworkInterfaces, NetworkIpAttributionType, NetworkType
from gi.repository import Gtk, Gdk
from egg.size_calculator import SizeCalculator

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

class NetworkCardLabel(Gtk.Label):
    networkConfiguration = None # Interface type wlan or eth
    
    def __init__(self, networkConfiguration):
        Gtk.Label.__init__(self)
        self.networkConfiguration = networkConfiguration

        self.set_property("margin", 8)
        self.set_halign(Gtk.Align.START)
        self.set_text(self.networkConfiguration.nameInterface + ": " + self.networkConfiguration.macAddress)
        self.show()

class WifiCardLabel(Gtk.Label):
    cell = None
    
    def __init__(self, cell):
        Gtk.Label.__init__(self)
        self.cell = cell

        self.set_property("margin", 8)
        self.set_halign(Gtk.Align.START)
        self.set_text(self.cell.ssid)
        self.show()

class NetworkAddressChooserRadioButton(Gtk.RadioButton):
    buttonid = None
    text = None

    def __init__(self, buttonid, text, button):
        Gtk.RadioButton.__init__(self, group=button)
        self.buttonid = buttonid
        self.text = text

        self.set_property("margin", 8)
        self.set_halign(Gtk.Align.START)
        self.set_label(self.text)
        self.show()

class Components():
    _components = {}
    
    def __init__(self):
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self._components["general_grid"] = Gtk.Grid()

        self._components["first_part"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._components["second_part"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["third_part"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)


        self._components["scroll_interfaces_window"] = Gtk.ScrolledWindow(None, None)
        self._components["listbox_interfaces_window"] = Gtk.ListBox()

        self._components["listbox_radio_selection"] = Gtk.ListBox()
        self._components["more_interfaces_button"] = Gtk.Image.new_from_icon_name("view-refresh-symbolic",
                                                        Gtk.IconSize.MENU)




        self._components["scroll_wifi_window"] = Gtk.ScrolledWindow(None, None)
        self._components["listbox_wifi_window"] = Gtk.ListBox()
        self._components["more_wifi_button"] = Gtk.Button()
        self._components["reload_wifi_button"] = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                        Gtk.IconSize.MENU)
        self._components["label_wifi_password"] = Gtk.Label()

        self._components["label_ip_address"] = Gtk.Label()
        self._components["label_netmask_address"] = Gtk.Label()
        self._components["label_gateway_address"] = Gtk.Label()
        self._components["label_nameserver1"] = Gtk.Label()
        self._components["label_nameserver2"] = Gtk.Label()

    def get_component(self, component_name):
        return self._components[component_name]

    def add_component(self, component_name, component):
        self._components[component_name] = component

class NetworkPage(Page):
    _components = None
    _win_parent = None
    _network_interfaces_service = None

    def __init__(self, language_manager, config_general):
        super(NetworkPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._config_general["network_page"] = {}
        self._config_general["network_page"]["current_interface_configuration"] = None
        self._config_general["network_page"]["hostname"] = None
        self._config_general["network_page"]["wifi_cell"] = None
        self._config_general["network_page"]["wifi_password"] = None

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
        self._components.get_component("general_grid").set_row_spacing(30)
        self._components.get_component("general_grid").set_column_spacing(35)

        self._components.get_component("more_interfaces_button").add(Gtk.Image.new_from_icon_name("view-more-symbolic", Gtk.IconSize.MENU))
        # Entry
        self._components.add_component("entry_ip_address",
            FieldsEntry("entry_ip_address", "", "", False, False, self.entry_ip_address))
        self._components.add_component("entry_netmask_address",
            FieldsEntry("entry_netmask_address", "", "", False, False, self.entry_netmask_address))
        self._components.add_component("entry_gateway_address",
            FieldsEntry("entry_gateway_address", "", "", False, False, self.entry_gateway_address))
        self._components.add_component("entry_nameserver1",
            FieldsEntry("entry_nameserver1", "", "", False, False, self.entry_nameserver1))
        self._components.add_component("entry_nameserver2",
            FieldsEntry("entry_nameserver2", "", "", False, False, self.entry_nameserver2))
        self._components.add_component("entry_wifi_password",
            FieldsEntry("entry_wifi_password", "", "", True, False, self.entry_wifi_password))

        # Interfaces box
        self._components.get_component("listbox_interfaces_window").set_size_request(60, -1)
        self._components.get_component("listbox_interfaces_window").connect_after("row-selected", self.on_row_select_interface)
        self._components.get_component("more_interfaces_button").show_all()

        self._components.get_component("scroll_interfaces_window").set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self._components.get_component("scroll_interfaces_window").add(self._components.get_component("listbox_interfaces_window"))
        self._components.get_component("scroll_interfaces_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)


        # Wifi box
        self._components.get_component("listbox_wifi_window").set_size_request(60, -1)
        self._components.get_component("listbox_wifi_window").connect_after("row-selected", self.on_row_select_wifi)
        self._components.get_component("more_wifi_button").show_all()

        self._components.get_component("scroll_wifi_window").set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self._components.get_component("scroll_wifi_window").add(self._components.get_component("listbox_wifi_window"))
        self._components.get_component("scroll_wifi_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)


        # Box
        self._components.get_component("listbox_radio_selection").set_size_request(60, -1)
        self._components.get_component("listbox_radio_selection").set_selection_mode(Gtk.SelectionMode.NONE)

        # Attach general grid
        self._components.get_component("first_part").pack_start(self._components.get_component("scroll_interfaces_window"), True, True, 0)
        self._components.get_component("first_part").pack_start(self._components.get_component("listbox_radio_selection"), True, False, 1)

        self._components.get_component("second_part").pack_start(self._components.get_component("more_interfaces_button"), True, False, 0)
        self._components.get_component("second_part").pack_start(self._components.get_component("scroll_wifi_window"), True, True, 1)
        self._components.get_component("second_part").pack_start(self._components.get_component("label_wifi_password"), True, False, 2)
        self._components.get_component("second_part").pack_start(self._components.get_component("entry_wifi_password"), True, False, 3)

        self._components.get_component("third_part").pack_start(self._components.get_component("label_ip_address"), True, False, 0)
        self._components.get_component("third_part").pack_start(self._components.get_component("entry_ip_address"), True, False, 1)
        self._components.get_component("third_part").pack_start(self._components.get_component("label_netmask_address"), True, False, 2)
        self._components.get_component("third_part").pack_start(self._components.get_component("entry_netmask_address"), True, False, 3)
        self._components.get_component("third_part").pack_start(self._components.get_component("label_gateway_address"), True, False, 4)
        self._components.get_component("third_part").pack_start(self._components.get_component("entry_gateway_address"), True, False, 5)
        self._components.get_component("third_part").pack_start(self._components.get_component("label_nameserver1"), True, False, 6)
        self._components.get_component("third_part").pack_start(self._components.get_component("entry_nameserver1"), True, False, 7)
        self._components.get_component("third_part").pack_start(self._components.get_component("label_nameserver2"), True, False, 8)
        self._components.get_component("third_part").pack_start(self._components.get_component("entry_nameserver2"), True, False, 9)
        
        self._components.get_component("general_grid").attach(self._components.get_component("first_part"), 1, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("second_part"), 2, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("third_part"), 3, 0, 1, 1)


    def entry_ip_address(self, data):
        self._config_general["network_page"]["current_interface_configuration"].ipAddress = data.get_text()

    def entry_netmask_address(self, data):
        self._config_general["network_page"]["current_interface_configuration"].netMaskAddress = data.get_text()

    def entry_gateway_address(self, data):
        self._config_general["network_page"]["current_interface_configuration"].gatewayAddress = data.get_text()

    def entry_nameserver1(self, data):
        self._config_general["network_page"]["current_interface_configuration"].nameServer1 = data.get_text()

    def entry_nameserver2(self, data):
        self._config_general["network_page"]["current_interface_configuration"].nameServer2 = data.get_text()

    def entry_wifi_password(self, data):
        self._config_general["network_page"]["wifi_password"] = data.get_text()


    def get_current_card(self):
        return self._config_general["network_page"]["current_interface_configuration"]

    def init_first_button_state(self):
        if self.get_current_card().networkIpAttributionType is NetworkIpAttributionType.DHCP:
            self._components.get_component("third_part").hide()
        else:
            self._components.get_component("third_part").show()

    def on_radio_button(self, button, btnType):
        self._config_general["network_page"]["current_interface_configuration"].networkIpAttributionType = NetworkIpAttributionType(btnType)
        self.init_first_button_state()
        self.enable_next_step()

    def add_radio_button(self, radio_id, active, label):
        if not self._components.get_component("listbox_radio_selection").get_children() or not self._components.get_component("listbox_radio_selection").get_children()[0]:
            current_button = NetworkAddressChooserRadioButton(radio_id, label, None)
        else:
            current_button = NetworkAddressChooserRadioButton(radio_id, label, self._components.get_component("listbox_radio_selection").get_children()[0].get_child())
        current_button.set_active(active)

        current_button.connect("toggled", self.on_radio_button, radio_id)
        self._components.get_component("listbox_radio_selection").add(current_button)

    def add_network_configuration_buttons(self, defaultValue):
        active1 = False
        active2 = False
        
        if defaultValue == 1:
            active1 = True
        elif defaultValue == 2:
            active2 = True
        
        self.add_radio_button(1, active1, self._language_manager.translate_msg("network_page", "network_configuration_choice_1"))
        self.add_radio_button(2, active2, self._language_manager.translate_msg("network_page", "network_configuration_choice_2"))
        self._config_general["network_page"]["current_interface_configuration"].networkIpAttributionType = NetworkIpAttributionType(defaultValue)
        self.init_first_button_state()

    def load_wifi_list(self, netinterfaceName, wifi):
        if wifi is False:
            self._components.get_component("scroll_wifi_window").hide()
            self._config_general["network_page"]["wifi_password"] = None
            return

        listbox = self._components.get_component("listbox_wifi_window").get_children()
        for current in listbox:
            self._components.get_component("listbox_wifi_window").remove(current)

        wifiService = WifiService(netinterfaceName)
        wifiList = wifiService.get_list_wifi()
        for current in wifiList:
            self._components.get_component("listbox_wifi_window").add(WifiCardLabel(current))
        self._components.get_component("listbox_wifi_window").add(self._components.get_component("more_wifi_button"))
        self.set_selected_wifi_row()
        self._components.get_component("scroll_wifi_window").show()

    def on_row_select_wifi(self, list_box, current_row_clicked=None):
        if not list_box or current_row_clicked is None:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
            return

        row_elem = current_row_clicked.get_child()
        if row_elem != self._components.get_component("more_wifi_button"):
            self._config_general["network_page"]["wifi_cell"] = row_elem.cell
            self.enable_next_step()
            return

        self._components.get_component("scroll_wifi_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("scroll_wifi_window").set_vexpand(True)
        self._components.get_component("scroll_wifi_window").set_valign(Gtk.Align.FILL)
        self._components.get_component("more_wifi_button").get_parent().hide()
        self.set_selected_wifi_row()
        self.enable_next_step()
        

    def set_selected_wifi_row(self):
        check_not_empty = self._components.get_component("listbox_wifi_window").get_children()
        if not check_not_empty:
            return

        for current in self._components.get_component("listbox_wifi_window").get_children():
            label = current.get_child()
            if label is self._components.get_component("more_wifi_button"):
                break
            if "wifi_cell" in self._config_general["network_page"] \
            and self._config_general["network_page"]["wifi_cell"] != None\
            and label.cell.ssid == self._config_general["network_page"]["wifi_cell"].ssid:
                self._components.get_component("listbox_wifi_window").select_row(current)
                return
        self._components.get_component("listbox_wifi_window").select_row(check_not_empty[0])




    def on_row_select_interface(self, list_box, current_row_clicked=None):
        if not list_box:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
            return

        row_elem = current_row_clicked.get_child()
        if row_elem != self._components.get_component("more_interfaces_button"):
            for item in self._components.get_component("listbox_radio_selection").get_children():
                self._components.get_component("listbox_radio_selection").remove(item)        
            self._config_general["network_page"]["current_interface_configuration"] = row_elem.networkConfiguration
            self.add_network_configuration_buttons(row_elem.networkConfiguration.networkIpAttributionType.value)
            if self.get_current_card().networkIpAttributionType is NetworkIpAttributionType.MANUAL:
                self._components.get_component("entry_ip_address").set_text(self.get_current_card().ipAddress)
                self._components.get_component("entry_netmask_address").set_text(self.get_current_card().netMaskAddress)
                # self._components.get_component("entry_gateway_address").set_text(self.get_current_card().gatewayAddress)
                self._components.get_component("entry_nameserver1").set_text("1.1.1.1")
                self._components.get_component("entry_nameserver2").set_text("1.0.0.1")
            if self.get_current_card().networkType is NetworkType.WIFI:
                self.load_wifi_list(self.get_current_card().nameInterface, True)
            else:
                self.load_wifi_list(self.get_current_card().nameInterface, False)
            return

        self._components.get_component("scroll_interfaces_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("scroll_interfaces_window").set_vexpand(True)
        self._components.get_component("scroll_interfaces_window").set_valign(Gtk.Align.FILL)
        self._components.get_component("more_interfaces_button").get_parent().hide()
        self.set_selected_card_row()
        self.enable_next_step()
        
    def set_selected_card_row(self):
        check_not_empty = self._components.get_component("listbox_interfaces_window").get_children()
        if not check_not_empty:
            return

        for current in self._components.get_component("listbox_interfaces_window").get_children():
            label = current.get_child()
            if label is self._components.get_component("more_interfaces_button"):
                break
            if "current_interface_configuration" in self._config_general["network_page"] \
            and self._config_general["network_page"]["current_interface_configuration"] != None\
            and label.networkConfiguration.nameInterface == self._config_general["network_page"]["current_interface_configuration"].nameInterface:
                self._components.get_component("listbox_interfaces_window").select_row(current)
                return
        self._components.get_component("listbox_interfaces_window").select_row(check_not_empty[0])

    def long_task(self):
        Gdk.threads_enter()
        self._network_interfaces_service = NetworkInterfaces()
        
        interfaces = self._network_interfaces_service.get_all_cards()
        interfaces.sort(key=lambda sort: sort.nameInterface.lower())
       
        for item in interfaces:
            self._components.get_component("listbox_interfaces_window").add(NetworkCardLabel(item))
        self._components.get_component("listbox_interfaces_window").add(self._components.get_component("more_interfaces_button"))
        Gdk.threads_leave()

    def load_win(self, win):
        self._win_parent = win

    def enable_next_step(self):
        if 'current_disk' in self._config_general['network_page'] and self._config_general['network_page']['current_disk'] != None and 'partition_type' in self._config_general['network_page'] and self._config_general['network_page']['partition_type'] != None:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        else:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)

    def load_page(self):
        self.set_selected_card_row()
        # self.enable_next_step()

    def refresh_ui_language(self):        
        self._components.get_component("label_ip_address").set_text(self._language_manager.translate_msg("network_page", "network_ip_address"))
        self._components.get_component("label_netmask_address").set_text(self._language_manager.translate_msg("network_page", "network_netmask_address"))
        self._components.get_component("label_gateway_address").set_text(self._language_manager.translate_msg("network_page", "network_gateway_address"))
        self._components.get_component("label_nameserver1").set_text(self._language_manager.translate_msg("network_page", "network_nameserver1_address"))
        self._components.get_component("label_nameserver2").set_text(self._language_manager.translate_msg("network_page", "network_nameserver2_address"))

        for current_row in self._components.get_component("listbox_radio_selection").get_children():
            radio_button = current_row.get_child()
            new_label = self._language_manager.translate_msg("network_page", "network_configuration_choice_" + str(radio_button.buttonid))
            radio_button.text = new_label
            radio_button.set_label(new_label)

    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("network_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("network_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["network"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["network"]["icon"]