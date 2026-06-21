#!/usr/bin/env python

import os

import importlib.machinery
import importlib.util

import launch_jobs
import path_utils

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "patcher"

    def _read_params(self):

        target_path = None
        target_index = None
        target_len = None
        source = None
        external_script = None

        # target_path
        try:
            target_path = self.params["target_path"]
        except KeyError:
            return False, "target_path is a required parameter"

        # target_index
        try:
            target_index = self.params["target_index"]
        except KeyError:
            pass # optional

        # target_len
        try:
            target_len = self.params["target_len"]
        except KeyError:
            pass # optional

        # source
        try:
            source = self.params["source"]
        except KeyError:
            pass # optional

        # external_script
        try:
            external_script = self.params["external_script"]
        except KeyError:
            pass # optional

        if external_script is None:

            if target_index is None:
                return False, "target_index is a required parameter (when external_script is absent)"

            if target_len is None:
                return False, "target_len is a required parameter (when external_script is absent)"

            if source is None:
                return False, "source is a required parameter (when external_script is absent)"

        return True, (target_path, target_index, target_len, source, external_script)

    def run_task(self, feedback_object, execution_name=None):

        v, r = self._read_params()
        if not v:
            return False, r
        target_path, target_index, target_len, source, external_script = r

        if not os.path.exists(target_path):
            return False, "target_path [%s] does not exist" % target_path

        if os.path.isdir(target_path):
            return False, "target_path [%s] is a folder" % target_path

        internal_process = (target_index is not None) and (target_len is not None) and (source is not None)

        if external_script is not None:

            loader = importlib.machinery.SourceFileLoader("patcher_plugin_callee_mod", external_script) # (partly) red meat
            spec = importlib.util.spec_from_loader(loader.name, loader) # pork
            mod = importlib.util.module_from_spec(spec) # pork
            loader.exec_module(mod) # pork

            try:
                di = mod.patcher_plugin_callee
                di(target_path)
            except:
                return False, "External script [%s] has no function named patcher_plugin_callee." % external_script

        if internal_process:

            contents = ""
            with open(target_path) as f:
                contents = f.read()

            target_index = int(target_index)
            target_len = int(target_len)

            if target_len == 0:
                return False, "target_len [%s] cannot be zero" % target_len

            final_pos = target_index+target_len

            if (final_pos) > len(contents):
                return False, "target_index [%s] plus target_len [%s] go past the content's total length [%s]" % (target_index, target_len, len(contents))

            new_contents = contents[0:target_index] + source + contents[target_index+target_len:]

            os.remove(target_path)

            with open(target_path, "w") as f:
                f.write(new_contents)

        return True, None
