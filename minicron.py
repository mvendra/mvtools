#!/usr/bin/env python3

import sys
import os

import time

def convert_time_string(time_string):

    # returns time_string in *seconds*
    # examples:
    # 7h (seven hours)
    # 30m (thirty minutes)
    # 15s *fifteen seconds)

    if not isinstance(time_string, str):
        return None

    if time_string is None:
        return None

    if len(time_string) < 2:
        return None

    unit_conv = {"h": 60*60, "m": 60, "s": 1}

    unit = time_string[len(time_string)-1]
    number = time_string[0:len(time_string)-1]

    if not unit in unit_conv:
        return None

    return int(number) * unit_conv[unit]

def busy_wait(duration):

    if duration is None:
        return None
    if not isinstance(duration, int):
        return None
    if duration < 1:
        return None

    time.sleep(duration)

    return True

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
