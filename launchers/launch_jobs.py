#!/usr/bin/env python3

import sys
import os

import path_utils
import maketimestamp
import toolbus
import minicron
import retry
import terminal_colors
import mvtools_exception

LAUNCHJOBS_TOOLBUS_DATABASE = "mvtools_launch_jobs"

def _format_job_info_msg_task(job, task):
    return "Job:  [%s][%s][%s]: now running task: [%s][%s]" % (maketimestamp.get_timestamp_now(), job.name, job.get_desc(), task.name, task.get_desc())

def _format_job_info_msg_started(job):
    return "Job:  [%s][%s][%s]: started." % (maketimestamp.get_timestamp_now(), job.name, job.get_desc())

def _format_job_info_msg_pause_failed(job, detail):
    return "Job:  [%s][%s][%s]: pausing failed: [%s]" % (maketimestamp.get_timestamp_now(), job.name, job.get_desc(), detail)

def _format_job_info_msg_succeeded(job):
    return "Job:  [%s][%s][%s]: succeeded." % (maketimestamp.get_timestamp_now(), job.name, job.get_desc())

def _format_job_info_msg_failed(job, detail):
    return "Job:  [%s][%s][%s]: failed: [%s]" % (maketimestamp.get_timestamp_now(), job.name, job.get_desc(), detail)

def _format_task_info_msg(task, detail):
    return "Task: [%s][%s][%s]: succeeded." % (maketimestamp.get_timestamp_now(), task.name, task.get_desc())

def _format_task_error_msg(task, detail):
    return "Task: [%s][%s][%s]: failed: [%s]" % (maketimestamp.get_timestamp_now(), task.name, task.get_desc(), detail)

def _format_task_warning_msg(task, detail):
    return "Task: [%s][%s][%s]: warns: [%s]" % (maketimestamp.get_timestamp_now(), task.name, task.get_desc(), detail)

def _format_task_warning_msg_console_output(task, detail):
    return "%s%s%s." % (terminal_colors.TTY_YELLOW, _format_task_warning_msg(task, detail), terminal_colors.get_standard_color())

class BaseJob:
    def __init__(self, name = None):
        self.name = name
        self.params = {}
        self.entries_list = []
    def get_desc(self):
        return "Base job"
    def add_task(self, task):
        return False, None
    def run_job(self, feedback_object, execution_name=None):
        return False, None

class BaseTask:
    def __init__(self, name = None):
        self.name = name
        self.params = {}
    def get_desc(self):
        return "Generic base task"
    def run_task(self, feedback_object, execution_name=None):
        return False, "Not implemented"

def _setup_toolbus(execution_name):

    # ensures the toolbus database exists
    v, r = toolbus.bootstrap_custom_toolbus_db(LAUNCHJOBS_TOOLBUS_DATABASE)
    # no need to check the return

    # if the following field already exists, then this execution has already been registered on toolbus. fail.
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status")
    if not v:
        return False, "Unable to start execution: [%s]" % r
    if r is not None:
        return False, "Unable to start execution: execution name [%s] already exists inside launch_jobs's toolbus database." % execution_name

    return True, None

def _retry_helper(wait_object, wait_object_name, function):

    if wait_object is None:
        return True, None

    retry_opts = {"retries_max": 800000, "retry_sleep_random": 2000}
    v, r = retry.retry(retry_opts, function, wait_object)
    if not v:
        return False, "Failed retrying on %s [%s]: [%s]" % (wait_object_name, wait_object, r)

    return True, None

def _handle_delayed_start_signal_delegate(signal_delay):
    v, r = toolbus.get_signal(signal_delay) # signal will be consumed
    return v, not (r == None)

def _handle_delayed_start_execution_delegate(execution_delay):
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_delay, "status")
    return v, (r == None)

def _is_status_paused_delegate(execution_name):
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status")
    if not v:
        return False, r
    if r is None:
        return False, "Unable to fetch execution [%s]'s status (for pausing)." % execution_name
    stat_val = (r[1].lower())
    if stat_val == "paused":
        return True, True
    elif stat_val == "running":
        return True, False
    else:
        return False, "Invalid value on status field: [%s]. Execution: [%s]" % (stat_val, execution_name)

