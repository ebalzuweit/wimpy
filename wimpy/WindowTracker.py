import ctypes
import logging
import win32con

import wimpy.config as config
import wimpy.win32 as win32


class WindowTracker(object):
    """description of class"""

    def __init__(self):
        self.tracked_window_handles = set()

    def refresh(self):
        handles = win32.EnumWindows()
        to_track = [h for h in handles if self.should_track_handle(h)]
        self.tracked_window_handles = to_track

    def add_handle(self, hwnd):
        if hwnd in self.tracked_window_handles:
            logging.debug(f"[{hwnd}] Ignoring duplicate window")
            return False
        if not self.should_track_handle(hwnd):
            logging.debug(f"[{hwnd}] Ignoring window")
            return False

        self.tracked_window_handles.append(hwnd)
        logging.debug(f"[{hwnd}] Tracking window")
        return True

    def remove_handle(self, hwnd):
        if hwnd in self.tracked_window_handles:
            self.tracked_window_handles.remove(hwnd)
            logging.debug(f"[{hwnd}] Stopped tracking window")
            return True
        return False

    def should_track_handle(self, hwnd):
        try:
            # check styles
            style = win32.GetWindowStyles(hwnd)
            caption = bool(style & win32con.WS_CAPTION)
            popup = bool(style & win32con.WS_POPUP)
            visible = bool(style & win32con.WS_VISIBLE)
            maxbox = bool(style & win32con.WS_MAXIMIZEBOX)
            minbox = bool(style & win32con.WS_MINIMIZEBOX)
            if not caption or popup or not maxbox or not minbox:
                return False

            # check visibility
            visible = win32.IsWindowVisible(hwnd)
            if not visible:
                return False

            iconic = win32.IsIconic(hwnd)
            if iconic:
                return False

            zoomed = ctypes.windll.user32.IsZoomed(hwnd)
            if zoomed:
                return False

            # check ignored classnames
            classname = win32.GetWindowClassName(hwnd)
            if classname in config.ignored_classnames():
                return False

            logging.info(
                f"[{hwnd}] {classname} - caption:{caption} popup:{popup}, visible:{visible}, maxbox:{maxbox}, minbox:{minbox}")
            self._print_window_styles(hwnd)
            return True
        except:
            logging.error(
                f"[{hwnd}] Error in should_track_handle:", exc_info=True)
            return False

    def _print_window_styles(self, hwnd):
        style_map = win32.GetWindowStyleMap(hwnd)
        for key, val in style_map.items():
            logging.debug(f"{key}: {val}")
