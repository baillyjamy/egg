import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from egg.filesystem import Filesystem
from egg.partition.partition_parameter import PartitionParameter

class AddPartitionWindow(Gtk.Window):
    win_parent = None
    builder = None
    _language_manager = None
    _config_manager = None
    
    name = None
    mount_point = None
    label = None

    on_partition_value_changed_callback = None
    on_before_free_value_changed_callback = None
    on_after_free_value_changed_callback = None

    def __init__(self, win_parent, language_manager, config_general):  # send win parent for disable or
        self.win_parent = win_parent
        self._language_manager = language_manager
        self._config_manager = config_general


        self.builder = Gtk.Builder()
        self.builder.add_from_file(config_general['config_page']['partition_disk']['add_glade_file'])
        self.builder.connect_signals(
            {
                'onDestroy': (self.close),
                'onButtonCancel': (self.cancel),
                'onApply': (self.apply)
            })

    def show_window(self, current_partition): #add prev and next
        self.current_partition = current_partition
        self.builder.get_object('add_partition_window').set_title(self._language_manager.translate_msg('new_partition_page', 'title'))
        self.win_parent.window_status(False)

        self.builder.get_object('add_win_minimum_size_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'minimum_size') + ' ' + str(1) + ' Mio')
        self.builder.get_object('add_win_maximum_size_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'maximum_size') + ' ' + current_partition.size_str)
        self.builder.get_object('add_win_partition_size_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'partition_size'))
        self.builder.get_object('add_win_free_size_before_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'before_partition_size'))
        self.builder.get_object('add_win_free_size_after_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'after_partition_size'))
        self.builder.get_object('add_win_filesystem_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'filesytem'))
        self.builder.get_object('add_win_mount_point_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'mountpoint'))
        self.builder.get_object('add_win_name_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'partition_name'))
        self.builder.get_object('add_win_label_partition_label').set_text(
            self._language_manager.translate_msg('new_partition_page', 'label'))
        self.builder.get_object('add_win_cancel_btn').set_label(
            self._language_manager.translate_msg('new_partition_page', 'cancel'))
        self.builder.get_object('add_win_resize_btn').set_label(
            self._language_manager.translate_msg('new_partition_page', 'add'))
        

        incrementation = 1
        adj_size = Gtk.Adjustment(current_partition.size, 1, current_partition.size + 1, incrementation, 1, 1)
        self.builder.get_object('add_win_partition_size_entry_spinner').configure(adj_size, 1, 0)
        adj_before_size = Gtk.Adjustment(0, 0, current_partition.size, incrementation, 1, 1)
        self.builder.get_object('add_win_free_size_before_partition_entry_spinner').configure(adj_before_size, 1, 0)
        adj_after_size = Gtk.Adjustment(0, 0, current_partition.size, incrementation, 1, 1)
        self.builder.get_object('add_win_free_size_after_partition_entry_spinner').configure(adj_after_size, 1, 0)


        self.partition_value = current_partition.size
        self.partition_before_value = 0
        self.partition_after_value = 0


        self.set_value_by_code(self.builder.get_object('add_win_partition_size_entry_spinner'), current_partition.size, self.on_partition_value_changed_callback)
        self.set_value_by_code(self.builder.get_object('add_win_free_size_before_partition_entry_spinner'), 0, self.on_before_free_value_changed_callback)
        self.set_value_by_code(self.builder.get_object('add_win_free_size_after_partition_entry_spinner'), 0, self.on_after_free_value_changed_callback)

        if self.on_partition_value_changed_callback is None:
            self.on_partition_value_changed_callback = self.on_partition_value_changed
            self.on_before_free_value_changed_callback = self.on_before_free_value_changed
            self.on_after_free_value_changed_callback = self.on_after_free_value_changed

            self.builder.get_object('add_win_partition_size_entry_spinner').connect('value-changed', self.on_partition_value_changed_callback)
            self.builder.get_object('add_win_free_size_before_partition_entry_spinner').connect('value-changed', self.on_before_free_value_changed_callback)
            self.builder.get_object('add_win_free_size_after_partition_entry_spinner').connect('value-changed', self.on_after_free_value_changed_callback)

                
        filesystemlen = len(Filesystem)
        i = 0
        for current in Filesystem:
            if (i < filesystemlen - 2):
                self.builder.get_object('add_win_filesystem_partition_combobox').append_text(str(current.name))
            else:
                break
            i += 1
        self.builder.get_object('add_win_filesystem_partition_combobox').set_active(0)

        self.builder.get_object('add_partition_window').show_all()

    def hide_window(self):
        self.win_parent.window_status(True)
        self.builder.get_object('add_partition_window').hide()

    def apply(self, *args):
        self.current_partition.filesystem = Filesystem[self.builder.get_object('add_win_filesystem_partition_combobox').get_active_text()]
        self.current_partition.set_size(self.partition_value)
        self.current_partition.set_used_size(0)
        self.current_partition.set_free_size(self.partition_value)

        self.current_partition.partition_name = "Raven Installation Partition"
        self.current_partition.name = self.builder.get_object('add_win_name_partition_entry').get_text()
        self.current_partition.mount_point = self.builder.get_object('add_win_mount_point_partition_entry').get_text()
        self.current_partition.label = self.builder.get_object('add_win_label_partition_entry').get_text()

        self.win_parent.new_partition(self.current_partition, self.partition_before_value, self.partition_after_value)
        self.hide_window()

    def cancel(self, *args):
        self.hide_window()

    def close(self, *args):
        self.win_parent.window_status(True)

    def set_value_by_code(self, button, value, callback):
        if callback is not None:
            button.handler_block_by_func(callback)
        button.set_value(value)
        if callback is not None:
            button.handler_unblock_by_func(callback)

    def on_partition_value_changed(self, event):
        new_value = self.builder.get_object('add_win_partition_size_entry_spinner').get_value_as_int()
        difference = 0

        if new_value > self.partition_value: # button +
            difference = new_value - self.partition_value
            difference_after = self.partition_after_value - difference
            
            if difference_after < 0:
                to_positive = difference_after * -1
                if self.partition_after_value - (difference - to_positive) >= 0:
                    difference_after = self.partition_after_value - (difference - to_positive)
                else:
                    difference_after = self.partition_after_value
                if self.partition_before_value - to_positive >= 0:
                    difference_before = self.partition_before_value - to_positive
                else:
                    difference_before = self.partition_before_value
            else:
                difference_before = self.partition_before_value
            
            if self.partition_before_value != difference_before:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_before_partition_entry_spinner'), difference_before, self.on_before_free_value_changed_callback)
                self.partition_before_value = difference_before
            
            if self.partition_after_value != difference_after:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_after_partition_entry_spinner'), difference_after, self.on_after_free_value_changed_callback)
                self.partition_after_value = difference_after

        elif new_value < self.partition_value: # button -
            difference = self.partition_value - new_value
            after_value = self.builder.get_object('add_win_free_size_after_partition_entry_spinner').get_value_as_int()

            if self.partition_after_value != after_value + difference:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_after_partition_entry_spinner'), after_value + difference, self.on_after_free_value_changed_callback)
                self.partition_after_value = after_value + difference
            
        self.partition_value = self.builder.get_object('add_win_partition_size_entry_spinner').get_value_as_int()


    def on_after_free_value_changed(self, event):
        new_value = self.builder.get_object('add_win_free_size_after_partition_entry_spinner').get_value_as_int()
        difference = 0

        if new_value > self.partition_after_value: # button +
            difference = new_value - self.partition_after_value
            difference_before = self.partition_before_value - difference
            
            if difference_before < 0:
                to_positive = difference_before * -1
                difference_before = self.partition_before_value - (difference - to_positive)
                difference_partition = self.partition_value - to_positive
            else:
                difference_partition = self.partition_value

            if self.partition_value != difference_partition:
                self.set_value_by_code(self.builder.get_object('add_win_partition_size_entry_spinner'), difference_partition, self.on_partition_value_changed_callback)
                self.partition_value = difference_partition

            if self.partition_before_value != difference_before:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_before_partition_entry_spinner'), difference_before, self.on_before_free_value_changed_callback)
                self.partition_before_value = difference_before

        elif new_value < self.partition_after_value: # button -
            difference = self.partition_after_value - new_value            
            before_value = self.builder.get_object('add_win_free_size_before_partition_entry_spinner').get_value_as_int()
            
            if self.partition_before_value != before_value + difference:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_before_partition_entry_spinner'), before_value + difference, self.on_before_free_value_changed_callback)
                self.partition_before_value = before_value + difference
            
        self.partition_after_value = self.builder.get_object('add_win_free_size_after_partition_entry_spinner').get_value_as_int()


    def on_before_free_value_changed(self, event):
        new_value = self.builder.get_object('add_win_free_size_before_partition_entry_spinner').get_value_as_int()
        difference = 0

        if new_value > self.partition_before_value: # button +
            difference = new_value - self.partition_before_value
            difference_after = self.partition_after_value - difference
            
            if difference_after < 0:
                to_positive = difference_after * -1
                difference_after = self.partition_after_value - (difference - to_positive)
                difference_partition = self.partition_value - to_positive
            else:
                difference_partition = self.partition_value
            
            if self.partition_value != difference_partition:
                self.set_value_by_code(self.builder.get_object('add_win_partition_size_entry_spinner'), difference_partition, self.on_partition_value_changed_callback)
                self.partition_value = difference_partition
            
            if self.partition_after_value != difference_after:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_after_partition_entry_spinner'), difference_after, self.on_after_free_value_changed_callback)
                self.partition_after_value = difference_after

        elif new_value < self.partition_before_value: # button -
            difference = self.partition_before_value - new_value
            after_value = self.builder.get_object('add_win_free_size_after_partition_entry_spinner').get_value_as_int()
            
            if self.partition_after_value != after_value + difference:
                self.set_value_by_code(self.builder.get_object('add_win_free_size_after_partition_entry_spinner'), after_value + difference, self.on_after_free_value_changed_callback)
                self.partition_after_value = after_value + difference

        self.partition_before_value = self.builder.get_object('add_win_free_size_before_partition_entry_spinner').get_value_as_int()
