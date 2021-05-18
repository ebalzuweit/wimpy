def area_from_size(size):
    l, t, r, b = size
    return (r - l) * (b - t)

def inset_size(size, inset):
    return (size[0] + inset[0], size[1] + inset[1], size[2] - inset[2], size[3] - inset[3])

class WindowManagementStrategy(object):
    """stuff"""

    def apply(self, displays, windows):
        pass
