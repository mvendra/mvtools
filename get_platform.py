#!/usr/bin/env python

import platform

PLAT_LINUX = "linux"
PLAT_WINDOWS = "windows"
PLAT_CYGWIN = "cygwin"
PLAT_MSYS = "msys"
PLAT_MINGW = "mingw"
PLAT_MACOS = "macos"
PLAT_UNKNOWN = "unknown_platform"

def getplat():
    ps = platform.system().lower()
    if ps == "linux":
        return PLAT_LINUX
    elif ps == "windows":
        return PLAT_WINDOWS
    elif "cygwin_nt" in ps:
        return PLAT_CYGWIN
    elif "msys_nt" in ps:
        return PLAT_MSYS
    elif "mingw64_nt" in ps:
        return PLAT_MINGW
    elif ps == "darwin":
        return PLAT_MACOS
    return PLAT_UNKNOWN

if __name__ == "__main__":
    print("%s" % (getplat()))
