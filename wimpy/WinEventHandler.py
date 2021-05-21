import ctypes
import logging
import threading
import win32con

class WinEventHandler(object):
    """description of class"""

    def __init__(self):
        pass

    def start_hook(self, callback, err_callback):
        """sets up Windows event hook and message loop"""
        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32

        ole32.CoInitialize(0)

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

        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE
        user32.SetWinEventHook.errcheck = err_callback

        self.thread = threading.Thread(target=self._message_loop, args=(user32, ole32))
        logging.debug(f"Starting message loop thread ({self.thread}).")
        self.thread.start()

    def stop_hook(self):
        """ends Windows event hook thread"""
        if self.thread is not None:
            logging.debug("Stopping message loop")
            ctypes.windll.user32.PostThreadMessageW(self.thread.ident, win32con.WM_QUIT, 0, 0)
            self.thread = None

    def _message_loop(self, user32, ole32):
        """message loop to dispatch events"""
        hook = user32.SetWinEventHook(
            win32con.EVENT_MIN,
            win32con.EVENT_MAX,
            0,
            self.WinEventProc,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT)
        if hook == 0: raise RuntimeError("Failed to set hook!")

        # message loop
        message = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), 0, 0, 0) != 0:
            user32.TranslateMessageW(message)
            user32.DispatchMessageW(message)

        # cleanup
        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()