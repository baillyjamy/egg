import os
from enum import Enum
import parted

import egg.disk_management
from egg.install_queue.install_event import InstallEvent


class Partition(object):

    class Type(Enum):
        PARTITION_NORMAL = parted.PARTITION_NORMAL
        PARTITION_LOGICAL = parted.PARTITION_LOGICAL
        PARTITION_EXTENDED = parted.PARTITION_EXTENDED

    class Filesystem(Enum):
        EXT4 = "ext4"
        SWAP = "swap"

    def __init__(self, partition: parted.Partition):
        self.rawPartition = partition

    @property
    def name(self) -> str:
        return self.rawPartition.get_name()

    @property
    def path(self) -> str:
        return self.rawPartition.path

    def capacity(self, unit='MB') -> int:
        return self.rawPartition.getLength(unit)

    @property
    def filesystem(self) -> parted.FileSystem:
        return self.rawPartition.fileSystem

    @property
    def start(self) -> int:
        return self.rawPartition.geometry.start

    @property
    def end(self) -> int:
        return self.rawPartition.geometry.end

    @property
    def freespace(self):
        mounted = egg.disk_management.mount_partition(parted_part=self.rawPartition)
        info = os.statvfs(mounted)
        free = info.f_frsize * info.f_bavail
        egg.disk_management.umount_partition(parted_part=mounted)
        return free


class PartitionInstallEvent(InstallEvent):

    def __init__(self, disk_path: str, partition_number: int, method_name: str, **kwargs):
        super().__init__(InstallEvent.EventType.PARTITION, method_name, **kwargs)
        self.disk_path = disk_path
        self.partition_number = partition_number

    def exec(self):
        from egg.disk_management import Disk
        partition = Partition(Disk(device_path=self.disk_path).partitions[self.partition_number])
        getattr(partition, self.method_name)(**self.kwargs)
