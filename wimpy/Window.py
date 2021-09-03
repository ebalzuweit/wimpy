import logging
import win32con
import win32gui

import wimpy.win32 as win32


class Window(object):
    """Represents a single window"""

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self._cache_properties()
        self.initial_size = self.display_size

    def refresh(self):
        self._cache_properties()

    def restore_initial_position(self):
        return self.move_to(self.initial_size)

    def move_to(self, window_size):
        logging.debug(
            f"move_to: {self.pretty_title} [{int(self.hwnd)}]\t{self.display_size} -> {window_size}")
        l, t, r, b = window_size
        win32.MoveWindow(self.hwnd, l, t, r - l, b - t, True)
        self.display_size = window_size

    def set_topmost(self, topmost):
        if self.topmost == topmost:
            return False

        l, t, r, b = self.display_size
        win32.SetWindowPos(
            self.hwnd, win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST, l, t, r - l, b - t, 0)
        self.topmost = topmost
        return True

    def _pretty_title(self):
        if " - " in self.title:
            parts = self.title.split(" - ")
            return " - ".join(parts[::-1])
        return self.title

    def _cache_properties(self):
        self.display_size = win32.GetWindowRect(self.hwnd)
        self.title = win32.GetWindowText(self.hwnd)
        self.pretty_title = self._pretty_title()
        self.classname = win32.GetWindowClassName(self.hwnd)
        self.topmost = self._get_topmost()

    def _get_topmost(self):
        try:
            exstyle = win32.GetWindowExStyles(self.hwnd)
            return exstyle & win32con.WS_EX_TOPMOST
        except:
            return False

    def __eq__(self, value):
        return int(self.hwnd) == int(value.hwnd)

    def __hash__(self):
        return hash(self.hwnd)

    def __str__(self):
        return self.pretty_title
