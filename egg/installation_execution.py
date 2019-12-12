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
from egg.network_management.interfaces_service import NetworkType, NetworkIpAttributionType

from egg.filesystem import Filesystem
import os


def sort_by_path(left, right):
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
        InstallQueue().execAll()
        
        # Exec formatage
        InstallQueue().execAll()
        partitions_in_dd = DiskService().get_disk(self._config_general["selection_disk_page"]["current_disk_service"].path).partitions
        partitions = list(zip(self._config_general['partition_disk']['partitions'], partitions_in_dd))
        partitions = sorted(partitions, key=cmp_to_key(lambda a, b: sort_by_path(a, b)))

        # Mount multiple partitions
        raven_install_path = self._config_general['install_mount_point']
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkdir -p " + raven_install_path))
        
        for current_ui, current in partitions:
            if current_ui.mount_point and current_ui.filesystem is not Filesystem.SWAP:
                InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mkdir -p " + raven_install_path + current_ui.mount_point))
                InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="mount " + current.path + " " + raven_install_path + current_ui.mount_point))            

        # Install Raven
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' pull"))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install corefs"))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install bash coreutils"))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="yes | " + self._config_general["nest_path"] + "nest --chroot='" + raven_install_path + "' install essentials-boot linux"))

        for current_ui, current in partitions:
            if current_ui.filesystem is Filesystem.SWAP:
                InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "swapon " + current.path)))


        # Install config
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "useradd -c '" + self._config_general["user_page"]["user_realfullname"] + " -p '" + self._config_general["user_page"]["user_password"] + "' -m " + self._config_general["user_page"]["user_username"])))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo -e \"" + self._config_general["user_page"]["root_password"] + "\n" + self._config_general["user_page"]["root_password"] + "\"")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "rm -f /etc/localtime")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "ln -sf /usr/share/zoneinfo/" + self._config_general["timezone_page"]["timezone_zone"] + " /etc/localtime")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo 'KEYMAP=\"" + self._config_general["language_installation_page"]["keyboard"] + "\"' > /etc/vconsole.conf")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo 'LANG=\"" + self._config_general["language_installation_page"]["locale"] + "\"' > /etc/locale.conf")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo '" + self._config_general["network_page"]["hostname"] + "' > /etc/hostname")))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="genfstab -U -p " + raven_install_path + " > /etc/fstab"))



        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=("grub_var=`which grub2-install > /dev/null 2>&1 && echo grub2 || echo grub`; $grub_var-install --target=x86_64-efi --themes= --recheck --removable --efi-directory='" + raven_install_path + "/boot/efi" + " --boot-directory='" + raven_install_path + "/boot" + "' && sync"))
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=("grub_var=`which grub2-install > /dev/null 2>&1 && echo grub2 || echo grub`; $grub_var-install --target=i386-pc --themes= --recheck --boot-directory='" + raven_install_path + "/boot" + "' " + self._config_general["selection_disk_page"]["current_disk_service"].path + " && sync"))

        #/boot/grub/grub.cfg

        if self._config_general["network_page"]["current_interface_configuration"] is not None and self._config_general["network_page"]["current_interface_configuration"].networkIpAttributionType is NetworkIpAttributionType.MANUAL:
            nameservers = ""
            nameservers2 = ""

            if self._config_general["network_page"]["current_interface_configuration"].nameServer1:
                nameservers += self._config_general["network_page"]["current_interface_configuration"].nameServer1
                nameservers2 += self._config_general["network_page"]["current_interface_configuration"].nameServer1

            if self._config_general["network_page"]["current_interface_configuration"].nameServer2:
                if nameservers:
                    nameservers += "\n" + self._config_general["network_page"]["current_interface_configuration"].nameServer2
                    nameservers2 += " " + self._config_general["network_page"]["current_interface_configuration"].nameServer2
                else:
                    nameservers += self._config_general["network_page"]["current_interface_configuration"].nameServer2
                    nameservers2 += self._config_general["network_page"]["current_interface_configuration"].nameServer2

            if nameservers:
                InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo -e \"" + nameservers  + "\" > /etc/resolv.conf")))
            else:
                nameservers2 = "8.8.8.8 8.8.4.4"

            interface_config = "interface " + self._config_general["network_page"]["current_interface_configuration"].nameInterface + "\n"
            interface_config += "static ip_address=" + self._config_general["network_page"]["current_interface_configuration"].ipAddress + "/24\n"
            interface_config += "static routers=" + self._config_general["network_page"]["current_interface_configuration"].gatewayAddress + "\n"
            interface_config += "domain_name_servers=" + self._config_general["network_page"]["current_interface_configuration"].nameservers2
        else:
            interface_config = "hostname\nduid\npersistent\noption rapid_commit\noption domain_name_servers, domain_name, domain_search, host_name\n"
            interface_config += "option classless_static_routes\noption ntp_servers\noption interface_mtu\nrequire dhcp_server_identifier\nslaac private"
        InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command=chroot_command(raven_install_path, "echo -e \"" + interface_config  + "\" > /etc/dhcpcd.conf")))


        # for current_ui, current in partitions:
        #     if current_ui.mount_point and current_ui.filesystem is not Filesystem.SWAP:
        #         InstallQueue().add(BasicInstallCommandEvent(BasicInstallCommandEvent.exec_command.__name__, command="umount " + current.path))


        # Raven Configuration
        InstallQueue().execAll()