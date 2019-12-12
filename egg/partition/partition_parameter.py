import parted
from egg.filesystem import Filesystem


class PartitionParameter:
    # Restrict mount point to enum or not ?
    partition_name = ''
    name = ''
    filesystem = None
    mount_point = ''
    label = ''
    size_str = ''
    size = 0.0
    used_size_str = ''
    used_size = 0.0
    free_size_str = ''
    free_size = 0.0
    is_bootable = False

    def __init__(self, partition_name: str=None, name: str=None, filesystem: Filesystem=Filesystem.NOT_ALLOCATED, is_bootable: bool=False, mount_point: str=None, label: str=None,
                 size: float=None, used_size: float=None, free_size: float=None) -> None:
        self.partition_name = partition_name
        self.name = name
        self.filesystem = filesystem
        self.mount_point = mount_point
        self.label = label
        self.set_size(size)
        self.set_used_size(used_size)
        self.set_free_size(free_size)
        self.is_bootable = is_bootable

    def convert_str_to_filesytem(self, filesystem):
        if filesystem == "ntfs":
            return Filesystem.NTFS
        elif filesystem == "ext4":
            return Filesystem.EXT4
        elif filesystem == "fat32":
            return Filesystem.FAT32
        else:
            return Filesystem.UNKNOWN

    def load_partition(self, partition):
        self.partition_name = partition.path
        self.name = partition.name
        if partition.filesystem is not None and partition.filesystem.type is not None:
            self.filesystem = self.convert_str_to_filesytem(partition.filesystem.type)#Convert
        else:
            self.filesystem = Filesystem.UNKNOWN
        self.mount_point = partition.mountpoint
        self.label = ''
        self.set_size(partition.capacity(unit='MiB')) # convert to mo
        try:
            freesize = round(parted.formatBytes(partition.freespace, "MiB"), 2)
            self.set_free_size(freesize)  # convert to mo
            used_space = round(partition.capacity(unit='MiB') - freesize, 2)
            self.set_used_size(used_space)  # convert to mo
        except Exception as e:
            return

    def set_size(self, size: float) -> None:
        self.size = size
        self.size_str = str(size) + ' Mio'

    def set_used_size(self, used_size: float) -> None:
        self.used_size = used_size
        self.used_size_str = str(used_size) + ' Mio'  # Mio

    def set_free_size(self, free_size: float) -> None:
        self.free_size = free_size
        self.free_size_str = str(free_size) + ' Mio'

    def change_partition_to_unallocated(self, name):
        self.partition_name = ''
        self.name = name
        self.set_used_size(0)
        self.set_free_size(0)
        self.mount_point = ''
        self.filesystem = Filesystem.NOT_ALLOCATED
        self.label = ''

    def get_partition_desc(self):
        return self.partition_name + " " + self.name + " " + self.mount_point + " " + self.size_str + " (" + self.filesystem.value + ")"
