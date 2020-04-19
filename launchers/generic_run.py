#!/usr/bin/env python3

import sys
import os
import subprocess

class run_cmd_result:
    def __init__(self, _success, _returncode, _stdout, _stderr):
        self.success = _success
        self.returncode = _returncode
        self.stdout = _stdout
        self.stderr = _stderr

def run_cmd(cmd_list, use_input=None, use_cwd=None, use_env=None, use_encoding="utf8"):

    # return format: bool, string, run_cmd_result
    # the first (bool) is the return of this API call only
    # the second (string) is a message about the API call only
    # the third (run_cmd_result) is the result of the called command itself

    if not isinstance(cmd_list, list):
        return False, "[%s] is not a list" % cmd_list, None
    if len(cmd_list) == 0:
        return False, "Nothing to run", None

    try:
        process = subprocess.run(cmd_list, input=use_input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=use_cwd, check=False, encoding=use_encoding, env=use_env)
        return True, "OK", run_cmd_result( (process.returncode==0), process.returncode, process.stdout, process.stderr )
    except Exception as ex:
        return False, str(ex), None
    return False, "run_cmd NOTREACHED", None

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
