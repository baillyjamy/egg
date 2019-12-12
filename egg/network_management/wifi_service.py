import wifi


class WifiService(object):
    
    network_card = None

    def __init__(self, network_card):
        self.network_card = network_card

    def get_list_wifi(self):
        wifissid = []

        cells = wifi.Cell.all(self.network_card)

        for cell in cells:
            wifissid.append(cell)

        return wifissid