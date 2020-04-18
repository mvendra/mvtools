#!/usr/bin/env python3

import sys
import os
import subprocess

def run_cmd_l(cmd_list, std_input=None, use_cwd=None, use_encoding="utf8"):
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
