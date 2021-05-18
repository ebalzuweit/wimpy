import logging
import os
import sys
import wx

import wimpy.config as config

from wimpy.WimpyTaskBarIcon import WimpyTaskBarIcon
from wimpy.BSPTilingStrategy import BSPTilingStrategy
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
	display_manager = DisplayManager(strategy)

	app = wx.App()
	taskbar = WimpyTaskBarIcon(PROGRAM_NAME, TRAY_ICON_PATH, display_manager)
	display_manager.start_event_hook()
	app.MainLoop()
	display_manager.stop_event_hook()
	sys.exit(0)

if __name__ == "__main__":
	main()
