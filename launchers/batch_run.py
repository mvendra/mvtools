#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run
import maketimestamp
import toolbus

# mvtodo: print out reminder: to stop this, send a toolbus signal such-and-such (variable per run -> only applicable for --run-until-fail)

def _stop_fail(stop_arg, proc_success, num_execs):
    return not proc_success

def _stop_count(stop_arg, proc_success, num_execs):
    return (num_execs == stop_arg)

def _save_iter(cmd, output_path, num, stdout, stderr):

    tg_name = path_utils.basename_filtered(cmd[0])

    iter_out_fn = "%s_stdout_%s.txt" % (tg_name, str(num))
    iter_err_fn = "%s_stderr_%s.txt" % (tg_name, str(num))

    iter_out_full = path_utils.concat_path(output_path, iter_out_fn)
    iter_err_full = path_utils.concat_path(output_path, iter_err_fn)

    with open(iter_out_full, "w") as f:
        f.write(stdout)

    with open(iter_err_full, "w") as f:
        f.write(stderr)

def _save_summary(cmd, output_path, num_total, num_failed, start_time):

    tg_name = path_utils.basename_filtered(cmd[0])
    sm_name = "%s_summary.txt" % tg_name
    sm_full = path_utils.concat_path(output_path, sm_name)

    sep_filler = ""
    for c in tg_name:
        sep_filler += "-"

    contents = ""
    contents += "Run of [%s] - summary:\n" % tg_name
    contents += "--------%s------------\n\n" % sep_filler
    contents += "Number of total executions: [%s]\n" % str(num_total)
    contents += "Number of failed executions: [%s]\n" % str(num_failed)
    contents += "Started time: [%s]\n" % start_time
    contents += "End time: [%s]\n" % maketimestamp.get_timestamp_now()

    with open(sm_full, "w") as f:
        f.write(contents)

def _run_until(cmd, output_path, op_mode_arg, save_mode, start_time, stop_callback):

    num_execs = 0
    num_failed = 0
    while (True):
        num_execs += 1

        v, r = generic_run.run_cmd(cmd)
        if not v:
            return False, r
        proc = r

        stdout = proc.stdout
        stderr = proc.stderr

        if save_mode == "save-all":
            _save_iter(cmd, output_path, num_execs, stdout, stderr)

        if not proc.success:

            num_failed += 1

            if save_mode == "save-fail":
                _save_iter(cmd, output_path, num_execs, stdout, stderr)

        if stop_callback(op_mode_arg, proc.success, num_execs):
            break

    _save_summary(cmd, output_path, num_execs, num_failed, start_time)

    return True, None

def batch_run(run_target, output_path, op_mode, op_mode_arg, save_mode, target_param_list):

    if not os.path.exists(run_target):
        return False, "Target [%s] does not exist." % run_target

    if os.path.exists(output_path):
        return False, "Output path [%s] already exists." % output_path

    if not path_utils.guaranteefolder(output_path):
        return False, "Unable to create folder [%s]." % output_path

    cmd = [os.path.abspath(run_target)]
    for p in target_param_list:
        cmd.append(p)

    start_time = maketimestamp.get_timestamp_now()
    stop_cb = None

    # run until fail
    if op_mode == "until-fail":
        stop_cb = _stop_fail

    # run until iteration count
    elif op_mode == "until-num":
        stop_cb = _stop_count

    else:
        return False, "Operation mode [%s] is invalid." % op_mode

    v, r = _run_until(cmd, output_path, op_mode_arg, save_mode, start_time, stop_cb)
    if not v:
        return False, r
    return True, None

def puaq():
    print("Usage: %s [--help] run_target output_path [--run-until-fail (default) | --run-until-num X | --run-until-signal X] [--save-fail (default) | --save-all] -- [target-param-list]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    params = sys.argv[3:]

    if "--help" in params:
        puaq()
        sys.exit(0)

    # decl
    target = None
    output_path = None
    op_mode = None
    op_mode_arg = None
    op_mode_arg_next = False
    save_mode = None
    parsing_target_param_list = False
    target_param_list = []

    # mandatory
    run_target = sys.argv[1]
    output_path = sys.argv[2]

    # defaults
    op_mode = "until-fail"
    save_mode = "save-fail"

    for p in params:

        if parsing_target_param_list:
            target_param_list.append(p)
            continue

        if op_mode_arg_next:
            op_mode_arg = p
            op_mode_arg_next = False
            continue

        if p == "--run-until-fail":
            op_mode = "until-fail"
        elif p == "--run-until-num":
            op_mode = "until-num"
            op_mode_arg_next = True
        elif p == "--run-until-signal":
            op_mode = "until-sig"
            op_mode_arg_next = True
        elif p == "--save-fail":
            save_mode = "save-fail"
        elif p == "--save-all":
            save_mode = "save-all"
        elif p == "--":
            parsing_target_param_list = True

    if op_mode_arg is None:

        if op_mode == "until-num":
            print("--run-until-num requires an argument")
            sys.exit(1)

        if op_mode == "until-sig":
            print("--run-until-signal requires an argument")
            sys.exit(1)

    v, r = batch_run(run_target, output_path, op_mode, op_mode_arg, save_mode, target_param_list)
    if not v:
        print(r)
        sys.exit(1)
    print("Successful")
