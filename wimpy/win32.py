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


def GetWindowClassName(hwnd):
    return win32gui.GetClassName(hwnd)


def GetWindowRect(hwnd):
    return win32gui.GetWindowRect(hwnd)


def GetWindowStyles(hwnd):
    return win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)


def GetWindowExStyles(hwnd):
    return win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)


def GetWindowStyleMap(hwnd):
    styles = GetWindowStyles(hwnd)
    ex_styles = GetWindowExStyles(hwnd)

    style_map = {}

    def _append_style(label, style_constant):
        style_map[label] = bool(styles & style_constant)

    def _append_exstyle(label, exstyle_constant):
        style_map[label] = bool(ex_styles & exstyle_constant)

    # styles
    # https://docs.microsoft.com/en-us/windows/win32/winmsg/window-styles
    _append_style("border", win32con.WS_BORDER)
    _append_style("caption", win32con.WS_CAPTION)
    _append_style("child", win32con.WS_CHILD)
    _append_style("child_window", win32con.WS_CHILDWINDOW)
    _append_style("clip_children", win32con.WS_CLIPCHILDREN)
    _append_style("clip_siblings", win32con.WS_CLIPSIBLINGS)
    _append_style("disabled", win32con.WS_DISABLED)
    _append_style("dlg_frame", win32con.WS_DLGFRAME)
    _append_style("group", win32con.WS_GROUP)
    _append_style("h_scroll", win32con.WS_HSCROLL)
    _append_style("iconic", win32con.WS_ICONIC)
    _append_style("maximize", win32con.WS_MAXIMIZE)
    _append_style("maximize_box", win32con.WS_MAXIMIZEBOX)
    _append_style("minimize", win32con.WS_MINIMIZE)
    _append_style("minimize_box", win32con.WS_MINIMIZEBOX)
    _append_style("overlapped", win32con.WS_OVERLAPPED)
    _append_style("overlapped_window", win32con.WS_OVERLAPPEDWINDOW)
    _append_style("popup", win32con.WS_POPUP)
    _append_style("popup_window", win32con.WS_POPUPWINDOW)
    _append_style("size_box", win32con.WS_SIZEBOX)
    _append_style("sys_menu", win32con.WS_SYSMENU)
    _append_style("tab_stop", win32con.WS_TABSTOP)
    _append_style("thick_frame", win32con.WS_THICKFRAME)
    _append_style("tiled", win32con.WS_TILED)
    _append_style("tiled_window", win32con.WS_TILEDWINDOW)
    _append_style("visible", win32con.WS_VISIBLE)
    _append_style("v_scroll", win32con.WS_VSCROLL)

    # extended styles
    # https://docs.microsoft.com/en-us/windows/win32/winmsg/extended-window-styles
    _append_exstyle("accept_files", win32con.WS_EX_ACCEPTFILES)
    _append_exstyle("app_window", win32con.WS_EX_APPWINDOW)
    _append_exstyle("client_edge", win32con.WS_EX_CLIENTEDGE)
    _append_exstyle("composited", win32con.WS_EX_COMPOSITED)
    _append_exstyle("context_help", win32con.WS_EX_CONTEXTHELP)
    _append_exstyle("control_parent", win32con.WS_EX_CONTROLPARENT)
    _append_exstyle("dlg_modal_frame", win32con.WS_EX_DLGMODALFRAME)
    _append_exstyle("layered", win32con.WS_EX_LAYERED)
    _append_exstyle("layout_rtl", win32con.WS_EX_LAYOUTRTL)
    _append_exstyle("left", win32con.WS_EX_LEFT)
    _append_exstyle("left_scrollbar", win32con.WS_EX_LEFTSCROLLBAR)
    _append_exstyle("ltr_reading", win32con.WS_EX_LTRREADING)
    _append_exstyle("mdi_child", win32con.WS_EX_MDICHILD)
    _append_exstyle("no_activate", win32con.WS_EX_NOACTIVATE)
    _append_exstyle("no_inherit_layout", win32con.WS_EX_NOINHERITLAYOUT)
    _append_exstyle("no_parent_notify", win32con.WS_EX_NOPARENTNOTIFY)
    _append_exstyle("overlapped_window", win32con.WS_EX_OVERLAPPEDWINDOW)
    _append_exstyle("palette_window", win32con.WS_EX_PALETTEWINDOW)
    _append_exstyle("right", win32con.WS_EX_RIGHT)
    _append_exstyle("right_scrollbar", win32con.WS_EX_RIGHTSCROLLBAR)
    _append_exstyle("rtl_reading", win32con.WS_EX_RTLREADING)
    _append_exstyle("static_edge", win32con.WS_EX_STATICEDGE)
    _append_exstyle("tool_window", win32con.WS_EX_TOOLWINDOW)
    _append_exstyle("topmost", win32con.WS_EX_TOPMOST)
    _append_exstyle("transparent", win32con.WS_EX_TRANSPARENT)
    _append_exstyle("window_edge", win32con.WS_EX_WINDOWEDGE)

    return style_map


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
