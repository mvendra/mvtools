#!/usr/bin/env python3

import os

import path_utils
import log_helper
import output_backup_helper

import launch_jobs
import recipe_processor

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "recipe"

    def _read_params(self):

        operation = None
        recipe = None
        exec_name = None
        early_abort = None
        time_delay = None
        signal_delay = None
        execution_delay = None
        envvars = []

        # operation
        local_run = "run" in self.params
        local_test = "test" in self.params
        if local_run and local_test:
            return False, "Specify only either run or test - not both"
        if not local_run and not local_test:
            return False, "Specify at least either run or test"

        if local_run:
            operation = "run"
        if local_test:
            operation = "test"

        # recipe
        try:
            recipe = self.params["recipe"]
        except KeyError:
            return False, "recipe is a required parameter"

        # exec_name
        try:
            exec_name = self.params["exec_name"]
        except KeyError:
            pass # optional

        # early_abort
        try:
            early_abort = self.params["early_abort"]
        except KeyError:
            pass # optional

        # time_delay
        try:
            time_delay = self.params["time_delay"]
        except KeyError:
            pass # optional

        # signal_delay
        try:
            signal_delay = self.params["signal_delay"]
        except KeyError:
            pass # optional

        # execution_delay
        try:
            execution_delay = self.params["execution_delay"]
        except KeyError:
            pass # optional

        # envvars
        try:
            envvars_read = self.params["envvar"]
            if isinstance(envvars_read, list):
                envvars = envvars_read
            else:
                envvars.append(envvars_read)
        except KeyError:
            pass # optional

        # validate recipe
        if not os.path.exists(recipe):
            return False, "recipe [%s] does not exist" % recipe

        return True, (operation, recipe, exec_name, early_abort, time_delay, signal_delay, execution_delay, envvars)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        operation, recipe, exec_name, early_abort, time_delay, signal_delay, execution_delay, envvars = r

        req_opts = assemble_requested_options(early_abort, time_delay, signal_delay, execution_delay)

        # actual execution
        if operation == "run":
            return recipe_processor.run_jobs_from_recipe_file(recipe, exec_name, req_opts)
        elif operation == "test":
            return recipe_processor.test_jobs_from_recipe_file(recipe, exec_name, req_opts)

        return False, "Invalid operation (or not reached)"
