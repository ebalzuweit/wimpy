import logging

import wimpy.config as config

from wimpy.Display import Display
from wimpy.WindowManagementStrategy import *

class BSPTilingStrategy(WindowManagementStrategy):
    """description of class"""

    def __init__(self):
        pass

    def apply(self, display, windows, active_hwnd):
        # filter out topmost windows
        notopmost_windows = list(filter(lambda w: not w.topmost, windows))
        self._partition_display(display, notopmost_windows, active_hwnd)

    def _partition_display(self, display, windows, active_hwnd):
        display_size = inset_size(display.display_size, config.display_padding())
        self._recursive_partition(display_size, windows, active_hwnd)

    def _recursive_partition(self, display_size, windows, active_hwnd):
        if len(windows) == 0:
            return
        elif len(windows) == 1:
            self._move_window(windows[0], display_size)
        else:
            # partition the display_size
            left_size, right_size = self._split_display_size(display_size)
            left = []
            right = []

            # sort window order for placement (by largest preference)
            windows.sort(key=lambda w: abs(self._get_partition_preference(w.display_size, left_size, right_size)), reverse=True)

            # assign windows to their preferred partition (if would not unbalance)
            max_windows = len(windows) // 2 + 1 if (len(windows) % 2 == 1) else len(windows) // 2
            for window in windows:
                pref = self._get_partition_preference(window.display_size, left_size, right_size)
                pref_text = "LEFT" if pref <= 0 else "RIGHT"
                if pref == 0:
                    pref_text = "NONE"
                if pref <= 0: # tiebreak prefers left
                    if len(left) < max_windows:
                        left.append(window)
                    else:
                        right.append(window)
                else:
                    if len(right) < max_windows:
                        right.append(window)
                    else:
                        left.append(window)

            self._recursive_partition(left_size, left, active_hwnd)
            self._recursive_partition(right_size, right, active_hwnd)

    def _get_partition_preference(self, size, a, b):
        """returns an int representing preference for b (positive) or a (negative)"""
        overlap_a = 0
        overlap_b = 0
        if check_overlap(size, a):
            overlap_a = overlap_area(size, a)
        if check_overlap(size, b):
            overlap_b = overlap_area(size, b)

        return overlap_b - overlap_a

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
            
