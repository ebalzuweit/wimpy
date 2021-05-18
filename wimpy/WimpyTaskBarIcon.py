import os
import wx
import wx.adv

class WimpyTaskBarIcon(wx.adv.TaskBarIcon):
    """TaskBarIcon for wimpy"""

    def __init__(self, program_name, icon_path, display_manager):
        super(wx.adv.TaskBarIcon, self).__init__()
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self._refresh)

        self.program_name = program_name
        self.display_manager = display_manager
        self._set_icon(icon_path, self.program_name)

    def CreatePopupMenu(self):
        """Creates the right-click menu for the TaskBarIcon."""
        menu = wx.Menu()

        # refresh
        refresh_item = menu.Append(wx.NewIdRef(), "Refresh")
        self.Bind(wx.EVT_MENU, self._refresh, refresh_item)
        
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
        self.display_manager.refresh()
        self._show_toast_notification("Refreshed!")

    def _exit(self, event):
        wx.CallAfter(self.Destroy)
        wx.Exit()
