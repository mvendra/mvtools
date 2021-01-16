#!/usr/bin/env python3

import sys
import os

import toolbus
import minicron

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

def _handle_delayed_start(execution_name, time_delay):

    if time_delay is None: # no delay applicable
        return True, None

    # setup initial delayed state
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "delayed", [])
    if not v:
        return False, "Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)

    wait_duration = minicron.convert_time_string(time_delay)
    if wait_duration is None:
        return False, "Unable to start execution [%s]: requested delay of [%s] couldn't be parsed." % (execution_name, options.time_delay)
    if not minicron.busy_wait(wait_duration):
        return False, "Unable to start execution [%s]: requested delay of [%s] failed to be performed." % (execution_name, options.time_delay)

    return True, None

class RunOptions:
    def __init__(self, early_abort=True, time_delay=None):
        self.early_abort = early_abort # stop upon first job failure (note: applies to jobs *only*)
        self.time_delay = time_delay # wait for a given amount of time before starting this execution (7h, 30m, 20s for example)

def run_job_list(job_list, options, execution_name=None):

    if execution_name is None:
        execution_name = "launch_jobs_%d" % os.getpid()

    # setup toolbus
    v, r = _setup_toolbus(execution_name)
    if not v:
        return False, [r]

    # delayed start if configured
    v, r = _handle_delayed_start(execution_name, options.time_delay)
    if not v:
        return False, [r]

    # setup the status of the soon-to-start execution
    v, r = toolbus.set_field(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name, "status", "running", [])
    if not v:
        return False, ["Unable to start execution: execution name [%s]'s status couldn't be registered on launch_jobs's toolbus database: [%s]" % (execution_name, r)]

    print("Execution context [%s] will begin running." % execution_name)

    report = []
    has_any_failed = False
    for j in job_list:

        v, r = j.run_job()
        j_msg = ""

        if v:
            j_msg = "Job [%s][%s] succeeded." % (j.name, j.get_desc())
        else:
            j_msg = "Job [%s][%s] failed: [%s]." % (j.name, j.get_desc(), r)
            has_any_failed = True

        report.append((v, j_msg))

        if not v and options.early_abort:
            break

    v, r = toolbus.remove_table(LAUNCHJOBS_TOOLBUS_DATABASE, execution_name)
    if not v:
        return False, ["Unable to remove execution named [%s] from toolbus database." % execution_name] + report

    return (not(has_any_failed)), report

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
