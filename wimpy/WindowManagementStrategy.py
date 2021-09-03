def area_from_size(size):
    l, t, r, b = size
    return (r - l) * (b - t)


def inset_size(size, inset):
    return (size[0] + inset[0], size[1] + inset[1], size[2] - inset[2], size[3] - inset[3])


def check_overlap(size_a, size_b):
    """return True if two display_size overlap"""
    if size_a[0] >= size_b[2] or size_a[1] >= size_b[3] or size_a[2] <= size_b[0] or size_a[3] <= size_b[1]:
        return False
    return True


def overlap_area(size_a, size_b):
    return min(size_a[2] - size_b[0], size_b[2] - size_a[0]) * min(size_a[3] - size_b[1], size_b[3] - size_a[1])


class WindowManagementStrategy(object):
    """stuff"""

    def apply(self, display, windows, active_hwnd):
        pass
