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

def run_cmd(cmd_list, use_input=None, use_shell=False, use_cwd=None, use_env=None, use_encoding="utf8", use_errors="ignore", use_timeout=None):

    # return format: bool, (string | run_cmd_result)
    # the first (bool) is the return of this API call only
    # if the API call failed (first bool == False), then the second parameter is an error message
    # if the API call succeeded (first bool == True), then the second parameter is a run_cmd_result object with details about the process execution

    if not isinstance(cmd_list, list):
        return False, "[%s] is not a list" % cmd_list
    if len(cmd_list) == 0:
        return False, "Nothing to run"

    try:
        process = subprocess.run(cmd_list, input=use_input, capture_output=True, shell=use_shell, cwd=use_cwd, check=False, encoding=use_encoding, errors=use_errors, env=use_env, timeout=use_timeout)
        return True, run_cmd_result( (process.returncode==0), process.returncode, process.stdout, process.stderr )
    except Exception as ex:
        return False, str(ex)
    return False, "run_cmd NOTREACHED"

def run_cmd_simple(cmd_list, suppress_stderr=False, use_input=None, use_shell=False, use_cwd=None, use_env=None, use_encoding="utf8", use_errors="ignore", use_timeout=None):

    # return format: bool, string
    # the first (bool) returns true is everything ran fine, false if anything at all went wrong
    # the second (string) returns stdout if the command ran fine, or an error message if anything went wrong

    v, r = run_cmd(cmd_list, use_input, use_shell, use_cwd, use_env, use_encoding, use_errors, use_timeout)

    if not v:
        return False, "Failed running command: %s" % r

    if not r.success:
        return False, "Failed running command: %s" % r.stderr

    if len(r.stderr) > 0 and not suppress_stderr:
        print(r.stderr, end="")
    return True, r.stdout
