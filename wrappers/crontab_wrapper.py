#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def get_crontab():

    v, r = generic_run.run_cmd_simple(["crontab", "-l"])
    if not v:
        return False, "Failed running crontab command: [%s]" % r

    return True, r

if __name__ == "__main__":

    v, r = get_crontab()
    if v:
        print(r)
    else:
        print("Failed calling 'crontab'")
        sys.exit(1)
