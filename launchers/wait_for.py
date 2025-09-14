#!/usr/bin/env python

import sys
import os

import path_utils
import minicron

def wait_for(time_delay_string):

    wait_duration = minicron.convert_time_string(time_delay_string)
    if wait_duration is None:
        return False, "Invalid time duration: [%s]" % time_delay_string

    if not minicron.busy_wait(wait_duration):
        return False, "Requested delay of [%s] failed to be performed." % (time_delay_string)

    return True, None

def puaq(selfhelp):
    print("Usage: %s time_delay_string" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        puaq(False)

    time_delay_string = sys.argv[1]
    v, r = wait_for(time_delay_string)
    if not v:
        print(r)
    else:
        print("Done")
