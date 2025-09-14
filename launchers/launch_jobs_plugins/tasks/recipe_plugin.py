#!/usr/bin/env python

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

        local_params = self.params.copy()

        # operation
        local_run = "run" in local_params
        local_test = "test" in local_params
        if local_run and local_test:
            return False, "Specify only either run or test - not both"
        if not local_run and not local_test:
            return False, "Specify at least either run or test"

        if local_run:
            operation = "run"
            del local_params["run"]
        elif local_test:
            operation = "test"
            del local_params["test"]

        # recipe
        try:
            recipe = local_params["recipe"]
            del local_params["recipe"]
        except KeyError:
            return False, "recipe is a required parameter"

        # exec_name
        try:
            exec_name = local_params["exec_name"]
            del local_params["exec_name"]
        except KeyError:
            pass # optional

        # early_abort
        try:
            early_abort = local_params["early_abort"]
            del local_params["early_abort"]
        except KeyError:
            pass # optional

        # time_delay
        try:
            time_delay = local_params["time_delay"]
            del local_params["time_delay"]
        except KeyError:
            pass # optional

        # signal_delay
        try:
            signal_delay = local_params["signal_delay"]
            del local_params["signal_delay"]
        except KeyError:
            pass # optional

        # execution_delay
        try:
            execution_delay = local_params["execution_delay"]
            del local_params["execution_delay"]
        except KeyError:
            pass # optional

        # envvars
        for ev in local_params:
            if not isinstance(local_params[ev], str): # reject stacked options: envvars can only hold one single value
                return False, "envvar [%s] rejected - stacked option. Choose only one value for its option" % ev
            envvars.append( (ev, local_params[ev]) )

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

        # handle early_abort translation
        local_early_abort = None
        if early_abort == "no":
            local_early_abort = False
        elif early_abort == "yes":
            local_early_abort = True
        req_opts = recipe_processor.assemble_requested_options(local_early_abort, time_delay, signal_delay, execution_delay)

        # keep a copy and update envvars
        envvars_copy = os.environ.copy()
        for ev in envvars:
            os.environ[ev[0]] = ev[1]

        v, r = self.run_task_delegate(operation,recipe, exec_name, req_opts)

        # restore envvars
        os.environ.clear()
        os.environ.update(envvars_copy)

        return v, r

    def run_task_delegate(self, operation, recipe, exec_name, req_opts):

        # actual execution
        if operation == "run":
            return recipe_processor.run_jobs_from_recipe_file(recipe, exec_name, req_opts)
        elif operation == "test":
            v, r = recipe_processor.test_jobs_from_recipe_file(recipe, exec_name, req_opts)
            # below: recipe_processor.test_jobs_from_recipe_file returns extra info on the second parameter upon success
            if not v:
                return False, r
            return True, None

        return False, "Invalid operation (or not reached)"
