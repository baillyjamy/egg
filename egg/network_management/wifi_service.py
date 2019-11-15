import wifi


class WifiService(object):
    
    network_card = None

    def __init__(self, network_card):
        self.network_card = network_card

    def ListWifi(self):
        wifissid = []

        cells = wifi.Cell.all(self.network_card)

        for cell in cells:
            wifissid.append(cell)

        return wifissid





    # def Connect(ssid, password=None):
    #     cell = FindFromSearchList(ssid)

    #     if cell:
    #         savedcell = FindFromSavedList(cell.ssid)

    #         # Already Saved from Setting
    #         if savedcell:
    #             savedcell.activate()
    #             return cell

    #         # First time to conenct
    #         else:
    #             if cell.encrypted:
    #                 if password:
    #                     scheme = Add(cell, password)

    #                     try:
    #                         scheme.activate()

    #                     # Wrong Password
    #                     except wifi.exceptions.ConnectionError:
    #                         Delete(ssid)
    #                         return False

    #                     return cell
    #                 else:
    #                     return False
    #             else:
    #                 scheme = Add(cell)

    #                 try:
    #                     scheme.activate()
    #                 except wifi.exceptions.ConnectionError:
    #                     Delete(ssid)
    #                     return False

    #                 return cell
        
    #     return False
