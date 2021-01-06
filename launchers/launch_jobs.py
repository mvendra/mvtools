#!/usr/bin/env python3

import sys
import os

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
        return "Generic base job"
    def add_task(self, task):
        task.params = _merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
    def run_job(self):
        for t in self.task_list:
            print("run_job [%s][%s]: now running task: [%s][%s]" % (self.name, self.get_desc(), t.name, t.get_desc()))
            v, r = t.run_task()
            if not v:
                return False, "Task [%s][%s] failed: [%s]" % (t.name, t.get_desc(), r)
        return True, None

class RunOptions:
    def __init__(self, early_abort=True):
        self.early_abort = early_abort # immediately stop the execution whenever any job fails (stop upon first failure)

def run_job_list(job_list, options):

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

    return (not(has_any_failed)), report

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
