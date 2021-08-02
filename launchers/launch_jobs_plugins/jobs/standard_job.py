#!/usr/bin/env python3

import launch_jobs

class StandardJob(launch_jobs.BaseJob): # hint: custom jobs should have a class named CustomJob
    def get_desc(self):
        return "Standard job"
    def add_task(self, task):
        task.params = launch_jobs._merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
        return True, None
    def run_job(self, feedback_object, execution_name=None):
        for t in self.task_list:
            v, r = launch_jobs._wait_if_paused(feedback_object, execution_name)
            if not v:
                return False, r
            feedback_object(launch_jobs._format_job_info_msg_task(self, t))
            try:
                v, r = t.run_task(feedback_object, execution_name)
            except:
                return False, "Task [%s][%s] caused an exception." % (t.name, t.get_desc())
            if not v:
                feedback_object(launch_jobs._format_task_error_msg(t, r))
                return False, "Failed task"
            if r is not None:
                feedback_object(launch_jobs._format_task_warning_msg_console_output(t, r))
            if v:
                feedback_object(launch_jobs._format_task_info_msg(t, r))
        return True, None
