import threading
import subprocess

from egg.disk_management import Partition
from functools import cmp_to_key
from ui.gtk.main_window_button import MainWindowButton
from egg.language_management import LanguageManagement
from egg.install_queue.install_queue import InstallQueue
from egg.install_queue.install_event import BasicInstallCommandEvent
from egg.disk_management.disk import Disk
from egg.disk_management.diskservice import DiskService

from egg.filesystem import Filesystem
import os


def sort_by_path(left, right):
    # Si ma string 1 est plus grande que la string 2 et que l'index 1 est inferieur 2
    # Ou Si ma string 1 est plus petite que la string 2 et que l'index 1 est superieur à 2
    left_ui_partition, left_partition = left
    right_ui_partition, right_partition = right

    if not left_ui_partition.mount_point and right_ui_partition.mount_point:
        return 1
    elif left_ui_partition.mount_point and not right_ui_partition.mount_point:
        return -1

    if left_ui_partition.mount_point is not right_ui_partition.mount_point \
        and (left_ui_partition.mount_point.startswith(os.path.abspath(right_ui_partition.mount_point)) or right_ui_partition.mount_point.startswith(os.path.abspath(left_ui_partition.mount_point))) \
        and len(list(filter(None, right_ui_partition.mount_point.split(os.path.sep)))) > len(list(filter(None, left_ui_partition.mount_point.split(os.path.sep)))):
        return -1
    elif left_ui_partition.mount_point is not right_ui_partition.mount_point \
        and (left_ui_partition.mount_point.startswith(os.path.abspath(right_ui_partition.mount_point)) or right_ui_partition.mount_point.startswith(os.path.abspath(left_ui_partition.mount_point))) \
        and len(list(filter(None, right_ui_partition.mount_point.split(os.path.sep)))) < len(list(filter(None, left_ui_partition.mount_point.split(os.path.sep)))):
        return 1

    return 0

def chroot_command(path: str, command: str) -> str:
    return "chroot " + path + " /bin/bash -c '" + command + "'"

class InstallRavenOS:

    def __init__(self, locale_general: LanguageManagement, config_general: dict) -> None:
        self._locale_general = locale_general
        self._config_general = config_general
    
    def install_raven_os(self):
        # Exec event
        # InstallQueue().execAll()
        
        # Exec formatage
        # InstallQueue().execAll()
        InstallQueue().clearAll()
        partitions_in_dd = DiskService().get_disk(self._config_general["selection_disk_page"]["current_disk_service"].path).partitions
        partitions = list(zip(self._config_general['partition_disk']['partitions'], partitions_in_dd))
        partitions = sorted(partitions, key=cmp_to_key(lambda a, b: sort_by_path(a, b)))

        # Mount multiple partitions
        raven_install_path = self._config_general['install_mount_point']
        # InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkdir -p " + raven_install_path))
        
        # for current_ui, current in partitions:
        #     if current_ui.mount_point and current_ui.filesystem is not Filesystem.SWAP:
        #         InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkdir -p " + raven_install_path + current_ui.mount_point))
        #         InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mount " + current.path + " " + raven_install_path + current_ui.mount_point))            

        # Install Raven
        # InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' pull"))
        # InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install corefs"))
        # InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install bash coreutils"))
        # InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install essentials linux"))

        for current_ui, current in partitions:
            if current_ui.filesystem is Filesystem.SWAP:
                InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "swapon " + current.path)))


        # Install config
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "rm -f /etc/localtime")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "ln -sf /usr/share/zoneinfo/" + self._config_general["timezone_page"]["timezone_zone"] + " /etc/localtime")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo 'KEYMAP=\"" + self._config_general["language_installation_page"]["keyboard"] + "\"' > /etc/vconsole.conf")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo 'LANG=\"" + self._config_general["language_installation_page"]["locale"] + "\"' > /etc/locale.conf")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo '" + self._config_general["network_page"]["hostname"] + "' > /etc/hostname")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="genfstab -U -p " + raven_install_path + " > /etc/fstab"))


        # for current_ui, current in partitions:
        #     if current_ui.mount_point and current_ui.filesystem is not Filesystem.SWAP:
        #         InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="umount " + current.path))


        # Raven Configuration
        InstallQueue().execAll()