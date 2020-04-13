#!/usr/bin/env python3

import sys
import os
import subprocess

def run_cmd_l(cmd_list, std_input=None, use_cwd=None, use_encoding="ascii"):
    try:
        if std_input is not None:

            if use_cwd is not None:
                process = subprocess.run(cmd_list, check=False, input=std_input, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=use_cwd, encoding=use_encoding)
            else:
                process = subprocess.run(cmd_list, check=False, input=std_input, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding=use_encoding)

        else:

            if use_cwd is not None:
                process = subprocess.run(cmd_list, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=use_cwd, encoding=use_encoding)
            else:
                process = subprocess.run(cmd_list, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding=use_encoding)

        if process.returncode == 0:
            return True, process.stdout
    except:
        pass
    return False, None

def run_cmd_l_asc(cmd_list, std_input=None):
    return run_cmd_l(cmd_list, std_input, None, "ascii")

def run_cmd_l_utf8(cmd_list, std_input=None):
    return run_cmd_l(cmd_list, std_input, None, "utf8")

def run_cmd(cmd, std_input=None, use_encoding="ascii"):
    cmd_list = []
    cmd_list_pre = cmd.strip().split(" ")
    for x in cmd_list_pre:
        xl = x.strip()
        if len(xl) > 0:
            cmd_list.append(xl)

    return run_cmd_l(cmd_list, std_input, None, use_encoding)

def run_cmd_asc(cmd, std_input=None):
    return run_cmd(cmd, std_input, "ascii")

def run_cmd_utf8(cmd, std_input=None):
    return run_cmd(cmd, std_input, "utf8")
