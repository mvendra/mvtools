#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def build(exec_path, jobs, config, target, options):

    if exec_path is None:
        return False, "Invalid execution path"

    if target is not None and not isinstance(target, str):
        return False, "target must be a string"

    full_cmd = ["bazel"]
    full_cmd.append("build")

    if jobs is not None:
        full_cmd.append("--jobs=%s" % jobs)

    if config is not None:
        full_cmd.append("--config=%s" % config)

    if target is not None:
        full_cmd.append(target)

    for opt in options:
        full_cmd.append(opt)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, "Failed running bazel build command: [%s]" % r
    return True, (r.success, r.stdout, r.stderr)

def fetch(exec_path, target):

    if exec_path is None:
        return False, "Invalid execution path"

    if target is not None and not isinstance(target, str):
        return False, "target must be a string"

    full_cmd = ["bazel"]
    full_cmd.append("fetch")

    if target is not None:
        full_cmd.append(target)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, "Failed running bazel fetch command: [%s]" % r
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
        return False, "Failed running bazel clean command: [%s]" % r
    return True, (r.success, r.stdout, r.stderr)

def run(exec_path, target, args):

    if exec_path is None:
        return False, "Invalid execution path"

    if target is not None and not isinstance(target, str):
        return False, "target must be a string"

    if not isinstance(args, list):
        return False, "args must be a list"

    full_cmd = ["bazel"]
    full_cmd.append("run")

    if target is not None:
        full_cmd.append(target)

    if len(args) > 0:
        full_cmd.append("--")
        for a in args:
            full_cmd.append(a)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, "Failed running bazel run command: [%s]" % r
    return True, (r.success, r.stdout, r.stderr)

def test(exec_path, jobs, config, target, options):

    if exec_path is None:
        return False, "Invalid execution path"

    if target is not None and not isinstance(target, str):
        return False, "target must be a string"

    full_cmd = ["bazel"]
    full_cmd.append("test")

    if jobs is not None:
        full_cmd.append("--jobs=%s" % jobs)

    if config is not None:
        full_cmd.append("--config=%s" % config)

    if target is not None:
        full_cmd.append(target)

    for opt in options:
        full_cmd.append(opt)

    v, r = generic_run.run_cmd(full_cmd, use_cwd=exec_path)
    if not v:
        return False, "Failed running bazel test command: [%s]" % r
    return True, (r.success, r.stdout, r.stderr)

def puaq(selfhelp):
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    puaq(False)
