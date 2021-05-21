import logging
import os
import sys
import wx

import wimpy.config as config

from wimpy.WimpyTaskBarIcon import WimpyTaskBarIcon
from wimpy.BSPTilingStrategy import BSPTilingStrategy
from wimpy.WinEventHandler import WinEventHandler
from wimpy.WindowManager import WindowManager
from wimpy.DisplayManager import DisplayManager

PROGRAM_NAME = "wimpy"
TRAY_ICON_PATH = os.path.join(os.getcwd(), "icon", "icon.ico")
CONFIG_FILENAME = "config.ini"

def configure():
	logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")
	config.load_file(CONFIG_FILENAME)

def main():
	configure()

	strategy = BSPTilingStrategy()
	window_manager = WindowManager(strategy)
	event_handler = WinEventHandler()

	app = wx.App()
	taskbar = WimpyTaskBarIcon(PROGRAM_NAME, TRAY_ICON_PATH, window_manager)
	event_handler.start_hook(window_manager.on_event, window_manager.on_error)
	app.MainLoop()
	event_handler.stop_hook()
	sys.exit(0)

if __name__ == "__main__":
	main()
