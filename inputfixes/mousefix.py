#!/usr/bin/env python

import os
import sys

import subprocess
import re
from subprocess import call

"""
mousefix tool
this tries to automatically do the equivalent of the following:
xinput --list
xinput --list-props DEVICE_ID
xinput set-prop DEVICE_ID "Device Accel Profile" -1
"""

def getidfromxinputstring(theline):
    """returns None if it cant find matches in the given line"""

    m = re.search("id=[0-9]+", theline)
    if m is None:
        return None # incorrect parameters. forget it.

    m = re.search("[0-9]+", m.group(0))
    if m is None:
        return None
    else:
        return m.group(0)

def getidfromdapstring(theline):
    """returns None if it cant find matches in the given line"""

    m = re.search("Device Accel Profile \([0-9]+\)", theline, re.IGNORECASE)
    if m is None:
        return None # incorrect parameters. forget it.

    m = re.search("[0-9]+", m.group(0))
    if m is None:
        return None
    else:
        return m.group(0)

def hascandidateinxinputstring(theline, candidate):
    """returns boolean"""

    if theline.lower().find(candidate.lower()) > 0:
        return True
    else:
        return False

def getdeviceaccelprofilefromid(mid):
    """returns None if cant find DAP"""
    xinput_listprops_ret = os.popen("xinput --list-props %s" % mid).read().strip()
    xlp_list = xinput_listprops_ret.split('\n')
    for pc in xlp_list: # pc = props candidate
        if hascandidateinxinputstring(pc, "Device Accel Profile"):
            dap = getidfromdapstring(pc)
            return dap
    return None

# mid = mouse id, dap = device accel profile
def applymousefix(mid, dap):
    call(["xinput", "set-prop", mid, dap, "-1"])

def detect_and_apply():
    mouse_detection = ["mouse", "touchpad", "DeathAdder"]

    call(["xset", "m", "0", "0"])

    xinput_ret = os.popen("xinput --list").read().strip()
    xr_list = xinput_ret.split('\n')
    for mc in xr_list: # mc = mouse candidate
        for md in mouse_detection: # md = mouse detection
            if hascandidateinxinputstring(mc, md):
                mouse_id = getidfromxinputstring(mc)
                dap = getdeviceaccelprofilefromid(mouse_id)
                if dap is not None:
                    applymousefix(mouse_id, dap)
                else:
                    print("%s: WARNING: detected mouse, but could not detect Device Accel Profile!" % os.path.basename(__file__))
                    return False

    return True

if __name__ == "__main__":

    # mvtodo: interactive completion for half detections - and similar? (i remember plugging in a wireless mouse once, and it wasnt detected as mouse anywhere, more like a Logitech Hub/Consolidated Generic thingy of sorts)
    # mvtodo: add --verbose option that prints everything it detects

    if (len(sys.argv) == 1):
        detect_and_apply()
    else:
        print("Parameterisation/partial/complementary detection not implemented.") # mvtodo: implement full/partial parameterisation plus full/partial(complementary) detection

