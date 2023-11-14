#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def build(exec_path, config, target):

    if exec_path is None:
        return False, "Invalid execution path"

    full_cmd = ["bazel"]
    full_cmd.append("build")

    if config is not None:
        full_cmd.append("--config=%s" % config)

    if target is not None:
        full_cmd.append(target)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def fetch(exec_path, target):

    if exec_path is None:
        return False, "Invalid execution path"

    full_cmd = ["bazel"]
    full_cmd.append("fetch")

    if target is not None:
        full_cmd.append(target)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def clean(exec_path, expunge):

    if exec_path is None:
        return False, "Invalid execution path"

    full_cmd = ["bazel"]
    full_cmd.append("clean")

    if expunge:
        full_cmd.append("--expunge")

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def test(exec_path, config, target):

    if exec_path is None:
        return False, "Invalid execution path"

    full_cmd = ["bazel"]
    full_cmd.append("test")

    if config is not None:
        full_cmd.append("--config=%s" % config)

    if target is not None:
        full_cmd.append(target)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, r
    return True, (r.success, r.stdout, r.stderr)

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
