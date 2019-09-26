import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ColumnRowPartitionTreeview(Gtk.TreeView):
    liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
    current_partition_row = list()

    def __init__(self, config_general):
        Gtk.TreeView.__init__(self, model=self.liststore)
        self._config_general = config_general

    def add_new_column_title(self, name: str, column_pos: int):
        render_text = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(name, render_text, text=column_pos)
        self.append_column(column)
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def add_new_partition_row(self, partition):
        self.liststore.append([partition.partition_name, partition.name,
            partition.filesystem.value, partition.mount_point, partition.label,
            partition.size_str, partition.used_size_str, partition.free_size_str])
        self.current_partition_row.append(partition)
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def add_new_partition_row_before_idx(self, partition, row_iter, idx):
        self.liststore.insert_before(row_iter, [partition.partition_name, partition.name,
                               partition.filesystem.value, partition.mount_point, partition.label,
                               partition.size_str, partition.used_size_str, partition.free_size_str])
        self.current_partition_row.insert(idx, partition)
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def add_new_partition_row_after_idx(self, partition, row_iter, idx):
        self.liststore.insert_after(row_iter, [partition.partition_name, partition.name,
                               partition.filesystem.value, partition.mount_point, partition.label,
                               partition.size_str, partition.used_size_str, partition.free_size_str])
        self.current_partition_row.insert(idx + 1, partition)
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def update_partition_row(self, partition, idx):
        self.current_partition_row[idx] = partition
        self.liststore[idx][0] = partition.partition_name
        self.liststore[idx][1] = partition.name
        self.liststore[idx][2] = partition.filesystem.value
        self.liststore[idx][3] = partition.mount_point
        self.liststore[idx][4] = partition.label
        self.liststore[idx][5] = partition.size_str
        self.liststore[idx][6] = partition.used_size_str
        self.liststore[idx][7] = partition.free_size_str
        self._config_general['partition_disk']['partitions'] = self.current_partition_row


    def delete_columns_titles(self):
        columns = self.get_columns()
        for current in columns:
            self.remove_column(current)

    def delete_rows(self):
        self.liststore.clear()
        self.current_partition_row.clear()
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def delete_rows_by_row_list(self, delete):
        for current in delete:
            self.current_partition_row.remove(current)

        current_partition_row_copy = list(self.current_partition_row)
        self.current_partition_row.clear()
        self.liststore.clear()

        for current in current_partition_row_copy:
            self.add_new_partition_row(current)
        self._config_general['partition_disk']['partitions'] = self.current_partition_row

    def get_current_selected_row(self):
        selection = self.get_selection()
        (treemodel, treeiter) = selection.get_selected_rows()
        if treeiter is None or not treeiter:
            return None
        idx_selected_row = treeiter[0].get_indices()[0]
        if self.current_partition_row is not None and len(self.current_partition_row) > 0:
            return self.current_partition_row[idx_selected_row]
        return None

    def get_current_previous_selected_row(self):
        selection = self.get_selection()
        (treemodel, treeiter) = selection.get_selected_rows()
        if treeiter is None or not treeiter:
            return None
        idx_selected_row = treeiter[0].get_indices()[0] - 1
        if self.current_partition_row is not None and len(self.current_partition_row) > 0 and idx_selected_row > 0:
            return self.current_partition_row[idx_selected_row]
        return None

    def get_current_next_selected_row(self):
        selection = self.get_selection()
        (treemodel, treeiter) = selection.get_selected_rows()
        if treeiter is None or not treeiter:
            return None
        idx_selected_row = treeiter[0].get_indices()[0] + 1
        if self.current_partition_row is not None and len(self.current_partition_row) > 0 and idx_selected_row < len(self.current_partition_row):
            return self.current_partition_row[idx_selected_row]
        return None

    def get_current_selected_idx_row(self):
        selection = self.get_selection()
        (treemodel, treeiter) = selection.get_selected_rows()
        if treeiter is None or not treeiter:
            return 0
        return treeiter[0].get_indices()[0]


    def get_current_selected_iter_row(self):
        selection = self.get_selection()

        (treemodel, treeiter) = selection.get_selected()
        return treeiter