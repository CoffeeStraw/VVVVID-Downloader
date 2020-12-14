"""
VVVVID Downloader - Utility Functions
Author: CoffeeStraw
GitHub: https://github.com/CoffeeStraw/VVVVID-Downloader
"""
from platform import system
from re import sub as re_sub


def os_fix_filename(filename):
    """Alter filenames containing illegal characters, depending on the OS.

    Ref: https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names/31976060#31976060
    """
    if system() == "Windows":
        return re_sub(r"[\<\>\:\"\/\\\|\?\*]+", "", filename)
    return re_sub(r"[\/]+", r"\\", filename)
