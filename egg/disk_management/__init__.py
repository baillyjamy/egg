import os
from typing import List

import parted

from egg.command import Command, cmd_exec

__all__ = ['Disk', 'Partition']

from egg.disk_management.disk import Disk
from egg.disk_management.partition import Partition


class DiskActionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_disk(device_path: str) -> Disk:
    return Disk(device_path=device_path)


def get_disks() -> List[Disk]:
    return list(map(lambda x: Disk(x), parted.getAllDevices()))


def is_mounted(path: str):
    cmd = Command("LANG=C mount | grep -w %s" % path)
    cmd.start()
    status = cmd.wait()
    (output, outputError) = cmd.process.communicate()
    if not output or status != 0:
        return False
    else:
        # Split opts.
        items = output.decode("utf-8").split(" ")
        return {"path": items[0], "mountpoint": items[2], "type": items[4],
                "options": items[-1].replace("(", "").replace(")", "").replace("\n", "")}


def mount_partition(parted_part: parted.partition = None, path: str = None, number: int = 1):
    if parted_part:
        path = parted_part.path
    elif not path:
        raise DiskActionError("mount_partition called without parted_part and without path!")

    if path.startswith("/") and not os.path.exists(path):
        raise DiskActionError("%s does not exist!" % path)

    _directory = path.replace("/", "")
    _mountpoint = os.path.join("/egg/mountpoints/%d" % number, _directory)
    if not os.path.exists(_mountpoint):
        os.makedirs(_mountpoint)

    if is_mounted(path):
        _mountpoint = is_mounted(path)["mountpoint"]
    else:
        cmd_exec("mount %s %s" % (path, _mountpoint))

    return _mountpoint


def umount_partition(parted_part=None, path=None, tries=0):
    if parted_part:
        path = parted_part.path
    elif not path:
        raise DiskActionError("umount_partition called without parted_part and without path!")

    if not is_mounted(path):
        raise DiskActionError("%s is not mounted!" % path)
    cmd_exec("umount %s" % path)
