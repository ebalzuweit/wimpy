import logging
import win32api
import win32con

from wimpy.Window import Window

class Display(object):
    """Represents a single display"""

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._cache_properties()

    def __eq__(self, value):
        return int(self.hwnd) == int(value.hwnd)

    def __hash__(self):
        return hash(self.hwnd)

    def __str__(self):
        l, t, r, b = self.display_size
        return f"[{int(self.hwnd)}] {r - l}x{b - t} @ ({l}, {t}){' PRIMARY' if self.is_primary else ''}"

    def _cache_properties(self):
        self.display_size = self._get_display_size()
        self.is_primary = self._is_primary_display()

    def _get_display_size(self):
        return win32api.GetMonitorInfo(self.hwnd)["Work"]

    def _is_primary_display(self):
        primary_hwnd = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
        return primary_hwnd == self.hwnd

    def contains_window(self, window_hwnd):
        hwnd = win32api.MonitorFromWindow(window_hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        return hwnd == self.hwnd

    @staticmethod
    def enumerate():
        displays = []
        for hwnd, _, _ in win32api.EnumDisplayMonitors():
            displays.append(Display(hwnd))

        logging.debug(f"Display enumerate found {len(displays)} display(s).")
        return displays

