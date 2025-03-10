#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run
import maketimestamp
import toolbus

def _compare_num(input_int, input_str):

    if len(input_str) < 3:
        return (input_int == int(input_str)) # default to eq

    if input_str[0:2] == "eq":
        return (input_int == int(input_str[2:]))

    if input_str[0:2] == "gt":
        return (input_int > int(input_str[2:]))

    return (input_int == int(input_str)) # default to eq

def _compare_time(input_current_date, input_arg_date):

    if input_arg_date[0:2] == "eq":
        return (input_current_date == input_arg_date[2:])

    if input_arg_date[0:2] == "gt":

        # current date
        day_cur = int(input_current_date[0:2])
        month_cur = int(input_current_date[2:4])
        year_cur = int(input_current_date[4:8])
        hour_cur = int(input_current_date[9:11])
        minute_cur = int(input_current_date[11:13])
        second_cur = int(input_current_date[13:15])

        # argument (target) date
        day_arg = int(input_arg_date[2:4])
        month_arg = int(input_arg_date[4:6])
        year_arg = int(input_arg_date[6:10])
        hour_arg = int(input_arg_date[11:13])
        minute_arg = int(input_arg_date[13:15])
        second_arg = int(input_arg_date[15:17])

        # round 1 - years
        if year_cur < year_arg:
            return False
        elif year_cur > year_arg:
            return True
        else:

            # round 2 - months
            if month_cur < month_arg:
                return False
            elif month_cur > month_arg:
                return True
            else:

                # round 3 - days
                if day_cur < day_arg:
                    return False
                elif day_cur > day_arg:
                    return True
                else:

                    # round 4 - hours
                    if hour_cur < hour_arg:
                        return False
                    elif hour_cur > hour_arg:
                        return True
                    else:

                        # round 5 - minutes
                        if minute_cur < minute_arg:
                            return False
                        elif minute_cur > minute_arg:
                            return True
                        else:

                            # round 6 - seconds
                            if second_cur < second_arg:
                                return False
                            elif second_cur > second_arg:
                                return True
                            else:
                                return False # same to the dot

    return (input_current_date == input_arg_date) # default to eq

def _stop_fail(stop_arg, num_exec, num_fail):
    return True, _compare_num(num_fail, stop_arg)

def _stop_count(stop_arg, num_exec, num_fail):
    return True, _compare_num(num_exec, stop_arg)

def _stop_time(stop_arg, num_exec, num_fail):
    return True, _compare_time(maketimestamp.get_timestamp_now_compact(), stop_arg)

def _stop_tb_sig(stop_arg, num_exec, num_fail):

    v, r = toolbus.get_signal(stop_arg, False)
    if not v:
        return False, r
    return True, (r is not None)

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

def _run_until(cmd, output_path, op_modes, stop_mode, save_mode, start_time):

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

        stop_flag = (stop_mode == "stop-all")
        for stop_cond in op_modes:

            fptr = stop_cond[0]
            v, r = fptr(stop_cond[1], num_execs, num_failed)
            if not v:
                return False, r

            if r and stop_mode == "stop-any":
                stop_flag = True
                break

            if not r and stop_mode == "stop-all":
                stop_flag = False
                break

        if stop_flag:
            break

    _save_summary(cmd, output_path, num_execs, num_failed, start_time)

    return True, None

def batch_run(run_target, output_path, op_modes, stop_mode, save_mode, target_param_list):

    if not os.path.exists(run_target):
        return False, "Target [%s] does not exist." % run_target

    if os.path.exists(output_path):
        return False, "Output path [%s] already exists." % output_path

    if not path_utils.guaranteefolder(output_path):
        return False, "Unable to create folder [%s]." % output_path

    valid_stop_modes = ["stop-any", "stop-all"]
    if not stop_mode in valid_stop_modes:
        return False, "Invalid stop mode: [%s]." % stop_mode

    valid_save_modes = ["save-all", "save-fail"]
    if not save_mode in valid_save_modes:
        return False, "Invalid save mode: [%s]." % save_mode

    if len(op_modes) < 1:
        return False, "No operation modes specified."

    cmd = [os.path.abspath(run_target)]
    for p in target_param_list:
        cmd.append(p)

    for opm in op_modes:

        opm_original_name = opm[0]

        # run until fail
        if opm[0] == "until-fail":
            opm[0] = _stop_fail

        # run until iteration count
        elif opm[0] == "until-cnt":
            opm[0] = _stop_count

        # run until time
        elif opm[0] == "until-time":
            if opm[1] is not None:
                if len(opm[1]) < 15:
                    return False, "argument of stop condition until-time is invalid: [%s]." % opm[1]
            opm[0] = _stop_time

        # run until toolbus signal
        elif opm[0] == "until-sig":
            opm[0] = _stop_tb_sig

        else:
            return False, "Operation mode [%s] is invalid." % opm[0]

        if opm[1] is None:
            return False, "Operation mode [%s] - missing argument." % opm_original_name

    start_time = maketimestamp.get_timestamp_now()
    v, r = _run_until(cmd, output_path, op_modes, stop_mode, save_mode, start_time)
    if not v:
        return False, r
    return True, None

def puaq():
    print("Usage: %s [--help] run_target output_path [--run-until-fail [eq(def)|gt]X | --run-until-count [eq(def)|gt]X | --run-until-time [eq(def)|gt]X | --run-until-signal X]+ [--stop-any (default) | --stop-all] [--save-fail (default) | --save-all] [-- target-param-list]" % path_utils.basename_filtered(__file__))
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
    op_modes = []
    op_modes_arg_next = False
    stop_mode = None
    save_mode = None
    parsing_target_param_list = False
    target_param_list = []

    # mandatory
    run_target = sys.argv[1]
    output_path = sys.argv[2]

    # defaults
    stop_mode = "stop-any"
    save_mode = "save-fail"

    for p in params:

        if parsing_target_param_list:
            target_param_list.append(p)
            continue

        if op_modes_arg_next:
            op_modes[len(op_modes)-1][1] = p
            op_modes_arg_next = False
            continue

        if p == "--run-until-fail":
            op_modes.append(["until-fail", None])
            op_modes_arg_next = True
        elif p == "--run-until-count":
            op_modes.append(["until-cnt", None])
            op_modes_arg_next = True
        elif p == "--run-until-time":
            op_modes.append(["until-time", None])
            op_modes_arg_next = True
        elif p == "--run-until-signal":
            op_modes.append(["until-sig", None])
            op_modes_arg_next = True
        elif p == "--save-fail":
            save_mode = "save-fail"
        elif p == "--save-all":
            save_mode = "save-all"
        elif p == "--stop-any":
            stop_mode = "stop-any"
        elif p == "--stop-all":
            stop_mode = "stop-all"
        elif p == "--":
            parsing_target_param_list = True

    if op_modes_arg_next:
        print("Unterminated operation mode parsing (missing arg).")
        sys.exit(1)

    v, r = batch_run(run_target, output_path, op_modes, stop_mode, save_mode, target_param_list)
    if not v:
        print(r)
        sys.exit(1)
    print("Successful")
