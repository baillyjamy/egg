from ui.gtk.main_window_button import MainWindowButton
from egg.disk_management.diskservice import DiskService
from egg.disk_management.diskservice import DiskService
from ui.gtk.pages.page import Page
from gi.repository import Gtk, Gdk
from egg.size_calculator import SizeCalculator
from egg.filesystem import Filesystem
from egg.partition.partition_parameter import PartitionParameter
from ui.gtk.pages.partition.partition_toolbar import PartitionToolbar
from ui.gtk.pages.partition.column_row_partition_treeview import ColumnRowPartitionTreeview
from egg.size_calculator import SizeCalculator
import egg.disk_management.partition

class Components():
    _components = {}

    def __init__(self, win, partition_page, language_manager, config_general):
        self._components['general_box'] = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._components['general_grid'] = Gtk.Grid()
        self._components['partition_treeview'] = ColumnRowPartitionTreeview(config_general)
        self._components['partition_treeview_scroll'] = Gtk.ScrolledWindow()
        self._components['partition_toolbar'] = PartitionToolbar(partition_page, language_manager, config_general) #language_manager
        self._components['separator'] = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)


    def get_component(self, component_name):
        return self._components[component_name]

class PartitionDiskPage(Page):
    _disk = None
    _components = None
    _win_parent = None
    _disk_selection_update = None
    _last_partition_type = None

    def __init__(self, language_manager, config_general):
        super(PartitionDiskPage, self).__init__()
        self._language_manager = language_manager
        self._config_general = config_general
        self._disk = DiskService()
        self._config_general['partition_disk'] = {}
        self._config_general['partition_disk']['partitions'] = None
        self._components = Components(self._win_parent, self, self._language_manager, self._config_general)
        self.init_components()
        self.refresh_ui_language()

    def init_components(self):
        # General grid
        self._components.get_component('general_box').pack_start(self._components.get_component('general_grid'), True, True, 1)

        self._components.get_component('general_grid').set_margin_start(10)
        self._components.get_component('general_grid').set_margin_end(10)
        self._components.get_component('general_grid').set_margin_top(10)
        self._components.get_component('general_grid').set_margin_bottom(10)

        self._components.get_component('partition_treeview').get_selection().connect('changed', self.on_selection_changed)

        # Treeview scrollview
        self._components.get_component('partition_treeview_scroll').set_min_content_height(200)
        self._components.get_component('partition_treeview_scroll').set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._components.get_component('partition_treeview_scroll').add(self._components.get_component('partition_treeview'))
        self._components.get_component('partition_treeview_scroll').set_hexpand(True)
        self._components.get_component('partition_treeview_scroll').set_vexpand(True)

        # Attach general grid
        self._components.get_component('general_grid').attach(self._components.get_component('partition_toolbar'), 0, 0, 1, 1)
        self._components.get_component('general_grid').attach(self._components.get_component('separator'), 0, 1, 1, 1)
        self._components.get_component('general_grid').attach(self._components.get_component('partition_treeview_scroll'), 0, 2, 1, 1)

    def new_partition(self, partition, free_before, free_after):
        current_idx = self._components.get_component('partition_treeview').get_current_selected_idx_row()
        current_iter = self._components.get_component('partition_treeview').get_current_selected_iter_row()
        self._components.get_component('partition_treeview').update_partition_row(partition, current_idx)

        if free_before > 0:
            free_partition = PartitionParameter()
            free_partition.set_size(free_before)
            free_partition.change_partition_to_unallocated(self._language_manager.translate_msg('partition_disk_page', 'notallocated'))
            self._components.get_component('partition_treeview').add_new_partition_row_before_idx(free_partition, current_iter, current_idx)
            current_idx += 1

        if free_after > 0:
            free_partition = PartitionParameter()
            free_partition.set_size(free_after)
            free_partition.change_partition_to_unallocated(self._language_manager.translate_msg('partition_disk_page', 'notallocated'))
            self._components.get_component('partition_treeview').add_new_partition_row_after_idx(free_partition, current_iter, current_idx)

        self._components.get_component('partition_toolbar').valid_partition()

    def resize_move_partition(self, partition, free_before, free_after):
        current_idx = self._components.get_component('partition_treeview').get_current_selected_idx_row()
        current_iter = self._components.get_component('partition_treeview').get_current_selected_iter_row()
        self._components.get_component('partition_treeview').update_partition_row(partition, current_idx)

        current_previous_partition = self.get_selected_previous_partition()
        current_next_partition = self.get_selected_next_partition()

        if free_before > 0:
            if current_previous_partition != None and current_previous_partition.filesystem == Filesystem.NOT_ALLOCATED:
                current_previous_partition.size = free_before
                self._components.get_component('partition_treeview').update_partition_row(current_previous_partition, current_idx - 1)
            else:
                free_partition = PartitionParameter()
                free_partition.set_size(free_before)
                free_partition.change_partition_to_unallocated(self._language_manager.translate_msg('partition_disk_page', 'notallocated'))
                self._components.get_component('partition_treeview').add_new_partition_row_before_idx(free_partition, current_iter, current_idx)
                current_idx += 1
        elif current_previous_partition != None and current_previous_partition.filesystem == Filesystem.NOT_ALLOCATED:
            self._components.get_component('partition_treeview').delete_rows_by_row_list([current_previous_partition])
            current_idx -= 1

        if free_after > 0:
            if current_next_partition != None and current_next_partition.filesystem == Filesystem.NOT_ALLOCATED:
                current_next_partition.size = free_after
                self._components.get_component('partition_treeview').update_partition_row(current_next_partition, current_idx + 1)
            else:
                free_partition = PartitionParameter()
                free_partition.set_size(free_after)
                free_partition.change_partition_to_unallocated(self._language_manager.translate_msg('partition_disk_page', 'notallocated'))
                self._components.get_component('partition_treeview').add_new_partition_row_after_idx(free_partition, current_iter, current_idx)
        elif current_next_partition != None and current_next_partition.filesystem == Filesystem.NOT_ALLOCATED:
            self._components.get_component('partition_treeview').delete_rows_by_row_list([current_next_partition])

        self._components.get_component('partition_toolbar').valid_partition()


    def delete_partition(self, current_partition, current_idx=None):
        previous_partition = None
        next_partition = None

        current_partition.change_partition_to_unallocated(self._language_manager.translate_msg('partition_disk_page', 'notallocated'))
        if current_idx is None:
            current_idx = self._components.get_component('partition_treeview').get_current_selected_idx_row()
        if current_idx - 1 >= 0 and self._components.get_component('partition_treeview').current_partition_row[
            current_idx - 1].filesystem == Filesystem.NOT_ALLOCATED:
            previous_partition = self._components.get_component('partition_treeview').current_partition_row[current_idx - 1]

        if current_idx + 1 < len(self._components.get_component('partition_treeview').current_partition_row) and self._components.get_component('partition_treeview').current_partition_row[
            current_idx + 1].filesystem == Filesystem.NOT_ALLOCATED:
            next_partition = self._components.get_component('partition_treeview').current_partition_row[current_idx + 1]

        if previous_partition is not None or next_partition is not None:
            totalsize = current_partition.size
            todelete = list()

            if previous_partition is not None:
                totalsize += previous_partition.size
                todelete.append(current_partition)
            if next_partition is not None:
                totalsize += next_partition.size
                todelete.append(next_partition)

            if previous_partition is not None:
                previous_partition.set_size(totalsize)
                self._components.get_component('partition_treeview').update_partition_row(previous_partition, current_idx - 1)
            else:
                current_partition.set_size(totalsize)
                self._components.get_component('partition_treeview').update_partition_row(current_partition, current_idx)
            self._components.get_component('partition_treeview').delete_rows_by_row_list(todelete)
            # change for select row
            self._components.get_component('partition_toolbar').nothing_selected()
            return

        self._components.get_component('partition_treeview').update_partition_row(current_partition, current_idx)
        self._components.get_component('partition_toolbar').free_space_partition()

    def on_selection_changed(self, selection):
        current_partition = self._components.get_component('partition_treeview').get_current_selected_row()
        if current_partition is not None and current_partition.filesystem == Filesystem.NOT_ALLOCATED:
            self._components.get_component('partition_toolbar').free_space_partition()
        elif current_partition is not None:
            self._components.get_component('partition_toolbar').valid_partition()

    def add_columns_titles(self):
        self._components.get_component('partition_treeview').delete_columns_titles()

        titles = [self._language_manager.translate_msg('partition_disk_page', 'column_1'), self._language_manager.translate_msg('partition_disk_page', 'column_2'),
        self._language_manager.translate_msg('partition_disk_page', 'column_3'), self._language_manager.translate_msg('partition_disk_page', 'column_4'),
        self._language_manager.translate_msg('partition_disk_page', 'column_5'), self._language_manager.translate_msg('partition_disk_page', 'column_6'),
        self._language_manager.translate_msg('partition_disk_page', 'column_7'), self._language_manager.translate_msg('partition_disk_page', 'column_8')]
        idx = 0
        for current in titles:
            self._components.get_component('partition_treeview').add_new_column_title(current, idx)
            idx += 1

    def change_column_name(self):
        titles = [self._language_manager.translate_msg('partition_disk_page', 'column_1'), self._language_manager.translate_msg('partition_disk_page', 'column_2'),
        self._language_manager.translate_msg('partition_disk_page', 'column_3'), self._language_manager.translate_msg('partition_disk_page', 'column_4'),
        self._language_manager.translate_msg('partition_disk_page', 'column_5'), self._language_manager.translate_msg('partition_disk_page', 'column_6'),
        self._language_manager.translate_msg('partition_disk_page', 'column_7'), self._language_manager.translate_msg('partition_disk_page', 'column_8')]
        self._components.get_component('partition_treeview').delete_columns_titles()

        idx = 0
        for current in titles:
            self._components.get_component('partition_treeview').add_new_column_title(current, idx)
            idx += 1

        current_idx = 0
        for current in self._components.get_component('partition_treeview').current_partition_row:
            if current.filesystem == Filesystem.NOT_ALLOCATED:
                current.name = self._language_manager.translate_msg('partition_disk_page', 'notallocated')
                self._components.get_component('partition_treeview').update_partition_row(current, current_idx)
            current_idx = current_idx + 1


    def get_selected_partition(self):
        return self._components.get_component('partition_treeview').get_current_selected_row()

    def get_selected_previous_partition(self):
        return self._components.get_component('partition_treeview').get_current_previous_selected_row()

    def get_selected_next_partition(self):
        return self._components.get_component('partition_treeview').get_current_next_selected_row()

    def get_selected_before_after_partition(self):
        return self._components.get_component('partition_treeview').get_current_selected_row()

    def add_current_partitions(self, force):
        new_partition_type = None
        if "partition_type" in self._config_general["selection_disk_page"] and \
            self._config_general["selection_disk_page"]["partition_type"] is not None:
            new_partition_type = self._config_general["selection_disk_page"]["partition_type"]
            
        if force is True \
            or self._last_partition_type is not new_partition_type \
            or self._last_partition_type is None \
            or self._disk_selection_update is None \
            or self._config_general["selection_disk_page"]["current_disk_service"] is not self._disk_selection_update \
            or self._components.get_component('partition_treeview').current_partition_row is None \
            or len(self._components.get_component('partition_treeview').current_partition_row) == 0:

            self._disk_selection_update = self._config_general["selection_disk_page"]["current_disk_service"]
            self._components.get_component('partition_treeview').delete_rows()
            for current in self._disk_selection_update.partitions:
                current_partition_parameter = PartitionParameter()
                current_partition_parameter.load_partition(current)
                self._components.get_component('partition_treeview').add_new_partition_row(current_partition_parameter)
            self._components.get_component('partition_toolbar').nothing_selected()

            if "partition_type" in self._config_general["selection_disk_page"] and \
                self._config_general["selection_disk_page"]["partition_type"] is not None:
                self._last_partition_type = self._config_general["selection_disk_page"]["partition_type"]

    def add_current_partitions_with_raven(self, force):
        new_partition_type = None
        if "partition_type" in self._config_general["selection_disk_page"] and \
            self._config_general["selection_disk_page"]["partition_type"] is not None:
            new_partition_type = self._config_general["selection_disk_page"]["partition_type"]

        if force is True \
            or self._last_partition_type is not new_partition_type \
            or self._last_partition_type is None \
            or self._disk_selection_update is None \
            or self._components.get_component('partition_treeview').current_partition_row is None \
            or self._config_general["selection_disk_page"]["current_disk_service"] is not self._disk_selection_update \
            or len(self._components.get_component('partition_treeview').current_partition_row) == 0:

            self._disk_selection_update = self._config_general["selection_disk_page"]["current_disk_service"]

            # disk_mo_capicity = SizeCalculator.get_mo_size(self._disk_selection_update.capacity) - (1024 + 560 + 2048)
            disk_mo_capicity = SizeCalculator.get_mo_size(self._disk_selection_update.capacity) - (1024 + 2048)
            # PartitionParameter("Raven Installation Partition", "EFI partition", Filesystem.FAT32, "/boot/efi", "RAVEN-OS PARTITION", 560, 0, 560),
            partitions = [ PartitionParameter("Raven Installation Partition", "Boot partition", Filesystem.EXT4, "/boot", "RAVEN-OS PARTITION", 1024, 0, 1024),
                PartitionParameter("Raven Installation Partition", "SWAP partition", Filesystem.SWAP, "", "RAVEN-OS PARTITION", 2048, 0, 2048),
                PartitionParameter("Raven Installation Partition", "Root partition", Filesystem.EXT4, "/", "RAVEN-OS PARTITION", disk_mo_capicity, 0, disk_mo_capicity)]
            self._components.get_component('partition_treeview').delete_rows()
            for current in partitions:
                filesystem = egg.disk_management.Partition.Filesystem[str(current.filesystem.name)]
                partition_type = egg.disk_management.Partition.Type.PARTITION_NORMAL
                self._config_general["selection_disk_page"]["current_disk_service"].add_partition(filesystem, partition_type, current.size, "MB")
                self._components.get_component('partition_treeview').add_new_partition_row(current)
            self._components.get_component('partition_toolbar').nothing_selected()

            self._last_partition_type = new_partition_type

    def window_status(self, status):
        self._win_parent._component.get_component('main_window').set_sensitive(status)

    def long_task(self):
        Gdk.threads_enter()
        self.add_columns_titles()
        Gdk.threads_leave()

    def load_win(self, win):
        self._win_parent = win

    def load_page(self):
        # configcheck
        # if "current_disk" in self._config_general["partition_disk"] and self._config_general["partition_disk"]["current_disk"] != None and "partition_type" in self._config_general["partition_disk"] and self._config_general["partition_disk"]["partition_type"] != None:
                
        if "partition_type" in self._config_general["selection_disk_page"] and \
            self._config_general["selection_disk_page"]["partition_type"] is not None \
            and self._config_general["selection_disk_page"]["partition_type"] == 2:
            self.add_current_partitions(False)
        else:
            self.add_current_partitions_with_raven(False)
        self._win_parent.set_button_action_visibility(MainWindowButton.NEXT, True)
        # else:
        #     self._win_parent.set_can_next(False)

    def refresh_ui_language(self):
        self.change_column_name()

    #page title
    def get_page_title(self):
        return self._language_manager.translate_msg('partition_disk_page', 'title')

    #page sidebar title
    def get_page_sidebar_title(self):
        return self._language_manager.translate_msg('partition_disk_page', 'sidebar_title')

    #page id
    def get_page_id(self):
        return self._config_general['config_page']['partition_disk']['id']

    #icon
    def get_page_icon(self):
        return self._config_general['config_page']['partition_disk']['icon']



