import os
from cx_Freeze import setup, Executable

base = "Win32GUI"

executables = [Executable(
    script="main.py",
    targetName="wimpy.exe",
    base=base,
    icon=os.path.join("icon", "icon.ico")
)]
packages = []
options = {
    "build_exe": {
        "packages": packages,
        "include_files": ["icon", "config.ini"]
    },
}

setup(
    name="wimpy",
    options=options,
    version="0.8.0",
    description="window manager in python",
    executables=executables
)
