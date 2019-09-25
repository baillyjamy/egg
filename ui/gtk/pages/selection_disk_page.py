from ui.gtk.main_window_button import MainWindowButton
from ui.gtk.pages.page import Page
from egg.disk_management.diskservice import DiskService
from gi.repository import Gtk, Gdk
from egg.size_calculator import SizeCalculator

class DiskLabel(Gtk.Label):
    model = None
    size = None
    path = None

    def __init__(self, model, size, path):
        Gtk.Label.__init__(self)
        self.model = model
        self.size = size
        self.path = path

        size_human, unit_human = SizeCalculator.get_human_size(self.size)
        
        self.size_human_mode = size_human + " " + unit_human
        self.set_property("margin", 8)
        self.set_halign(Gtk.Align.START)
        self.set_text(self.path + " " + self.size_human_mode + " " + self.model + " (" + str(self.size) + " octets)")
        self.show()

    def get_disk_name(self):
        return self.path + " " + self.size_human_mode + " " + self.model + " (" + str(self.size) + " octets)"

class DiskActionChooserRadioButton(Gtk.RadioButton):
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
        self._components["general_box"] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components["general_grid"] = Gtk.Grid()
        self._components["scroll_disk_window"] = Gtk.ScrolledWindow(None, None)
        self._components["listbox_disk_window"] = Gtk.ListBox()

        self._components["listbox_radio_selection"] = Gtk.ListBox()
        self._components["more_disk_button"] = Gtk.Image.new_from_icon_name("view-more-symbolic",
                                                        Gtk.IconSize.MENU)

    def get_component(self, component_name):
        return self._components[component_name]

class SelectionDiskPage(Page):
    _disk = None
    _components = None
    _win_parent = None

    def __init__(self, language_manager, config_general):
        super(SelectionDiskPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._disk = DiskService()
        self._config_general["selection_disk_page"] = {}
        self._config_general["selection_disk_page"]["current_disk"] = None
        self._config_general['selection_disk_page']['partition_type'] = None
        self._components = Components()
        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        # General grid
        self._components.get_component("general_box").pack_start(self._components.get_component("general_grid"), True, True, 1)
                
        self._components.get_component("general_grid").set_margin_start(10)
        self._components.get_component("general_grid").set_margin_end(10)
        self._components.get_component("general_grid").set_margin_top(10)
        self._components.get_component("general_grid").set_margin_bottom(10)
        self._components.get_component("general_grid").set_row_spacing(30)

        # Language box
        self._components.get_component("listbox_disk_window").set_size_request(60, -1)
        self._components.get_component("listbox_disk_window").connect_after("row-selected", self.on_row_select_disk)
        self._components.get_component("more_disk_button").show_all()

        self._components.get_component("scroll_disk_window").set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self._components.get_component("scroll_disk_window").add(self._components.get_component("listbox_disk_window"))
        self._components.get_component("scroll_disk_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

        # Box
        self._components.get_component("listbox_radio_selection").set_size_request(60, -1)
        self._components.get_component("listbox_radio_selection").set_selection_mode(Gtk.SelectionMode.NONE)

        # Attach general grid
        self._components.get_component("general_grid").attach(self._components.get_component("scroll_disk_window"), 0, 0, 1, 1)
        self._components.get_component("general_grid").attach(self._components.get_component("listbox_radio_selection"), 0, 1, 1, 1)


    def on_radio_button(self, button, partition_type):
        self._config_general["selection_disk_page"]["partition_type"] = partition_type
        self.enable_next_step()

    def add_radio_button(self, radio_id, label):
        if not self._components.get_component("listbox_radio_selection").get_children() or not self._components.get_component("listbox_radio_selection").get_children()[0]:
            current_button = DiskActionChooserRadioButton(radio_id, label, None)
        else:
            current_button = DiskActionChooserRadioButton(radio_id, label, self._components.get_component("listbox_radio_selection").get_children()[0].get_child())

        current_button.connect("toggled", self.on_radio_button, radio_id)
        self._components.get_component("listbox_radio_selection").add(current_button)

    def add_button_test(self):
        self.add_radio_button(1, self._language_manager.translate_msg("selection_disk_page", "disk_usage_choice_1"))
        self.add_radio_button(2, self._language_manager.translate_msg("selection_disk_page", "disk_usage_choice_2"))
        self._config_general["selection_disk_page"]["partition_type"] = 1

    def on_row_select_disk(self, list_box_disk, current_row_disk_clicked=None):
        if not list_box_disk:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)
            return

        row_elem = current_row_disk_clicked.get_child()
        if row_elem != self._components.get_component("more_disk_button"):
            for item in self._components.get_component("listbox_radio_selection").get_children():
                self._components.get_component("listbox_radio_selection").remove(item)
        
            self.add_button_test()
            self._config_general["selection_disk_page"]["current_disk"] = row_elem
            self.enable_next_step()
            return

        # load more disk
        self._components.get_component("scroll_disk_window").set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component("scroll_disk_window").set_vexpand(True)
        self._components.get_component("scroll_disk_window").set_valign(Gtk.Align.FILL)
        self._components.get_component("more_disk_button").get_parent().hide()
        self.set_selected_language_row()
        self.enable_next_step()

    def set_selected_language_row(self):
        check_not_empty = self._components.get_component("listbox_disk_window").get_children()
        if not check_not_empty:
            return

        for current in self._components.get_component("listbox_disk_window").get_children():
            label = current.get_child()
            if label == self._components.get_component("more_disk_button"):
                continue
            if "current_disk" in self._config_general["selection_disk_page"] \
            and self._config_general["selection_disk_page"]["current_disk"] != None\
            and label.model == self._config_general["selection_disk_page"]["current_disk"].model:
                self._components.get_component("listbox_disk_window").select_row(current)
                return
        self._components.get_component("listbox_disk_window").select_row(check_not_empty[0])

    # def load_checkbox_button_action:
    #     take the all disk and can erase
    #     configure by yourself

    def long_task(self):
        Gdk.threads_enter()
        disks = self._disk.get_disk_list()

        # take only 5 one or will have problem with the window
        disk_label = list()
        for item in disks:
            disk_label.append(DiskLabel(str(item.model), item.capacity, str(item.path)))
        
        disk_label.sort(key=lambda sort: sort.model.lower())
        for current in disk_label:
            self._components.get_component("listbox_disk_window").add(current)

        self._components.get_component("listbox_disk_window").add(self._components.get_component("more_disk_button"))
        self.add_button_test()
        Gdk.threads_leave()

    def load_win(self, win):
        self._win_parent = win

    def enable_next_step(self):
        if 'current_disk' in self._config_general['selection_disk_page'] and self._config_general['selection_disk_page']['current_disk'] != None and 'partition_type' in self._config_general['selection_disk_page'] and self._config_general['selection_disk_page']['partition_type'] != None:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        else:
            self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, False)

    def load_page(self):
        self.set_selected_language_row()
        self.enable_next_step()

    def refresh_ui_language(self):
        for current_row in self._components.get_component("listbox_radio_selection").get_children():
            radio_button = current_row.get_child()
            new_label = self._language_manager.translate_msg("selection_disk_page", "disk_usage_choice_" + str(radio_button.buttonid))
            radio_button.text = new_label
            radio_button.set_label(new_label)

    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg("selection_disk_page", "title")

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg("selection_disk_page", "sidebar_title")

    #page id
    def get_page_id(self):
        return self._config_general["config_page"]["selection_disk"]["id"]
   
    #icon
    def get_page_icon(self):
        return self._config_general["config_page"]["selection_disk"]["icon"]