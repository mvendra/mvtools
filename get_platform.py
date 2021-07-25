#!/usr/bin/env python3

import platform

PLAT_LINUX = "linux"
PLAT_WINDOWS = "windows"
PLAT_CYGWIN = "cygwin"
PLAT_MACOSX = "macosx"
PLAT_UNKNOWN = "unknown_platform"

ARCH_64 = "x64"
ARCH_32 = "x32"
ARCH_UNKNOWN = "unknown_arch"

def getplat():
    ps = platform.system().lower()
    if ps == "linux":
        return PLAT_LINUX
    elif ps == "windows":
        return PLAT_WINDOWS
    elif "cygwin_nt-10" in ps:
        return PLAT_CYGWIN
    elif ps == "darwin":
        return PLAT_MACOSX
    return PLAT_UNKNOWN

def getarch():
    pm = platform.machine().lower()
    if pm == "x86_64":
        return ARCH_64
    elif pm == "amd64":
        return ARCH_64
    elif pm == "i686":
        return ARCH_32
    else:
        return ARCH_UNKNOWN

if __name__ == "__main__":
    print("%s %s" % (getplat(), getarch()))
