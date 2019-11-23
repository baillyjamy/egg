import copy
from typing import List

import parted

from egg.disk_management.partition import Partition
from egg.install_queue.install_event import InstallEvent, BasicInstallCommandEvent
from egg.install_queue.install_queue import InstallQueue


class Disk(object):

    def __init__(self, device: parted.Device = None, device_path: str = None, is_managed: bool = True):
        if device is not None:
            self.device: parted.Device = device
        elif device_path:
            self.device: parted.Device = parted.getDevice(device_path)
        else:
            raise parted.DiskException("no device specified")
        self.disk: parted.Disk = parted.newDisk(self.device)
        if self.disk is not None:
            self.partitions: List[Partition] = list(map(lambda x: Partition(x), self.disk.partitions))
        self.is_managed: bool = is_managed

    def __del__(self):
        self.device.removeFromCache()

    def write_table(self, table_name: str):
        if self.is_managed:
            self.disk = parted.freshDisk(self.device, table_name)
        else:
            event = DiskInstallEvent(self.path, self.write_table.__name__, table_name=table_name)
            InstallQueue().add(event)

    def add_partition(self, fs: Partition.Filesystem, partition_type: Partition.Type, size: int, unit: str):
        if self.is_managed:
            if len(self.partitions) == 0:
                start = 0
            else: 
                start = self.partitions[len(self.partitions) - 1].end + 1

            sectors = parted.sizeToSectors(size, unit, self.device.sectorSize)
            geometry = parted.Geometry(start=start, length=sectors, device=self.device)
            filesystem = parted.FileSystem(type=fs.value, geometry=geometry)
            partition = parted.Partition(disk=self.disk, type=partition_type.value, fs=filesystem, geometry=geometry)
            self.disk.addPartition(partition, constraint=self.device.optimalAlignedConstraint)
            partition.setFlag(parted.PARTITION_NORMAL)
            self.disk.commit()

            event = None
            if fs is Partition.Filesystem.EXT4:
                event = BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkfs.ext4 -F " + partition.path)
            elif fs is Partition.Filesystem.SWAP:
                event = BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkswap -f " + partition.path)
            elif fs is Partition.Filesystem.FAT32:
                event = BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkfs.vfat " + partition.path)
            return InstallQueue().add(event)
        else:
            event = DiskInstallEvent(self.path, self.add_partition.__name__, fs=fs, partition_type=partition_type,
                                     size=size, unit=unit)
            return InstallQueue().add(event)

    def to_unmanaged(self):
        unmanaged_disk = copy.copy(self)
        unmanaged_disk.is_managed = False
        return unmanaged_disk

    def get_and_refresh_partition(self):
        self.partitions: List[Partition] = list(map(lambda x: Partition(x), self.disk.partitions))
        return self.partitions


    @property
    def model(self) -> str:
        return str(self.device.model)

    @property
    def type(self) -> str:
        return self.disk.type

    @property
    def capacity(self) -> int:
        return self.device.getLength() * self.device.sectorSize

    @property
    def path(self) -> str:
        return self.device.path


class DiskInstallEvent(InstallEvent):

    def __init__(self, device_path: str, method_name: str, **kwargs):
        super().__init__(InstallEvent.EventType.DISK, method_name, **kwargs)
        self.device_path = device_path

    def exec(self):
        disk = Disk(device_path=self.device_path)
        getattr(disk, self.method_name)(**self.kwargs)
