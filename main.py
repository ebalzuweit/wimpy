import argparse
import logging
import os
import sys
import wx

import wimpy.config as config

from wimpy.WimpyTaskBarIcon import WimpyTaskBarIcon
from wimpy.WindowManagementStrategy import WindowManagementStrategy
from wimpy.BSPTilingStrategy import BSPTilingStrategy
from wimpy.WinEventHandler import WinEventHandler
from wimpy.WindowManager import WindowManager

PROGRAM_NAME = "wimpy"
TRAY_ICON_PATH = os.path.join(os.getcwd(), "icon", "icon.ico")
CONFIG_FILENAME = "config.ini"
LOG_FILENAME = "log.txt"


def configure():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        handlers=[
                            logging.StreamHandler(sys.stdout),
                            logging.FileHandler(LOG_FILENAME, encoding="utf-8")
                        ])
    config.load_file(CONFIG_FILENAME)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", "--debug", action="store_true",
                           help="Disables window management for debugging purposes.")
    args = argparser.parse_args()

    configure()

    strategy = BSPTilingStrategy()
    if args.debug:
        strategy = WindowManagementStrategy()
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
