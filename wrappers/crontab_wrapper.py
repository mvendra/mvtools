#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def get_crontab():

    ct_cmd = ["crontab", "-l"]
    v, r = generic_run.run_cmd_l_asc(ct_cmd)
    return v, r

if __name__ == "__main__":

    v, r = get_crontab()
    if v:
        print(r)
    else:
        print("Failed calling 'crontab'")
        sys.exit(1)
