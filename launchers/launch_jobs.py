#!/usr/bin/env python3

import sys
import os

class BaseStep:
    def __init__(self, params=None):
        self.params = params
    def desc(self):
        return "BaseStep"
    def run_step(self):
        return False, "Not implemented"

class BaseJob:

    def __init__(self, params=None):
        self.params = params
        self.step_list = []

    def _merge_params_downwards(self, p_parent, p_child):

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

    def desc(self):
        return "BaseJob"

    def add_step(self, the_step):
        the_step.params = self._merge_params_downwards(self.params, the_step.params)
        self.step_list.append(the_step)

    def run_job(self):
        for s in self.step_list:
            print("run_job (%s): now running step: [%s]" % (self.desc(), s.desc()))
            v, r = s.run_step()
            if not v:
                return False, "Step [%s] failed: [%s]" % (s.desc(), r)
        return True, None

def run_job_list(job_list):

    for j in job_list:
        print("run_job_list: now running job: [%s]" % j.desc())
        v, r = j.run_job()
        if not v:
            return False, "Job [%s] failed. Step: [%s]" % (j.desc(), r)
    return True, None

def puaq():
    print("Usage: %s input.txt" % os.path.basename(__file__)) # mvtodo: adapt filename (input.txt) once decision is made
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    # mvtodo: also accept a "recipe" file
