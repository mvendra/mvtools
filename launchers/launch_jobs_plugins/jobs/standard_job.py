#!/usr/bin/env python3

import launch_jobs

class StandardJob(launch_jobs.BaseJob): # hint: custom jobs should have a class named CustomJob
    def get_desc(self):
        return "Standard job"
    def add_task(self, task):
        task.params = launch_jobs._merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
        return True, None
    def run_job(self, execution_name=None):
        for t in self.task_list:
            v, r = launch_jobs._wait_if_paused(execution_name)
            if not v:
                return False, r
            print(launch_jobs._format_job_info_msg(self, t))
            v, r = t.run_task(execution_name)
            if not v:
                return False, launch_jobs._format_task_error_msg(t, r)
        return True, None
