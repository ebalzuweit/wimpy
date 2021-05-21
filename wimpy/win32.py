import logging
import pywintypes
import win32api
import win32con
import win32gui

def EnumDisplayMonitors():
    hwnds = []
    for hwnd, _, _ in win32api.EnumDisplayMonitors():
        hwnds.append(hwnd)

    return hwnds

def EnumWindows():
    def _cb(hwnd, handles):
        handles.append(hwnd)

    hwnds = []
    win32gui.EnumWindows(_cb, hwnds)
    return hwnds

def GetForegroundWindow():
    return win32gui.GetForegroundWindow()

def GetWindowExStyles(hwnd):
    return win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

def GetWindowClassName(hwnd):
    return win32gui.GetClassName(hwnd)

def GetWindowRect(hwnd):
    return win32gui.GetWindowRect(hwnd)

def GetWindowStyles(hwnd):
    return win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

def GetWindowText(hwnd):
    return win32gui.GetWindowText(hwnd)

def IsIconic(hwnd):
    return win32gui.IsIconic(hwnd)

def IsWindowVisible(hwnd):
    return win32gui.IsWindowVisible(hwnd)

def MoveWindow(hwnd, x, y, cx, cy, repaint):
    try:
        return win32gui.MoveWindow(hwnd, x, y, cx, cy, repaint)
    except pywintypes.error as err:
        winerr, funcname, message = err.args
        logging.error(f"{funcname} ({winerr}): {message}")

def SetWindowPos(hwnd, hwnd_insert_after, x, y, cx, cy, u_flags):
    return win32gui.SetWindowPos(hwnd, hwnd_insert_after, x, y, cx, cy, u_flags)