import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from egg.filesystem import Filesystem
from ui.gtk.pages.partition.add_partition_window import AddPartitionWindow
from ui.gtk.pages.partition.edit_partition_window import ResizeMovePartitionWindow


class PartitionToolbar(Gtk.Toolbar):
    parent_win = None
    resize_move_partition_window = None
    add_partition_window = None

    add_new_partition_button = None
    resize_move_partition_button = None
    delete_partition_button = None

    def __init__(self, parent_win, language_manager, config_general):
        Gtk.Toolbar.__init__(self)
        self.parent_win = parent_win
        self.resize_move_partition_window = ResizeMovePartitionWindow(self.parent_win, language_manager, config_general)
        self.add_partition_window = AddPartitionWindow(self.parent_win, language_manager, config_general)

        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        self.add_new_partition_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        self.add_new_partition_button.connect('clicked', self.add_new_partition)
        self.add_new_partition_button.show()

        self.resize_move_partition_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_EDIT)
        self.resize_move_partition_button.connect('clicked', self.resize_move_partition)
        self.resize_move_partition_button.show()

        self.delete_partition_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_DELETE)
        self.delete_partition_button.connect('clicked', self.delete_partition)
        self.delete_partition_button.show()

        reset_default_partition_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CANCEL)
        reset_default_partition_button.connect('clicked', self.reset_default_partition)
        reset_default_partition_button.show()

        self.insert(self.add_new_partition_button, 0)
        self.insert(self.resize_move_partition_button, 1)
        self.insert(self.delete_partition_button, 2)
        self.insert(reset_default_partition_button, 3)

    def add_new_partition(self, win):
        current_partition = self.parent_win.get_selected_partition()
        self.add_partition_window.show_window(current_partition)

    def resize_move_partition(self, win):
        before_partition_size = 0
        after_partition_size = 0
        current_partition = self.parent_win.get_selected_partition()
        current_previous_partition = self.parent_win.get_selected_previous_partition()
        current_next_partition = self.parent_win.get_selected_next_partition()
        
        if current_previous_partition != None and current_previous_partition.filesystem == Filesystem.NOT_ALLOCATED:
            before_partition_size = current_previous_partition.size
        if current_next_partition != None and current_next_partition.filesystem == Filesystem.NOT_ALLOCATED:
            after_partition_size = current_next_partition.size
        self.resize_move_partition_window.show_window(current_partition, before_partition_size, after_partition_size)

    def delete_partition(self, win):
        current_partition = self.parent_win.get_selected_partition()
        self.parent_win.delete_partition(current_partition)

    def reset_default_partition(self, win):
        # Or raven default
        self.parent_win.add_current_partitions()

    def nothing_selected(self):
        self.add_new_partition_button.set_sensitive(False)
        self.resize_move_partition_button.set_sensitive(False)
        self.delete_partition_button.set_sensitive(False)

    def valid_partition(self):
        self.add_new_partition_button.set_sensitive(False)
        self.resize_move_partition_button.set_sensitive(True)
        self.delete_partition_button.set_sensitive(True)

    def free_space_partition(self):
        self.add_new_partition_button.set_sensitive(True)
        self.resize_move_partition_button.set_sensitive(False)
        self.delete_partition_button.set_sensitive(False)
