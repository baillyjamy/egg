import parted

from egg.disk_management.disk import Disk


class DiskService(object):

    def get_disk_list(self):
        return list(map(lambda x: Disk(x), parted.getAllDevices()))

    def get_disk(self, device_path):
        return Disk(device=None, device_path=device_path)
