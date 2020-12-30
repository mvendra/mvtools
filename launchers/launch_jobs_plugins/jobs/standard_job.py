#!/usr/bin/env python3

import launch_jobs

class StandardJob(launch_jobs.BaseJob):
    def __init__(self, desc="", params=None):
        super().__init__(params)
        self.desc = desc
    def get_desc(self):
        return self.desc
    def add_task(self, task):
        task.params = launch_jobs._merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
    def run_job(self):
        for t in self.task_list:
            print("run_job (%s): now running task: [%s]" % (self.get_desc(), t.get_desc()))
            v, r = t.run_task()
            if not v:
                return False, "Task [%s] failed: [%s]" % (t.get_desc(), r)
        return True, None
