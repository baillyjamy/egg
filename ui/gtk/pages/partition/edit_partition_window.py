import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from egg.filesystem import Filesystem


class ResizeMovePartitionWindow(Gtk.Window):
    win_parent = None
    builder = None
    current_partition = None
    _language_manager = None
    _config_manager = None

    on_partition_value_changed_callback = None
    on_before_free_value_changed_callback = None
    on_after_free_value_changed_callback = None

    def __init__(self, win_parent, language_manager, config_general):
        self.win_parent = win_parent
        self._language_manager = language_manager
        self._config_manager = config_general

        self.builder = Gtk.Builder()
        self.builder.add_from_file(config_general['config_page']['partition_disk']['resize_glade_file'])
        self.builder.connect_signals(
            {
                'onDestroy': (self.close),
                'onButtonCancel': (self.cancel),
                'onApply': (self.apply)
            })

    def show_window(self, current_partition, before_partition_size, after_partition_size):
        self.current_partition = current_partition
        self.builder.get_object('resize_move_partition_window').set_title(self._language_manager.translate_msg('edit_partition_page', 'title'))
        self.win_parent.window_status(False)

        self.builder.get_object('resize_move_win_minimum_size_label').set_text(
            self._language_manager.translate_msg('edit_partition_page', 'minimum_size') + ' ' + current_partition.used_size_str)
        self.builder.get_object('resize_move_win_maximum_size_label').set_text(
            self._language_manager.translate_msg('edit_partition_page', 'maximum_size') + ' ' + str(current_partition.size + before_partition_size + after_partition_size) + ' Mio')

        self.builder.get_object('resize_move_win_partition_size_label').set_text(
            self._language_manager.translate_msg('edit_partition_page', 'partition_size'))
        self.builder.get_object('resize_move_win_free_size_before_partition_label').set_text(
            self._language_manager.translate_msg('edit_partition_page', 'before_partition_size'))
        self.builder.get_object('resize_move_win_free_size_after_partition_label').set_text(
            self._language_manager.translate_msg('edit_partition_page', 'after_partition_size'))
        self.builder.get_object('resize_move_win_cancel_btn').set_label(
            self._language_manager.translate_msg('edit_partition_page', 'cancel'))
        self.builder.get_object('resize_move_win_resize_btn').set_label(
            self._language_manager.translate_msg('edit_partition_page', 'resize'))
        
       
        incrementation = 1
        adj_size = Gtk.Adjustment(current_partition.size, current_partition.used_size, current_partition.size + before_partition_size + after_partition_size + 1, incrementation, 1, 1)
        self.builder.get_object('resize_move_win_partition_size_entry_spinner').configure(adj_size, 1, 0)
        adj_before_size = Gtk.Adjustment(before_partition_size, 0, current_partition.free_size + before_partition_size + after_partition_size, incrementation, 1, 1)
        self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn').configure(adj_before_size, 1, 0)
        adj_after_size = Gtk.Adjustment(after_partition_size, 0, current_partition.free_size + before_partition_size + after_partition_size, incrementation, 1, 1)
        self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').configure(adj_after_size, 1, 0)


        self.partition_value = current_partition.size
        self.partition_before_value = before_partition_size
        self.partition_after_value = after_partition_size


        self.set_value_by_code(self.builder.get_object('resize_move_win_partition_size_entry_spinner'), current_partition.size, self.on_partition_value_changed_callback)
        self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn'), before_partition_size, self.on_before_free_value_changed_callback)
        self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn'), after_partition_size, self.on_after_free_value_changed_callback)

        if self.on_partition_value_changed_callback is None:
            self.on_partition_value_changed_callback = self.on_partition_value_changed
            self.on_before_free_value_changed_callback = self.on_before_free_value_changed
            self.on_after_free_value_changed_callback = self.on_after_free_value_changed
            
            self.builder.get_object('resize_move_win_partition_size_entry_spinner').connect('value-changed', self.on_partition_value_changed_callback)
            self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn').connect('value-changed', self.on_before_free_value_changed_callback)
            self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').connect('value-changed', self.on_after_free_value_changed_callback)

        self.builder.get_object('resize_move_partition_window').show_all()

    def hide_window(self):
        self.win_parent.window_status(True)
        self.builder.get_object('resize_move_partition_window').hide()

    def apply(self, *args):
        self.current_partition.set_size(self.partition_value)
        self.current_partition.set_free_size(self.current_partition.size - self.current_partition.used_size)
        self.win_parent.resize_move_partition(self.current_partition, self.partition_before_value, self.partition_after_value)
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
        new_value = self.builder.get_object('resize_move_win_partition_size_entry_spinner').get_value_as_int()
        difference = 0

        if new_value > self.partition_value: # button +
            difference = new_value - self.partition_value
            difference_after = self.partition_after_value - difference
            
            if difference_after < 0:
                to_positive = difference_after * -1
                difference_after = self.partition_after_value - (difference - to_positive)
                
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
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn'), difference_before, self.on_before_free_value_changed_callback)
                self.partition_before_value = difference_before

            if self.partition_after_value != difference_after:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn'), difference_after, self.on_after_free_value_changed_callback)
                self.partition_after_value = difference_after

        elif new_value < self.partition_value: # button -
            difference = self.partition_value - new_value
            after_value = self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').get_value_as_int()
            
            if self.partition_after_value != after_value + difference:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn'), after_value + difference, self.on_after_free_value_changed_callback)
                self.partition_after_value = after_value + difference
            
        self.partition_value = self.builder.get_object('resize_move_win_partition_size_entry_spinner').get_value_as_int()


    def on_after_free_value_changed(self, event):
        new_value = self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').get_value_as_int()
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
                self.set_value_by_code(self.builder.get_object('resize_move_win_partition_size_entry_spinner'), difference_partition, self.on_partition_value_changed_callback)
                self.partition_value = difference_partition


            if self.partition_before_value != difference_before:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn'), difference_before, self.on_before_free_value_changed_callback)
                self.partition_before_value = difference_before

        elif new_value < self.partition_after_value: # button -
            difference = self.partition_after_value - new_value
            before_value = self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn').get_value_as_int()

            if self.partition_before_value != before_value + difference:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn'), before_value + difference, self.on_before_free_value_changed_callback)
                self.partition_before_value = before_value + difference
            
        self.partition_after_value = self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').get_value_as_int()


    def on_before_free_value_changed(self, event):
        new_value = self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn').get_value_as_int()
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
                self.set_value_by_code(self.builder.get_object('resize_move_win_partition_size_entry_spinner'), difference_partition, self.on_partition_value_changed_callback)
                self.partition_value = difference_partition

            if self.partition_after_value != difference_after:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn'), difference_after, self.on_after_free_value_changed_callback)
                self.partition_after_value = difference_after

        elif new_value < self.partition_before_value: # button -
            difference = self.partition_before_value - new_value
            after_value = self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn').get_value_as_int()
            
            if self.partition_after_value != after_value + difference:
                self.set_value_by_code(self.builder.get_object('resize_move_win_free_size_after_partition_entry_spinn'), after_value + difference, self.on_after_free_value_changed_callback)
                self.partition_after_value = after_value + difference

        self.partition_before_value = self.builder.get_object('resize_move_win_free_size_before_partition_entry_spinn').get_value_as_int()
