import os

import parted

import egg.disk_management


class Partition(object):

    def __init__(self, partition: parted.Partition):
        self.rawPartition = partition

    @property
    def name(self) -> str:
        return self.rawPartition.get_name()

    @property
    def path(self) -> str:
        return self.rawPartition.path

    @property
    def capacity(self) -> int:
        return self.rawPartition.getLength()

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
