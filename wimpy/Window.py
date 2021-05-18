import logging
import win32gui

class Window(object):
    """Represents a single window"""

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._cache_properties()

    def __eq__(self, value):
        return int(self.hwnd) == int(value.hwnd)

    def __hash__(self):
        return hash(self.hwnd)

    def __str__(self):
        return f"[{int(self.hwnd)}] {self.title} ({self.classname})"

    def _cache_properties(self):
        self.display_size = self._get_display_size()
        self.title = self._get_title()
        self.classname = self._get_classname()

    def _get_display_size(self):
        return win32gui.GetWindowRect(self.hwnd)

    def _get_title(self):
        return win32gui.GetWindowText(self.hwnd)

    def _get_classname(self):
        return win32gui.GetClassName(self.hwnd)

    def move_to(self, window_size):
        logging.debug(f"{self.title} move_to {window_size}.")
        l, t, r, b = window_size
        win32gui.MoveWindow(self.hwnd, l, t, r - l, b - t, True)
        win32gui.UpdateWindow(self.hwnd)