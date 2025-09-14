#!/usr/bin/env python

import os

import launch_jobs
import toolbus
import retry

def _check_signal(signal_name):
    v, r = toolbus.get_signal(signal_name) # signal will be consumed
    return v, not (r == None)

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "toolbus"

    def _read_params(self):

        operation = None
        signal_name = None
        signal_value = None

        # operation
        try:
            operation = self.params["operation"]
        except:
            return False, "operation is a required parameter"

        # signal_name
        try:
            signal_name = self.params["signal_name"]
        except:
            return False, "signal_name is a required parameter"

        # signal_value
        try:
            signal_value = self.params["signal_value"]
        except:
            pass # optional

        return True, (operation, signal_name, signal_value)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        operation, signal_name, signal_value = r

        if operation == "set_signal":
            return self.set_signal(feedback_object, signal_name, signal_value)
        elif operation == "wait_signal":
            return self.wait_signal(feedback_object, signal_name)
        else:
            return False, "Invalid operation: [%s]" % operation

    def set_signal(self, feedback_object, signal_name, signal_value):

        if signal_value is None:
            return False, "signal_value is a required parameter for the set_signal operation"

        v, r = toolbus.set_signal(signal_name, signal_value)
        if not v:
            return False, "Unable to set signal: [%s]" % r
        return True, None

    def wait_signal(self, feedback_object, signal_name):

        feedback_object("Will wait on signal [%s]" % signal_name)

        retry_opts = {"retries_max": 800000, "retry_sleep_random": 2000}
        v, r = retry.retry(retry_opts, _check_signal, signal_name)
        if not v:
            return False, "Failed retrying on %s [%s]: [%s]" % (wait_object_name, wait_object, r)
        return True, None
