import logging

import wimpy.win32 as win32

from wimpy.WindowTracker import WindowTracker


class DebugWindowTracker(WindowTracker):

    def should_track_handle(self, hwnd):
        should_track = super().should_track_handle(hwnd)

        logging.debug(
            f"[{hwnd}] {win32.GetWindowText(hwnd)} ({win32.GetWindowClassName(hwnd)}) :: {'TRACKED' if should_track else 'IGNORED'}")
        if should_track:
            self._print_window_styles(hwnd)

        return should_track

    def _print_window_styles(self, hwnd):
        style_map = win32.GetWindowStyleMap(hwnd)
        for key, val in style_map.items():
            logging.debug(f"{key}: {val}")
