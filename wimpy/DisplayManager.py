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
        
        self.tracked_window_handles = []

    def _enumerate_windows(self):
        def _enum_windows_callback(window_hwnd, results):
            results.append(window_hwnd)

        windows = []
        win32gui.EnumWindows(_enum_windows_callback, windows)
        return windows

    def _should_track_window(self, hwnd):
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
        if not style & win32con.WS_MAXIMIZEBOX:
            return False
        
        # check visibility
        try:
            visible = win32gui.IsWindowVisible(hwnd)
            iconic = win32gui.IsIconic(hwnd)
        except:
            return False

        return visible and not iconic

    def _update_tracked_windows(self, _, dwmsEventTime):
        window_handles = list(filter(lambda hwnd: self._should_track_window(hwnd), self._enumerate_windows()))

        added_handles = [hwnd for hwnd in window_handles if hwnd not in self.tracked_window_handles]
        removed_handles = [hwnd for hwnd in self.tracked_window_handles if hwnd not in window_handles]

        self.tracked_window_handles = window_handles
        if len(added_handles) > 0 or len(removed_handles) > 0:
            logging.debug(f"Adding {len(added_handles)} handle(s), removing {len(removed_handles)} handle(s).")
            self._apply_strategy()

    def _apply_strategy(self):
        displays = Display.enumerate()
        windows = [Window(hwnd) for hwnd in self.tracked_window_handles]

        logging.debug(f"Applying strategy to {len(displays)} display(s), {len(windows)} window(s).")
        self.management_strategy.apply(displays, windows)

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
        self._apply_strategy()

    def start_event_hook(self):
        """Sets up and starts a thread handling windows events"""
        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32

        ole32.CoInitialize(0)

        # setup callback
        MESSAGE_MAP = {
            win32con.EVENT_OBJECT_CREATE: self._update_tracked_windows,
            win32con.EVENT_OBJECT_LOCATIONCHANGE: self._update_tracked_windows,
            win32con.EVENT_SYSTEM_MINIMIZESTART: self._update_tracked_windows,
            win32con.EVENT_SYSTEM_MINIMIZEEND: self._update_tracked_windows,
            win32con.EVENT_OBJECT_HIDE: self._update_tracked_windows,
        }
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