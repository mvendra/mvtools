#!/usr/bin/env python3

import sys
import os

import terminal_colors
import dsl_type20

import path_utils

import importlib.machinery
import importlib.util

# minimal automation framework
# dsltype20-based recipes are supported, syntax as follows:
#
# [
# @job1 {options_base}
# * step1 {options_custom} = "sample_echo_true.py"
# ]
#
# this would be a recipe file with only one job, which itself has only one step.
# job options (options_base in the example above) are inherited/merged downwards
# onto the job's steps. step options take precedence whenever there are duplications.
# by default, step scripts are searched inside MVTOOLS/launchers/launch_jobs_plugins
# this can be changed by adding the following freestanding (i.e. outside any context) variable:
# * recipe_namespace = "/home/user/custom_mvtools_launch_jobs_plugins"
#
# a recipe is deemed successful if (and only if) every single step in every single job succeeded
# a recipe may include other recipes using the following freestanding variable:
# * include_recipe = "/home/user/other_recipe.t20"
# includes are recursive.

RECIPE_INCLUDES_DEPTH_LIMITER = 100 # disallow more than 100 recursive includes

def _merge_params_downwards(p_parent, p_child):

    result = {}

    if p_parent is None and p_child is None:
        return None
    if p_parent is None and p_child is not None:
        return p_child
    if p_parent is not None and p_child is None:
        return p_parent

    for k in p_parent:
        if not k in p_child:
            result[k] = p_parent[k]

    for k in p_child:
        result[k] = p_child[k]

    return result

def _convert_dsl_opts_into_py_map(options):

    result = {}
    for o in options:
        result[o[0]] = o[1]
    return result

def _get_plugins_path(namespace=None):

    full_path = ""

    if namespace is not None:
        full_path = namespace
    else:
        mvtools_env = ""
        try:
            mvtools_env = os.environ["MVTOOLS"]
        except KeyError:
            return False, "The MVTOOLS environment variable is not defined. It is required to resolve included plugins."
        plugins_base_folder = path_utils.concat_path("launchers", "launch_jobs_plugins")
        full_path = path_utils.concat_path(mvtools_env, plugins_base_folder)

    if not os.path.exists(full_path):
        return False, "Plugins path [%s] does not exist." % full_path

    return True, full_path

def _get_step_instance(step_script, namespace=None):

    v, r = _get_plugins_path(namespace)
    if not v:
        return False, r
    script_base_path = r

    step_script_full = path_utils.concat_path(script_base_path, step_script)
    if not os.path.exists(step_script_full):
        return False, "Step script [%s] does not exist." % step_script_full

    loader = importlib.machinery.SourceFileLoader("CustomStepMod", step_script_full) # (partly) red meat
    spec = importlib.util.spec_from_loader(loader.name, loader) # pork
    mod = importlib.util.module_from_spec(spec) # pork
    loader.exec_module(mod) # pork

    try:
        di = mod.CustomStep()
    except:
        return False, "Step script [%s] has no class named CustomStep." % step_script_full

    return True, mod.CustomStep

class BaseStep:
    def __init__(self, params=None):
        self.params = params
    def get_desc(self):
        return "Generic base step"
    def run_step(self):
        return False, "Not implemented"

class BaseJob:
    def __init__(self, desc="", params=None):
        self.desc = desc
        self.params = params
        self.step_list = []

    def get_desc(self):
        return self.desc

    def add_step(self, the_step):
        the_step.params = _merge_params_downwards(self.params, the_step.params)
        self.step_list.append(the_step)

    def run_job(self):
        for s in self.step_list:
            print("run_job (%s): now running step: [%s]" % (self.get_desc(), s.get_desc()))
            v, r = s.run_step()
            if not v:
                return False, "Step [%s] failed: [%s]" % (s.get_desc(), r)
        return True, None

def run_job_list(job_list):

    for j in job_list:
        v, r = j.run_job()
        if not v:
            return False, "Job [%s] failed. Step: [%s]" % (j.get_desc(), r)
    return True, None

class RecipeProcessor:

    def __init__(self, recipe):
        self.recipe = recipe
        self._clear()

    def _clear(self):
        self.depth_counter = 0
        self.circular_tracker = []

    def run(self):

        self._clear()

        v, r = self._bootstrap_dsl_object(self.recipe)
        if not v:
            return False, r
        dsl = r

        v, r = self._translate_dsl_into_jobs(dsl)
        if not v:
            return False, r
        jobs = r

        v, r = run_job_list(jobs)
        if not v:
            return False, r

        return True, None

    def _bootstrap_dsl_object(self, local_recipe):

        if (os.path.basename(local_recipe)) in self.circular_tracker:
            return False, "Recipe file [%s]: circular inclusion detected while including [%s]." % (self.recipe, local_recipe)

        if not os.path.exists(local_recipe):
            return False, "Recipe file [%s] does not exist." % local_recipe

        file_contents = None
        with open(local_recipe) as f:
            file_contents = f.read()
        if file_contents is None or file_contents == "":
            return False, "Recipe file [%s]'s contents are invalid." % local_recipe

        dsl_opts = dsl_type20.DSLType20_Options(expand_envvars = True, expand_user = True, allow_dupes = True, vars_auto_ctx_options=False, variable_decorator = "* ")
        dsl = dsl_type20.DSLType20(dsl_opts)

        v, r = dsl.parse(file_contents)
        if not v:
            return False, r

        self.circular_tracker.append(os.path.basename(local_recipe))
        return True, dsl

    def _translate_dsl_into_jobs(self, dsl):

        self.depth_counter += 1
        if self.depth_counter > RECIPE_INCLUDES_DEPTH_LIMITER:
            return False, "Base recipe file [%s]: depth limit exceeded." % self.recipe

        namespace = None
        jobs = []

        # recipe namespace (for steps/plugins)
        var_rn = dsl.get_vars("recipe_namespace")
        if len(var_rn) > 0:
            namespace = var_rn[0][1]

        # recipe includes
        for var_ir in dsl.get_vars("include_recipe"):
            v, r = self._bootstrap_dsl_object(var_ir[1])
            if not v:
                return False, r
            v, r = self._translate_dsl_into_jobs(r)
            if not v:
                return False, r
            jobs += r

        for ctx in dsl.get_all_contexts():

            job_params = _convert_dsl_opts_into_py_map(dsl.get_context_options(ctx))
            new_job = BaseJob(ctx, job_params)

            for var in dsl.get_all_vars(ctx):

                # var[0] is currently not used for anything (the variable name)

                step_params = _convert_dsl_opts_into_py_map(var[2])

                v, r = _get_step_instance(var[1], namespace)
                if not v:
                    return False, r

                new_step = r(step_params)
                new_job.add_step(new_step)

            jobs.append(new_job)

        self.depth_counter -= 1
        return True, jobs

def run_jobs_from_recipe_file(recipe_file):
    recipe_processor = RecipeProcessor(recipe_file)
    return recipe_processor.run()

def puaq():
    print("Usage: %s recipe.t20" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    recipe_file = sys.argv[1]
    v, r = run_jobs_from_recipe_file(recipe_file)
    if not v:
        print("%sExecution of recipe [%s] failed: [%s]%s" % (terminal_colors.TTY_RED, recipe_file, r, terminal_colors.TTY_WHITE))
    else:
        print("%sExecution of recipe [%s] succeeded.%s" % (terminal_colors.TTY_GREEN, recipe_file, terminal_colors.TTY_WHITE))
