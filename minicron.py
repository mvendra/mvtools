#!/usr/bin/env python

import sys
import os

import path_utils
import time

UNIT_CONV = {"h": 60*60, "m": 60, "s": 1}

def convert_single_part(part_string):

    # returns time_string in *seconds*
    # examples:
    # 7h (seven hours)
    # 30m (thirty minutes)
    # 15s *fifteen seconds)

    if part_string is None:
        return None
    if not isinstance(part_string, str):
        return None
    if len(part_string) < 2:
        return None

    unit = part_string[len(part_string)-1]
    number = part_string[0:len(part_string)-1]

    if not unit in UNIT_CONV:
        return None

    return int(number) * UNIT_CONV[unit]

def convert_time_string(time_string):

    if time_string is None:
        return None
    if not isinstance(time_string, str):
        return None
    if len(time_string) < 2:
        return None

    total_seconds = 0

    current_part = ""
    for c in time_string:
        current_part += c
        if c in UNIT_CONV:
            latest_seconds = convert_single_part(current_part)
            if latest_seconds is None:
                return None
            total_seconds += latest_seconds
            current_part = ""

    if current_part != "":
        return None # leftovers
    return total_seconds

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
    print("Hello from %s" % path_utils.basename_filtered(__file__))
