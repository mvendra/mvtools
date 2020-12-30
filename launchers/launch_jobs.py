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
    def __init__(self, params=None):
        self.params = params
    def get_desc(self):
        return "Generic base task"
    def run_task(self):
        return False, "Not implemented"

class BaseJob:
    def __init__(self, params=None):
        self.params = params
        self.task_list = []
    def get_desc(self):
        return "Generic base job"
    def add_task(self, task):
        return None
    def run_job(self):
        return False, "Not implemented"

def run_job_list(job_list):
    for j in job_list:
        v, r = j.run_job()
        if not v:
            return False, "Job [%s] failed. Task: [%s]" % (j.get_desc(), r)
    return True, None

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
