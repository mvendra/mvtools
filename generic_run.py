#!/usr/bin/env python3

import sys
import os
import subprocess

def run_cmd_l(cmd_list):
    try:
        process = subprocess.run(cmd_list, check=True, stdout=subprocess.PIPE)
        if process.returncode == 0:
            return True
    except:
        pass
    return False

def run_cmd(cmd):
    cmd_list = []
    cmd_list_pre = cmd.strip().split(" ")
    for x in cmd_list_pre:
        xl = x.strip()
        if len(xl) > 0:
            cmd_list.append(xl)

    return run_cmd_l(cmd_list)
