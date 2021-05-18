import logging

import wimpy.config as config

from wimpy.Display import Display
from wimpy.WindowManagementStrategy import *

class BSPTilingStrategy(WindowManagementStrategy):
    """description of class"""

    def __init__(self):
        pass

    def _partition_display(self, display, windows):
        logging.debug(f"Partitioning {len(windows)} window(s) for display '{display}'...")
        display_size = inset_size(display.display_size, config.display_padding())
        self._recursive_partition(display_size, windows)

    def _recursive_partition(self, display_size, windows):
        if len(windows) == 0:
            return
        elif len(windows) == 1:
            self._move_window(windows[0], display_size)
        else:
            # sort windows largest to smallest
            windows.sort(reverse=True, key=lambda w: area_from_size(w.display_size))

            # alternately assign windows to partitions
            right = [windows[i] for i in range(0, len(windows), 2)]
            left = [w for w in windows if w not in right]
            left_size, right_size = self._split_display_size(display_size)
            self._recursive_partition(left_size, left)
            self._recursive_partition(right_size, right)

    def _move_window(self, window, size):
        window_size = inset_size(size, config.window_margin())
        window.move_to(window_size)

    def _display_area(self, size):
        l, t, r, b = size
        return (r - l) * (b - t)

    def _split_display_size(self, size):
        l, t, r, b = size
        hw = (r - l) // 2
        hh = (b - t) // 2

        if hw > hh * config.partition_split_ratio():
            return [(l, t, l + hw, b), (l + hw, t, r, b)]
        else:
            return [(l, t, r, t + hh), (l, t + hh, r, b)]

    def apply(self, displays, windows):
        for display in displays:
            display_windows = list(filter(lambda w: display.contains_window(w.hwnd), windows))
            self._partition_display(display, display_windows)
