
class SizeCalculator(object):

    @staticmethod
    def get_human_size(size):
        power = 2**10
        power_labels = {0 : '', 1: 'k', 2: 'm', 3: 'g', 4: 't'}
        i = 0
        while size > power:
            size /= power
            i += 1
        return str(round(size, 2)), str(power_labels[i] + 'o')

    @staticmethod
    def get_mo_size(size):
        power = 2**10

        size /= power
        size /= power

        return round(size, 2)
