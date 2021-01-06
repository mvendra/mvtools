#!/usr/bin/env python3

import launch_jobs

class StandardJob(launch_jobs.BaseJob):
    def get_desc(self):
        return "Standard job"
    def add_task(self, task):
        task.params = launch_jobs._merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
        return True, None
    def run_job(self):
        for t in self.task_list:
            print("run_job [%s][%s]: now running task: [%s][%s]" % (self.name, self.get_desc(), t.name, t.get_desc()))
            v, r = t.run_task()
            if not v:
                return False, "Task [%s][%s] failed: [%s]" % (t.name, t.get_desc(), r)
        return True, None
