#!/usr/bin/env python

import launch_jobs
import mvtools_exception

class CustomJob(launch_jobs.BaseJob):

    def get_desc(self):
        return "Optional job"

    def add_entry(self, task):
        self.entries_list.append(task)
        return True, None

    def run_job(self, feedback_object, execution_name = None, options = None):

        any_warnings = False
        intermediary_failure = False
        skip_on_clear = []

        if "skip-on-clear" in self.params:
            skip_on_clear_read = self.params["skip-on-clear"]
            if skip_on_clear_read == None:
                return False, "The skip-on-clear option cannot be valueless"
            if isinstance(skip_on_clear_read, list):
                skip_on_clear = skip_on_clear_read
            else:
                skip_on_clear.append(skip_on_clear_read)

        for entry in self.entries_list:

            entry_skip_on_clear = entry.name in skip_on_clear

            if entry.get_type() == launch_jobs.BASE_TYPE_JOB:

                v, r = launch_jobs.run_single_job(entry, self.name, feedback_object, execution_name, options)
                if not v:
                    if options.early_abort:
                        return False, "Failed job: [%s]" % r
                    else:
                        intermediary_failure = True
                if v and r:
                    any_warnings = True

                if entry_skip_on_clear and v and (r is None):
                    return True, any_warnings

                continue

            v, r = launch_jobs._wait_if_paused(feedback_object, execution_name)
            if not v:
                return False, r

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
                return False, "Failed task: [%s]" % r

            if r is not None:
                any_warnings = True
                feedback_object(launch_jobs._format_task_warning_msg_console_output(entry, r))
            else:
                feedback_object(launch_jobs._format_task_info_msg(entry))
                if entry_skip_on_clear:
                    return True, any_warnings

        if intermediary_failure:
            return False, "Intermediary failures"
        return True, any_warnings
