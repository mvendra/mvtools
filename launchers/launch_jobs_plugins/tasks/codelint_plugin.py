#!/usr/bin/env python3

import os

import path_utils
import launch_jobs

import codelint

def select_suf(target_size):
    if target_size == 1:
        return ""
    else:
        return "s"

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "codelint"

    def _read_params(self):

        plugins = None
        plugins_params = None
        autocorrect = None
        files = None
        folder = None
        extensions = None

        # plugins
        try:
            plugins_read = self.params["plugins"]
            if isinstance(plugins_read, list):
                plugins = plugins_read
            else:
                plugins = [plugins_read]
        except KeyError:
            return False, "plugins is a required parameter"

        # plugins_params
        try:
            plugins_params_read = self.params["plugins_params"]
            if isinstance(plugins_params_read, list):
                plugins_params = plugins_params_read
            else:
                plugins_params = [plugins_params_read]
        except KeyError:
            pass # optional

        # autocorrect
        autocorrect = "autocorrect" in self.params

        # files
        try:
            files_read = self.params["files"]
            if isinstance(files_read, list):
                files = files_read
            else:
                files = [files_read]
        except KeyError:
            pass # (semi) optional

        # folder
        try:
            folder_read = self.params["folder"]
            if isinstance(folder_read, list):
                return False, "folder must be a (single) string"
            folder = folder_read
        except KeyError:
            pass # (semi) optional

        # extensions
        try:
            extensions_read = self.params["extensions"]
            if isinstance(extensions_read, list):
                extensions = extensions_read
            else:
                extensions = [extensions_read]
        except KeyError:
            pass # optional

        if plugins_params is not None:
            if (len(plugins_params) % 2) != 0:
                return False, "plugins_params must be of even length (would be converted into a map)"

        if files is None and folder is None:
            return False, "either files or folder must be selected"

        if files is not None and folder is not None:
            return False, "either files or folder can be selected"

        if files is not None and extensions is not None:
            return False, "extensions cannot be used with files"

        return True, (plugins, plugins_params, autocorrect, files, folder, extensions)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        plugins, plugins_params, autocorrect, files, folder, extensions = r

        plugins_params_resolved = {}

        if plugins_params is not None:
            if len(plugins_params) > 0:
                for idx in range(0, len(plugins_params), 2):
                    if plugins_params[idx] in plugins_params_resolved:
                        plugins_params_resolved[plugins_params[idx]].append(plugins_params[idx+1])
                    else:
                        plugins_params_resolved[plugins_params[idx]] = [plugins_params[idx+1]]

        if folder is not None:
            v, r = codelint.files_from_folder(folder, extensions)
            if not v:
                return False, r
            files = r

        findings_final = None
        findings_interm = []

        v, r = codelint.codelint(plugins, plugins_params_resolved, autocorrect, files)
        if not v:
            errmsg, partial_report = r
            if len(partial_report) > 0:
                feedback_object("Partially generated report:")
                for e in partial_report:
                    feedback_object(e[1])
            return False, errmsg

        for e in r:
            if e[0]:
                findings_interm.append(e[1])
            else:
                feedback_object(e[1])

        if len(findings_interm) > 0:
            findings_final = "(%s finding%s): " % (len(findings_interm), select_suf(len(findings_interm)))
            for fi in range(len(findings_interm)):
                findings_final += "#%s: %s." % ((fi+1), findings_interm[fi])
                if fi < (len(findings_interm)-1):
                    findings_final += " "

        return True, findings_final
