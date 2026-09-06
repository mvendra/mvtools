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
        expect_fail = []
        if "expect-fail" in self.params:
            expect_fail_read = self.params["expect-fail"]
            if expect_fail_read == None:
                return False, "The expect-fail option cannot be valueless"
            if isinstance(expect_fail_read, list):
                expect_fail = expect_fail_read
            else:
                expect_fail.append(expect_fail_read)

        for entry in self.entries_list:

            entry_must_fail = entry.name in expect_fail

            if entry.get_type() == launch_jobs.BASE_TYPE_JOB:

                v, r = launch_jobs.run_single_job(entry, self.name, feedback_object, execution_name, options)
                if entry_must_fail:
                    if v:
                        return False, "Job [%s] was expected to fail" % entry.name
                    continue
                if not v:
                    if options.early_abort:
                        return False, "Failed job: [%s]" % r
                    else:
                        intermediary_failure = True
                if v and r:
                    any_warnings = True

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

            if entry_must_fail:
                if v:
                    return False, "Task [%s] was expected to fail" % entry.name
                continue

            if not v:
                feedback_object(launch_jobs._format_task_error_msg(entry, r))
                return False, "Failed task: [%s]" % r

            if r is not None:
                any_warnings = True
                feedback_object(launch_jobs._format_task_warning_msg_console_output(entry, r))
            else:
                feedback_object(launch_jobs._format_task_info_msg(entry))

        if intermediary_failure:
            return False, "Intermediary failures"
        return True, any_warnings