def _is_status_running_delegate(execution_name):
    v, r = _is_status_paused_delegate(execution_name)
    if not v:
        return False, r
    return v, (not r)

def _get_delay_report_msg(execution_name):
    delay_timestamp = maketimestamp.get_timestamp_now()
    base_delay_report_message = "Execution context [%s] will be delayed at [%s]" % (execution_name, delay_timestamp)
    return base_delay_report_message

def _handle_delayed_start_time(feedback_object, message_report_function, execution_name, time_delay):

    if time_delay is None:
        return True, None

    wait_duration = minicron.convert_time_string(time_delay)
    if wait_duration is None:
        return False, "Requested delay of [%s] couldn't be parsed." % (time_delay)

    feedback_object("%s Reason: time delay of [%s]" % (message_report_function(execution_name), time_delay))
    if not minicron.busy_wait(wait_duration):
        return False, "Requested delay of [%s] failed to be performed." % (time_delay)

    return True, None

def _handle_delayed_start_signal(feedback_object, message_report_function, execution_name, signal_delay):
    if signal_delay is None:
        return True, None
    feedback_object("%s Reason: signal delay [%s]" % (message_report_function(execution_name), signal_delay))
    return _retry_helper(signal_delay, "signal", _handle_delayed_start_signal_delegate)

def _handle_delayed_start_execution(feedback_object, message_report_function, execution_name, execution_delay):
    if execution_delay is None:
        return True, None
    feedback_object("%s Reason: execution delay [%s]" % (message_report_function(execution_name), execution_delay))
    return _retry_helper(execution_delay, "execution", _handle_delayed_start_execution_delegate)

def _handle_delayed_start(feedback_object, execution_name, time_delay, signal_delay, execution_delay):
    try:
        v, r = _handle_delayed_start_delegate(feedback_object, execution_name, time_delay, signal_delay, execution_delay)
        return v, r
    except KeyboardInterrupt as kbi:
        return False, "Delayed start failed - user aborted"
    except:
        return False, "Delayed start failed - unknown reason"

