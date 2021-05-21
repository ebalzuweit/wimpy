import ctypes
import logging
import threading
import win32con
import win32gui

import wimpy.config as config

from wimpy.Display import Display
from wimpy.Window import Window

class DisplayManager(object):
    """Manages displays using the given strategy"""

    def __init__(self, management_strategy):
        logging.info(f"Using strategy '{type(management_strategy).__name__}'")
        self.management_strategy = management_strategy
        
        self.windows = []
        self.displays = []
        self.display_window_map = {}
        self.tracked_window_handles = []
        self.movesize_window_handle = None

    def _enumerate_windows(self):
        def _enum_windows_callback(window_hwnd, results):
            results.append(window_hwnd)

        windows = []
        win32gui.EnumWindows(_enum_windows_callback, windows)
        return windows

    def _should_track_window(self, hwnd):
        # TODO: why Photos not tracked?

        # check ignored classes
        try:
            classname = win32gui.GetClassName(hwnd)
        except:
            return False
        if classname in config.ignored_classnames():
            return False

        # check bad styling
        try:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        except:
            return False
        if not style & win32con.WS_MAXIMIZEBOX or style & win32con.WS_POPUP:
            return False
        
        # check visibility
        try:
            visible = win32gui.IsWindowVisible(hwnd)
            iconic = win32gui.IsIconic(hwnd)
            zoomed = ctypes.windll.user32.IsZoomed(hwnd)
        except:
            return False

        return visible and not iconic and not zoomed

    def _update_tracked_windows(self, _, dwmsEventTime):
        window_handles = list(filter(lambda hwnd: self._should_track_window(hwnd), self._enumerate_windows()))

        added_handles = [hwnd for hwnd in window_handles if hwnd not in self.tracked_window_handles]
        removed_handles = [hwnd for hwnd in self.tracked_window_handles if hwnd not in window_handles]

        self.tracked_window_handles = window_handles
        if len(added_handles) > 0 or len(removed_handles) > 0:
            self._refresh_windows()
            self._apply_strategy()

    def _on_location_change(self, hwnd, dwmsEventTime):
        if hwnd == self.movesize_window_handle:
            return

        window = self._get_tracked_window(hwnd)
        if window is None: return
        logging.debug(f"location_change: {window.pretty_title}")

        curr_display = None
        past_display = None
        for display in self.displays:
            if window in self.display_window_map[str(display.hwnd)]:
                past_display = display
            if display.contains_window(window.hwnd):
                curr_display = display

        if past_display is not None and curr_display != past_display:
            # changed displays
            self._apply_strategy_to_display(past_display)
            self._apply_strategy_to_display(curr_display)
        else:
            # same display, check movement
            size = win32gui.GetWindowRect(hwnd)
            if size != window.display_size:
                self._apply_strategy_to_display(curr_display)

    def _on_movesize_start(self, hwnd, dwmsEventTime):
        if hwnd not in self.tracked_window_handles:
            return

        # track dragged windows so we don't mess with them
        self.movesize_window_handle = hwnd
        self._apply_strategy_to_display_by_window_handle(hwnd)

    def _on_movesize_end(self, hwnd, dwmsEventTime):
        movesize_end_hwnd = self.movesize_window_handle
        self.movesize_window_handle = None

        window = self._get_tracked_window(movesize_end_hwnd)
        if window is None: return

        window.refresh()
        for display in self.displays:
            if display.contains_window(movesize_end_hwnd):
                self._apply_strategy_to_display(display)
                return

    def _refresh_windows(self):
        self.windows = [Window(hwnd) for hwnd in self.tracked_window_handles]

    def _get_tracked_window(self, hwnd):
        if hwnd not in self.tracked_window_handles:
            return None

        for w in self.windows:
            if w.hwnd == hwnd:
                return w
        return None

    def _get_foreground_window_handle(self):
        return win32gui.GetForegroundWindow()

    def _restore_original_window_size(self, hwnd):
        window = self._get_tracked_window(hwnd)
        if window is not None:
            window.restore_size()

    def _apply_strategy(self):
        self.displays = Display.enumerate()
        for display in self.displays:
            self._apply_strategy_to_display(display)

    def _apply_strategy_to_display(self, display):
        for w in self.windows:
            w.refresh()

        # capture windows for display
        display_windows = list(filter(lambda w: display.contains_window(w.hwnd), self.windows))
        self.display_window_map[str(display.hwnd)] = display_windows

        # apply strategy to windows
        strategy_windows = list(filter(lambda w: w.hwnd != self.movesize_window_handle, display_windows))
        logging.debug(f"Applying strategy to DISPLAY {display} ({len(strategy_windows)} window(s))")
        if len(display_windows) != len(strategy_windows):
            logging.debug(f"\tIgnoring dragged window [{self.movesize_window_handle}]")
        self.management_strategy.apply(display, strategy_windows, self._get_foreground_window_handle())

    def _apply_strategy_to_display_by_window_handle(self, hwnd):
        if hwnd not in self.tracked_window_handles:
            return

        for display in self.displays:
            handles = [w.hwnd for w in self.display_window_map[str(display.hwnd)]]
            if hwnd in handles:
                self._apply_strategy_to_display(display)
                return

    def _message_loop(self, user32, ole32):
        """Message loop that calls our event hooks"""
        hook = user32.SetWinEventHook(
            win32con.EVENT_MIN,
            win32con.EVENT_MAX,
            0,
            self.WinEventProc,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT)
        if hook == 0: raise RuntimeError("Failed SetWinEventHook")
        
        # message loop
        message = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), 0, 0, 0) != 0:
            user32.TranslateMessageW(message)
            user32.DispatchMessageW(message)

        # cleanup
        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()

    def refresh(self):
        self._refresh_windows()
        self._apply_strategy()

    def toggle_window_topmost(self, window):
        window.set_topmost(not window.topmost)
        self._apply_strategy_to_display_by_window_handle(window.hwnd)

    def dispose(self):
        logging.info("Disposing DisplayManager")

    def start_event_hook(self):
        """Sets up and starts a thread handling windows events"""
        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32

        ole32.CoInitialize(0)

        # setup callback
        MESSAGE_MAP = {
            win32con.EVENT_OBJECT_CREATE: self._update_tracked_windows,
            win32con.EVENT_OBJECT_LOCATIONCHANGE: self._on_location_change,
            win32con.EVENT_SYSTEM_MOVESIZESTART: self._on_movesize_start,
            win32con.EVENT_SYSTEM_MOVESIZEEND: self._on_movesize_end,
            win32con.EVENT_SYSTEM_MINIMIZESTART: self._update_tracked_windows,
            win32con.EVENT_SYSTEM_MINIMIZEEND: self._update_tracked_windows
        }
        # TODO: alternate strategies & events (e.g. focused window fills screen, others move to edge)
        # EVENT_SYSTEM_MOVESIZEEND when move / resize is completed
        # EVENT_SYSTEM_SWITCHEND when user releases alt + tab, hwnd is selected window
        # EVENT_SYSTEM_FOREGROUND when foreground window changes, hwnd is foreground window
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            func = MESSAGE_MAP.get(event)
            if func is not None and hwnd is not None:
                func(hwnd, dwmsEventTime)

        WinEventProcType = ctypes.WINFUNCTYPE(
            None,
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LONG,
            ctypes.wintypes.LONG,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD)
        self.WinEventProc = WinEventProcType(callback)

        # setup error handling
        def win_error(result, func, args):
            if not result: raise ctypes.WinError(ctypes.get_last_error())
            return args

        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        user32.SetWinEventHook.errcheck = win_error

        # start message loop
        self.thread = threading.Thread(target=self._message_loop, args=(user32, ole32))
        self.thread.start()

    def stop_event_hook(self):
        """Ends the thread running our message loop"""
        if self.thread is not None:
            ctypes.windll.user32.PostThreadMessageW(
                self.thread.ident, win32con.WM_QUIT, 0, 0)
            self.thread = None