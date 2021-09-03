import os
import wx
import wx.adv


class WimpyTaskBarIcon(wx.adv.TaskBarIcon):
    """TaskBarIcon for wimpy"""

    def __init__(self, program_name, icon_path, window_manager):
        super(wx.adv.TaskBarIcon, self).__init__()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self._refresh)

        self.program_name = program_name
        self.window_manager = window_manager
        self._set_icon(icon_path, self.program_name)

        self.window_mapping = {}

    def CreatePopupMenu(self):
        """Creates the right-click menu for the TaskBarIcon."""
        menu = wx.Menu()

        # label
        label_item = menu.Append(wx.NewIdRef(), "wimpy")
        label_item.Enable(False)

        menu.AppendSeparator()

        # refresh
        refresh_item = menu.Append(wx.NewIdRef(), "Refresh")
        self.Bind(wx.EVT_MENU, self._refresh, refresh_item)

        menu.AppendSeparator()

        # window toggles
        for window in self.window_manager.windows:
            raw_label = str(window)
            label = raw_label if len(
                raw_label) < 42 else raw_label[:39] + "..."
            window_item = menu.AppendCheckItem(wx.NewIdRef(), label)
            window_item.Check(window.topmost)
            self.Bind(wx.EVT_MENU, self._on_window_click,
                      id=window_item.GetId())
            self.window_mapping[window_item.GetId()] = window

        menu.AppendSeparator()

        # exit
        exit_item = menu.Append(wx.NewIdRef(), "Exit")
        self.Bind(wx.EVT_MENU, self._exit, exit_item)

        return menu

    def _set_icon(self, path, tooltip):
        icon = wx.Icon()
        icon.LoadFile(path)
        self.SetIcon(icon, tooltip)

    def _show_toast_notification(self, message):
        self.ShowBalloon(self.program_name, message)

    def _refresh(self, event):
        self.window_manager.refresh()

    def _exit(self, event):
        self.window_manager.restore_positions()
        wx.CallAfter(self.Destroy)
        wx.Exit()

    def _on_window_click(self, event):
        window = self.window_mapping[event.GetId()]
        self.window_manager.toggle_window_topmost(window)