def _handle_delayed_start_delegate(feedback_object, execution_name, time_delay, signal_delay, execution_delay):

    if time_delay is None and signal_delay is None and execution_delay is None: # no delay applicable
        return True, None

    # setup initial delayed state
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "delayed", [])
    if not v:
        return False, "Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)

    # time delay
    v, r = _handle_delayed_start_time(feedback_object, _get_delay_report_msg, execution_name, time_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    # signal delay
    v, r = _handle_delayed_start_signal(feedback_object, _get_delay_report_msg, execution_name, signal_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    # execution delay
    v, r = _handle_delayed_start_execution(feedback_object, _get_delay_report_msg, execution_name, execution_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    return True, None

def _wait_if_paused(feedback_object, execution_name):

    v, r = _is_status_paused_delegate(execution_name)
    if not v:
        return False, r
    if not r: # has not been paused
        return True, None

    # yes, execution has been paused
    feedback_object("Execution [%s] has been paused." % execution_name)
    v, r = _retry_helper(execution_name, "execution name", _is_status_running_delegate)
    if not v:
        return False, r
    feedback_object("Execution [%s] will resume." % execution_name)
    return True, None

class RunOptions:
    def __init__(self, early_abort=True, time_delay=None, signal_delay=None, execution_delay=None):
        self.early_abort = early_abort # stop upon first job failure (note: applies to jobs *only*)
        self.time_delay = time_delay # wait for a given amount of time before starting this execution (7h, 30m, 20s for example)
        self.signal_delay = signal_delay # wait for the given toolbus signal before starting this execution
        self.execution_delay = execution_delay # wait for the given execution to end before starting this execution

def _has_any_job_failed(job_result):
    for jr in job_result:
        if not jr[0]:
            return True
    return False

def run_job_list(job_list, feedback_object, execution_name=None, options=None):

    if execution_name is None:
        execution_name = "launch_jobs_%d" % os.getpid()

    if options is None:
        options = RunOptions()

    # setup toolbus
    v, r = _setup_toolbus(execution_name)
    if not v:
        return False, [r]

    job_v, job_r = run_job_list_delegate(job_list, feedback_object, execution_name, options)

    v, r = toolbus.remove_table(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name)
    if not v:
        return False, ["Unable to remove execution named [%s] from toolbus database." % execution_name] + job_r

    return job_v, job_r

def run_job_list_delegate(job_list, feedback_object, execution_name, options):

    # delayed start if configured
    v, r = _handle_delayed_start(feedback_object, execution_name, options.time_delay, options.signal_delay, options.execution_delay)
    if not v:
        return False, [r]

    # setup the status of the soon-to-start execution
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "running", [])
    if not v:
        return False, ["Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)]

    begin_timestamp = maketimestamp.get_timestamp_now()

    # register timestamp in the execution context
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "begin-timestamp", begin_timestamp, [])
    if not v:
        return False, ["Unable to start execution: execution name [%s]'s begin-timestamp couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)]

    feedback_object("Execution context [%s] will begin running at [%s]" % (execution_name, begin_timestamp))

    report = []
    for j in job_list:

        feedback_object(_format_job_info_msg_started(j))

        j_msg = ""
        v, r = _wait_if_paused(feedback_object, execution_name)
        if not v:
            j_msg = _format_job_info_msg_pause_failed(j, r)
        else:

            try:
                v, r = j.run_job(feedback_object, execution_name)
            except mvtools_exception.mvtools_exception as mvtex:
                return False, ["Job [%s][%s] caused an mvtools exception. Aborting: [%s]" % (j.name, j.get_desc(), mvtex)]
            except Exception as ex:
                return False, ["Job [%s][%s] caused an exception. Aborting: [%s]" % (j.name, j.get_desc(), ex)]
            except:
                return False, ["Job [%s][%s] caused an unknown exception. Aborting." % (j.name, j.get_desc())]

            if v:
                j_msg = _format_job_info_msg_succeeded(j)
            else:
                j_msg = _format_job_info_msg_failed(j, r)

        report.append((v, j_msg))
        feedback_object(j_msg)

        if not v and options.early_abort:
            break

    return (not _has_any_job_failed(report)), report

def get_current_executions():

    v, r = toolbus.get_all_tables(LAUNCHJOBS_TOOLBUS_DATABASE)
    if not v:
        return False, "Unable to fetch executions from toolbus launch_jobs database: [%s]" % r

    report = []
    for exe_name in r:
        v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, exe_name, "status")
        if not v:
            return False, "Unable to fetch execution [%s]'s status: [%s]" % (exe_name, r)
        if r is None:
            return False, "Unable to fetch execution [%s]'s status." % (exe_name)
        report.append("%s: %s" % (exe_name, r[1]))

    return True, report

def _change_status(exec_name, status_val, log_noun, log_verb):

    v, r = toolbus.get_all_tables(LAUNCHJOBS_TOOLBUS_DATABASE)
    if not v:
        print("Unable to fetch executions from toolbus launch_jobs database: [%s]" % r)
        return
    if exec_name not in r:
        print("Execution [%s] is not registered on launch_jobs toolbus database." % exec_name)
        return

    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, exec_name, "status", status_val, [])
    if not v:
        print("Unable to %s execution [%s]: [%s]" % (log_noun, exec_name, r))
        return

    print("Execution [%s] has been %s" % (exec_name, log_verb))

def menu_pause(exec_name):
    _change_status(exec_name, "paused", "pause", "paused")

def menu_resume(exec_name):
    _change_status(exec_name, "running", "resume", "resumed")

def menu_list():

    print("List of active executions:")
    v, r = get_current_executions()
    if not v:
        print(r)
        return

    for l in r:
        print(l)

def puaq():
    print("Usage: %s [--list-executions | --pause-execution execution-name | --resume-execution execution-name]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    params = sys.argv[1:]

    next_pause_exec = False
    next_resume_exec = False

    for p in params:

        if next_pause_exec:
            next_pause_exec = False
            menu_pause(p)
            continue
        elif next_resume_exec:
            next_resume_exec = False
            menu_resume(p)
            continue

        if p == "--list-executions":
            menu_list()
        elif p == "--pause-execution":
            next_pause_exec = True
        elif p == "--resume-execution":
            next_resume_exec = True
        else:
            print("Invalid commandline argument: [%s]" % p)
