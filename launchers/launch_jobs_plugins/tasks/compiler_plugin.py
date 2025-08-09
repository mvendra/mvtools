#!/usr/bin/env python3

import os

import path_utils
import launch_jobs
import gcc_wrapper

class CustomTask(launch_jobs.BaseTask):

    def get_desc(self):
        return "compiler"

    def _read_params(self):

        compiler_base = None
        compiler = None
        params = []

        # compiler_base
        try:
            compiler_base = self.params["compiler_base"]
        except KeyError:
            pass # optional

        # compiler
        try:
            compiler = self.params["compiler"]
        except KeyError:
            return False, "compiler is a required parameter"

        # params
        try:
            params_read = self.params["params"]
            if isinstance(params_read, list):
                params = params_read
            else:
                params.append(params_read)
        except KeyError:
            return False, "params is a required parameter"

        if compiler_base is not None:
            if not os.path.exists(compiler_base):
                return False, "compiler_base [%s] does not exist" % compiler_base

        valid_compilers = {}
        valid_compilers["gcc"] = gcc_wrapper

        if not compiler in valid_compilers:
            return False, "Compiler [%s] is unknown/not supported" % compiler

        return True, (compiler_base, valid_compilers[compiler], params)

    def run_task(self, feedback_object, execution_name=None):

        # read params
        v, r = self._read_params()
        if not v:
            return False, r
        compiler_base, compiler, params = r

        # actual execution
        v, r = compiler.exec(compiler_base, params)
        if not v:
            return False, r
        return True, None
