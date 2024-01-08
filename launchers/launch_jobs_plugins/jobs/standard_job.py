#!/usr/bin/env python3

import launch_jobs
import mvtools_exception

class StandardJob(launch_jobs.BaseJob): # hint: custom jobs should have a class named CustomJob

    def get_desc(self):
        return "Standard job"

    def add_entry(self, task):
        self.entries_list.append(task)
        return True, None

    def run_job(self, feedback_object, execution_name=None, options=None):

        intermediary_failure = False
        for entry in self.entries_list:

            if entry.get_type() == launch_jobs.BASE_TYPE_JOB:

                v, r = launch_jobs.run_single_job(entry, feedback_object, execution_name, options)
                if not v:
                    if options.early_abort:
                        return False, "Failed job"
                    else:
                        intermediary_failure = True
                        feedback_object(launch_jobs._format_job_info_msg_failed(entry, r))

                continue

            v, r = launch_jobs._wait_if_paused(feedback_object, execution_name)
            if not v:
                return False, r

            feedback_object(launch_jobs._format_job_info_msg_task(self, entry))
            try:
                v, r = entry.run_task(feedback_object, execution_name)
            except mvtools_exception.mvtools_exception as mvtex:
                return False, "Task [%s][%s] caused an mvtools exception: [%s]" % (entry.name, entry.get_desc(), mvtex)
            except Exception as ex:
                return False, "Task [%s][%s] caused an exception: [%s]" % (entry.name, entry.get_desc(), ex)
            except:
                return False, "Task [%s][%s] caused an unknown exception." % (entry.name, entry.get_desc())

            if not v:
                feedback_object(launch_jobs._format_task_error_msg(entry, r))
                return False, "Failed task"

            if r is not None:
                feedback_object(launch_jobs._format_task_warning_msg_console_output(entry, r))
            else:
                feedback_object(launch_jobs._format_task_info_msg(entry, r))

        if intermediary_failure:
            return False, "Intermediary failures"
        return True, None
