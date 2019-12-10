import netifaces
from enum import Enum

class NetworkType(Enum):
    WIFI = "wifi"
    ETH = "eth"

class NetworkIpAttributionType(Enum):
    DHCP = 1
    MANUAL = 2

class NetworkConfiguration(object):
    macAddress = None
    nameInterface = None
    ipAddress = None
    netMaskAddress = None
    gatewayAddress = None
    networkType = None # Interface type wlan or eth
    networkIpAttributionType = None
    nameServer1 = None
    nameServer2 = None

    def __init__(self, nameInterface, macAddress, networkType, ipAddress=None, netMaskAddress=None, gatewayAddress=None, nameServer1=None, nameServer2=None):
        self.nameInterface = nameInterface
        self.macAddress = macAddress
        self.networkType = networkType
        self.ipAddress = ipAddress
        self.netMaskAddress = netMaskAddress
        self.gatewayAddress = gatewayAddress
        self.nameServer1 = nameServer1
        self.nameServer2 = nameServer2
        if self.ipAddress is not None:
            self.networkIpAttributionType = NetworkIpAttributionType.MANUAL
        else:
            self.networkIpAttributionType = NetworkIpAttributionType.DHCP

class NetworkInterfaces(object):
    networkInterfaces = None
    networkGateways = None

    def __init__(self):
        self.networkInterfaces = netifaces.interfaces()
        self.networkGateways = netifaces.gateways()

    def refresh_interfaces(self):
        self.networkInterfaces = netifaces.interfaces()
        self.networkGateways = netifaces.gateways()

    def get_addrs_type(self, interfaces):
        for current in interfaces:
            if current is netifaces.AF_INET or current is netifaces.AF_INET6:
                return current
        return netifaces.AF_LINK

    def get_card_configuration(self, ifName):
        if ifName.startswith("en") or ifName.startswith("eth"):
            type_card = NetworkType.ETH
        elif ifName.startswith("wl"):
            type_card = NetworkType.WIFI
        else:
            return None
        addrs = netifaces.ifaddresses(ifName)
        addrs_type = self.get_addrs_type(addrs)
        addrs_detail = addrs[addrs_type]
        if len(addrs_detail) > 0:
            addrs_detail = addrs_detail[0]

        if addrs_type is netifaces.AF_LINK:
            return NetworkConfiguration(ifName, addrs_detail.get('addr', None), type_card)
        else:
            mac_addrs_detail = addrs[netifaces.AF_LINK]
            if len(mac_addrs_detail) > 0:
                mac_addrs_detail = mac_addrs_detail[0]
            return NetworkConfiguration(ifName, mac_addrs_detail.get('addr', None), type_card, addrs_detail.get('addr', None), addrs_detail.get('netmask', None))

    def get_all_cards(self):
        all_network_configurations = list()
        
        for current in self.networkInterfaces:
            res = self.get_card_configuration(current)
            if res is not None:
                all_network_configurations.append(res)
        return all_network_configurations