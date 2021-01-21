#!/usr/bin/env python3

import sys
import os
import datetime
import time

import toolbus
import minicron
import retry

LAUNCHJOBS_TOOLBUS_DATABASE = "mvtools_launch_jobs"

def _merge_params_downwards(p_parent, p_child):

    result = {}

    if p_parent is None and p_child is None:
        return None
    if p_parent is None and p_child is not None:
        return p_child
    if p_parent is not None and p_child is None:
        return p_parent

    for k in p_parent:
        if not k in p_child:
            result[k] = p_parent[k]

    for k in p_child:
        result[k] = p_child[k]

    return result

def _format_job_info_msg(job, task):
    return "Job: [%s][%s]: now running task: [%s][%s]" % (job.name, job.get_desc(), task.name, task.get_desc())

def _format_task_error_msg(task, detail):
    return "Task [%s][%s] failed: [%s]" % (task.name, task.get_desc(), detail)

class BaseTask:
    def __init__(self, name=None, params=None):
        self.name = name
        self.params = params
    def get_desc(self):
        return "Generic base task"
    def run_task(self):
        return False, "Not implemented"

class BaseJob:
    def __init__(self, name=None, params=None):
        self.name = name
        self.params = params
        self.task_list = []
    def get_desc(self):
        return "Base job"
    def add_task(self, task):
        return False, None
    def run_job(self):
        return False, None

def _setup_toolbus(execution_name):

    # ensures the toolbus database exists
    v, r = toolbus.bootstrap_custom_toolbus_db(LAUNCHJOBS_TOOLBUS_DATABASE)
    # no need to check the return

    # if the following field already exists, then this execution has already been registered on toolbus. fail.
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status")
    if v:
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
    return toolbus.get_signal(signal_delay) # signal will be consumed

def _handle_delayed_start_execution_delegate(execution_delay):
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_delay, "status")
    return not v, r

def _is_status_paused_delegate(execution_name):
    v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status")
    if not v:
        return False, r
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

def _handle_delayed_start_time(time_delay):

    if time_delay is None:
        return True, None

    wait_duration = minicron.convert_time_string(time_delay)
    if wait_duration is None:
        return False, "Requested delay of [%s] couldn't be parsed." % (time_delay)
    if not minicron.busy_wait(wait_duration):
        return False, "Requested delay of [%s] failed to be performed." % (time_delay)

    return True, None

def _handle_delayed_start_signal(signal_delay):
    return _retry_helper(signal_delay, "signal", _handle_delayed_start_signal_delegate)

def _handle_delayed_start_execution(execution_delay):
    return _retry_helper(execution_delay, "execution", _handle_delayed_start_execution_delegate)

def _handle_delayed_start(execution_name, time_delay, signal_delay, execution_delay):

    if time_delay is None and signal_delay is None and execution_delay is None: # no delay applicable
        return True, None

    # setup initial delayed state
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "delayed", [])
    if not v:
        return False, "Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)

    # time delay
    v, r = _handle_delayed_start_time(time_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    # signal delay
    v, r = _handle_delayed_start_signal(signal_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    # execution delay
    v, r = _handle_delayed_start_execution(execution_delay)
    if not v:
        return False, "Unable to start execution [%s]: %s." % (execution_name, r)

    return True, None

def _wait_if_paused(execution_name):

    v, r = _is_status_paused_delegate(execution_name)
    if not v:
        return False, r
    if not r: # has not been paused
        return True, None

    # yes, execution has been paused
    print("Execution [%s] has been paused." % execution_name)
    v, r = _retry_helper(execution_name, "execution name", _is_status_running_delegate)
    if not v:
        return False, r
    print("Execution [%s] will resume." % execution_name)
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

def run_job_list(job_list, execution_name=None, options=None):

    if execution_name is None:
        execution_name = "launch_jobs_%d" % os.getpid()

    if options is None:
        options = RunOptions()

    # setup toolbus
    v, r = _setup_toolbus(execution_name)
    if not v:
        return False, [r]

    # delayed start if configured
    v, r = _handle_delayed_start(execution_name, options.time_delay, options.signal_delay, options.execution_delay)
    if not v:
        return False, [r]

    # setup the status of the soon-to-start execution
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "running", [])
    if not v:
        return False, ["Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)]

    begin_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S - %d/%m/%Y")

    # register timestamp in the execution context
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "begin-timestamp", begin_timestamp, [])
    if not v:
        return False, ["Unable to start execution: execution name [%s]'s begin-timestamp couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)]

    print("Execution context [%s] will begin running at [%s]." % (execution_name, begin_timestamp))

    report = []
    for j in job_list:

        j_msg = ""
        v, r = _wait_if_paused(execution_name)
        if not v:
            j_msg = "Pausing failed: [%s]. Job: [%s]" % (r, j.name)
        else:
            v, r = j.run_job()
            if v:
                j_msg = "Job [%s][%s] succeeded." % (j.name, j.get_desc())
            else:
                j_msg = "Job [%s][%s] failed: [%s]." % (j.name, j.get_desc(), r)

        report.append((v, j_msg))

        if not v and options.early_abort:
            break

    v, r = toolbus.remove_table(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name)
    if not v:
        return False, ["Unable to remove execution named [%s] from toolbus database." % execution_name] + report

    return (not _has_any_job_failed(report)), report

def print_current_executions():

    v, r = toolbus.get_all_tables(LAUNCHJOBS_TOOLBUS_DATABASE)
    if not v:
        return False, "Unable to fetch executions from toolbus launch_jobs database: [%s]" % r

    report = []
    for exe_name in r:
        v, r = toolbus.get_field(LAUNCHJOBS_TOOLBUS_DATABASE, exe_name, "status")
        if not v:
            return False, "Unable to fetch execution [%s]'s status: [%s]" % (exe_name, r)
        report.append("%s: %s" % (exe_name, r[1]))

    return True, report

if __name__ == "__main__":
    v, r = print_current_executions()
    if not v:
        print(r)
        sys.exit(1)
    for l in r:
        print(l)
