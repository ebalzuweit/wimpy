import collections
import ctypes
import logging
import win32con

import wimpy.config as config
import wimpy.win32 as win32

from wimpy.Display import Display
from wimpy.Window import Window

class WindowManager(object):
    """description of class"""

    def __init__(self, strategy):
        logging.info(f"Using strategy '{type(strategy).__name__}'.")
        self.strategy = strategy        
        self.MESSAGE_MAP = {
            win32con.EVENT_OBJECT_CREATE: self._on_object_create,
            win32con.EVENT_OBJECT_DESTROY: self._on_object_destroy,
            win32con.EVENT_OBJECT_HIDE: self._on_object_destroy,
            win32con.EVENT_OBJECT_LOCATIONCHANGE: self._on_location_change,
            win32con.EVENT_OBJECT_SHOW: self._on_object_create,
            win32con.EVENT_SYSTEM_MOVESIZESTART: self._on_movesize_start,
            win32con.EVENT_SYSTEM_MOVESIZEEND: self._on_movesize_end,
            win32con.EVENT_SYSTEM_MINIMIZESTART: self._on_minimize_start,
            win32con.EVENT_SYSTEM_MINIMIZEEND: self._on_minimize_end
        }
        
        self.displays = []
        self.windows = []
        self.tracked_window_handles = set()
        self.movesize_window_handle = None

        self._update_tracked_windows(0, 0)

    def on_event(self, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if hwnd is None:
            return
        if idObject != win32con.OBJID_WINDOW:
            return

        func = self.MESSAGE_MAP.get(event)
        if func is not None:
            func(hwnd, dwmsEventTime)

    def on_error(self, result, func, args):
        pass

    def restore_positions(self):
        logging.debug("Restoring window positions")
        for w in self.windows:
            w.restore_initial_position()

    def toggle_window_topmost(window):
        pass

    def refresh(self):
        self.displays = [Display(hwnd) for hwnd in win32.EnumDisplayMonitors()]
        self.windows = [Window(w) for w in self.tracked_window_handles]
        logging.debug(f"Refresh found {len(self.displays)} Display(s), {len(self.windows)} Window(s).")

        self._apply_strategy()

    def _start_tracking_window(self, hwnd):
        self.tracked_window_handles.add(hwnd)
        self.windows.append(Window(hwnd))
        self._apply_strategy_to_display_by_window(hwnd)

    def _stop_tracking_window(self, hwnd):
        display = self._get_display_by_window_handle(hwnd)
        self.tracked_window_handles.remove(hwnd)
        self.windows = list(filter(lambda w: w.hwnd != hwnd, self.windows))

        if display is not None:
            self._apply_strategy_to_display(display)

    def _apply_strategy(self):
        for display in self.displays:
            self._apply_strategy_to_display(display)

    def _apply_strategy_to_display(self, display):
        for w in self.windows:
            w.refresh()

        # get windows in display
        display_windows = [w for w in self.windows if display.contains_window(w.hwnd)]

        # apply strategy
        windows = [w for w in display_windows if w.hwnd != self.movesize_window_handle]
        logging.debug(f"Applying strategy to {len(windows)} window(s) in display '{display}'.")
        self.strategy.apply(display, windows, win32.GetForegroundWindow())

    def _apply_strategy_to_display_by_window(self, hwnd):
        display = self._get_display_by_window_handle(hwnd)
        if display is not None:
            self._apply_strategy_to_display(display)

    def _update_tracked_windows(self, _, dwmsEventTime):
        hwnds = win32.EnumWindows()
        window_handles = [w for w in hwnds if self._should_track_window(w)]

        added = [hwnd for hwnd in window_handles if hwnd not in self.tracked_window_handles]
        removed = [hwnd for hwnd in self.tracked_window_handles if hwnd not in window_handles]

        if len(added) > 0 or len(removed) > 0:
            logging.debug(f"Adding {len(added)} tracked window(s), removing {len(removed)}.")
            for w in added: self.tracked_window_handles.add(w)
            for w in removed: self.tracked_window_handles.remove(w)
            self.refresh()

    def _on_object_create(self, hwnd, dwmsEventTime):
        if not self._should_track_window(hwnd):
            return

        logging.debug(f"object_create: [{hwnd}]")
        self._start_tracking_window(hwnd)

    def _on_object_destroy(self, hwnd, dwmsEventTime):
        if hwnd in self.tracked_window_handles:
            logging.debug(f"object_destroy: [{hwnd}]")
            self._stop_tracking_window(hwnd)

    def _on_location_change(self, hwnd, dwmsEventTime):
        if hwnd == self.movesize_window_handle:
            return

        window = self._get_tracked_window_by_handle(hwnd)
        if window is not None:
            prev_size = window.display_size
            window.refresh()

            if prev_size != window.display_size:
                logging.debug(f"location_change: [{hwnd}] {window.pretty_title}")
                self._apply_strategy_to_display_by_window(hwnd)

    def _on_movesize_start(self, hwnd, dwmsEventTime):
        if hwnd in self.tracked_window_handles:
            logging.debug(f"Start moving [{hwnd}]")
            self.movesize_window_handle = hwnd
            self._apply_strategy_to_display_by_window(hwnd)

    def _on_movesize_end(self, hwnd, dwmsEventTime):
        if hwnd != self.movesize_window_handle:
            return

        logging.debug(f"Stopped moving [{hwnd}]")
        self.movesize_window_handle = None
        self._apply_strategy_to_display_by_window(hwnd)

    def _on_minimize_start(self, hwnd, dwmsEventTime):
        if hwnd in self.tracked_window_handles:
            logging.debug(f"minimize_start: [{hwnd}]")
            self._stop_tracking_window(hwnd)

    def _on_minimize_end(self, hwnd, dwmsEventTime):
        if not self._should_track_window(hwnd):
            return

        if hwnd not in self.tracked_window_handles:
            logging.debug(f"minimize_end: [{hwnd}]")
            self._start_tracking_window(hwnd)

    def _get_display_by_window_handle(self, hwnd):
        if hwnd not in self.tracked_window_handles:
            return None

        for display in self.displays:
            if display.contains_window(hwnd):
                return display
        return None

    def _get_tracked_window_by_handle(self, hwnd):
        if hwnd not in self.tracked_window_handles:
            return None

        for w in self.windows:
            if w.hwnd == hwnd:
                return w
        return None

    def _should_track_window(self, hwnd):
        try:
            # check styles
            style = win32.GetWindowStyles(hwnd)
            popup = bool(style & win32con.WS_POPUP)
            visible = bool(style & win32con.WS_VISIBLE)
            maxbox = bool(style & win32con.WS_MAXIMIZEBOX)
            minbox = bool(style & win32con.WS_MINIMIZEBOX)
            if popup or not maxbox or not minbox:
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

            return True
        except:
            return False