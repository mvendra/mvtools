#!/usr/bin/env python3

import sys
import os

import importlib.machinery
import importlib.util

import launch_jobs
import dsl_type20

import standard_job

import path_utils
import terminal_colors

import mvtools_envvars

# minimal automation framework
# dsltype20-based recipes are supported, syntax as follows:
#
# [
# @job1 {options_base}
# * task1 {options_custom} = "sample_echo_true.py"
# ]
#
# this would be a recipe file with only one job, which itself has only one task (task1)
# job options (options_base in the example above) are inherited/merged downwards
# onto the job's tasks. task options take precedence whenever there are duplications.
# a recipe is deemed successful if (and only if) every single task in every single job
# succeeded (some exceptions may apply - see below)
#
# by default, task scripts are searched inside MVTOOLS/launchers/launch_jobs_plugins/tasks
# this can be changed by adding the following freestanding (i.e. outside any context) variable:
# * recipe_namespace = "/home/user/custom_mvtools_launch_jobs_plugins"
# it operates in two modes: exclusive mode (which is the default) and inclusive mode.
# in exclusive mode, scripts will only be searched inside the specified path. in inclusive
# mode, scripts will first be searched inside the built-in plugins
# folder (MVTOOLS/launchers/launch_jobs_plugins/tasks), and if its not found there, then, and
# only then, the custom path will be searched. example:
# * recipe_namespace {inclusive} = "/home/user/custom_mvtools_launch_jobs_plugins"
# it is not necessary to explicitly set "exclusive" to activate the exclusive mode, because
# it is the default.
#
# it is possible to define launch_jobs's execution options either via commandline
# arguments (requested options) or using freestanding variables inside the recipe (which
# will overwrite the commandline options when specified):
#
# * execution name = "exec-name" # this will define the execution name that will be written
# to the launch_jobs toolbus database
#
# * early_abort = "true" # "true" or "false" are accepted - exclusively
# this will specify whether an execution should be aborted whenever any job fails. the execution
# itself will be deemed a failure upon any job failure, but with this option enabled, the execution
# will nonetheless continue until there are no more jobs in the list.
#
# * time_delay = "1h" # defines a pre-execution delay. examples: "7h", "30m", "15".
#
# * signal_delay = "sig-name" # defines a toolbus internal signal to be waited for before starting this
# execution. the signal gets consumed upon availability.
#
# * execution_delay = "exec-name" # defines a toolbus launch_jobs database-registered execution name
# to be waited for before starting this execution. this will cause this execution to be delayed *until*
# the defined execution name is concluded (i.e. has bee removed from launch_jobs's toolbus database)
#
# a recipe may include other recipes using the following freestanding variable:
# * include_recipe = "/home/user/other_recipe.t20"
# includes are recursive. included recipes can have their own namespaces.
#
# it is possible to override the standard job (jobs/standard_job.py) default implementation
# by using the following syntax:
#
# [
# @job1 {mvtools_recipe_processor_plugin_job: "custom_job_impl.py"}
# * task1 = "sample_echo_true.py"
# ]
#
# which makes the option "mvtools_recipe_processor_plugin_job" not available for
# custom/general use (i.e. not usable by task plugins)

RECIPE_INCLUDES_DEPTH_LIMITER = 100 # disallow more than 100 recursive includes

def _conditional_write(source1, source2):
    if source2 is not None:
        return source2
    return source1

def _convert_dsl_opts_into_py_map(options):

    result = {}
    for o in options:
        if o[0] in result: # repeated option. stack it up. dupes are allowed.
            val_read = result[o[0]]
            if not isinstance(val_read, list):
                result[o[0]] = [val_read] # re-set this entry as a list, with the previously existing item as the first item in it
            result[o[0]].append(o[1])
        else:
            result[o[0]] = o[1]
    return result

def _get_plugins_path(namespace=None):

    full_path = ""

    if namespace is not None:
        full_path = namespace
    else:

        v, r = mvtools_envvars.mvtools_envvar_read_main()
        if not v:
            return False, "The main MVTOOLS environment variable is not defined. It is required to resolve included plugins."
        mvtools_env = r

        plugins_base_folder = path_utils.concat_path("launchers", "launch_jobs_plugins")
        full_path = path_utils.concat_path(mvtools_env, plugins_base_folder)

    if not os.path.exists(full_path):
        return False, "Plugins path [%s] does not exist." % full_path

    return True, full_path

def _get_task_instance(task_script, namespace=None):

    if namespace is None:
        return _get_task_instance_delegate(task_script, None)

    if namespace[1]: # exclusive mode - only the custom namespace is tried
        return _get_task_instance_delegate(task_script, namespace[0])
    else: # inclusive mode - first the built-in namespace is tried, and if that fails, then the custom namespace is tried
        v, r = _get_task_instance_delegate(task_script, None)
        if not v:
            return _get_task_instance_delegate(task_script, namespace[0])
        return v, r

def _get_task_instance_delegate(task_script, namespace):

    v, r = _get_plugins_path(namespace)
    if not v:
        return False, r
    script_base_path = r
    if namespace is None:
        script_base_path = path_utils.concat_path(r, "tasks")

    task_script_full = path_utils.concat_path(script_base_path, task_script)
    if not os.path.exists(task_script_full):
        return False, "Task script [%s] does not exist." % task_script_full

    loader = importlib.machinery.SourceFileLoader("CustomTaskMod", task_script_full) # (partly) red meat
    spec = importlib.util.spec_from_loader(loader.name, loader) # pork
    mod = importlib.util.module_from_spec(spec) # pork
    loader.exec_module(mod) # pork

    try:
        di = mod.CustomTask()
    except:
        return False, "Task script [%s] has no class named CustomTask." % task_script_full

    return True, mod.CustomTask

def _get_job_instance(job_params, namespace=None):

    if namespace is None:
        return _get_job_instance_delegate(job_params, None)

    if namespace[1]: # exclusive mode - only the custom namespace is tried
        return _get_job_instance_delegate(job_params, namespace[0])
    else: # inclusive mode - first the built-in namespace is tried, and if that fails, then the custom namespace is tried
        v, r = _get_job_instance_delegate(job_params, None)
        if not v:
            return _get_job_instance_delegate(job_params, namespace[0])
        return v, r

def _get_job_instance_delegate(job_params, namespace):

    if not "mvtools_recipe_processor_plugin_job" in job_params:
        return True, standard_job.StandardJob
    job_script = job_params["mvtools_recipe_processor_plugin_job"]

    v, r = _get_plugins_path(namespace)
    if not v:
        return False, r
    script_base_path = r
    if namespace is None:
        script_base_path = path_utils.concat_path(r, "jobs")

    job_script_full = path_utils.concat_path(script_base_path, job_script)
    if not os.path.exists(job_script_full):
        return False, "Job script [%s] does not exist." % job_script_full

    loader = importlib.machinery.SourceFileLoader("CustomJobMod", job_script_full) # (partly) red meat
    spec = importlib.util.spec_from_loader(loader.name, loader) # pork
    mod = importlib.util.module_from_spec(spec) # pork
    loader.exec_module(mod) # pork

    try:
        di = mod.CustomJob()
    except:
        return False, "Job script [%s] has no class named CustomJob." % job_script_full

    return True, mod.CustomJob

class RecipeProcessor:

    def __init__(self, recipe, requested_options):
        self.recipe = recipe
        self.requested_options = requested_options
        self._clear()

    def _clear(self):
        self.depth_counter = 0
        self.circular_tracker = []

    def test(self, requested_execution_name=None):

        self._clear()

        v, r = self._bootstrap_dsl_object(self.recipe)
        if not v:
            return False, r
        dsl = r

        v, r = self._translate_dsl_into_jobs(dsl)
        if not v:
            return False, r
        jobs = r

        v, r = self._get_launch_options_from_recipe(dsl)
        if not v:
            return False, r
        options = r

        v, r = self._resolve_options(options)
        if not v:
            return False, r
        options = r

        v, r = self._get_exec_name_from_recipe(dsl)
        if not v:
            return False, r
        exec_name = r

        v, r = self._resolve_exec_name(requested_execution_name, exec_name)
        if not v:
            return False, r
        exec_name = r

        return True, (jobs, options, exec_name)

    def run(self, requested_execution_name=None):

        self._clear()

        v, r = self.test(requested_execution_name)
        if not v:
            return False, r

        jobs = r[0]
        options = r[1]
        exec_name = r[2]

        v, r = launch_jobs.run_job_list(jobs, print, exec_name, options)
        if not v:
            return False, r

        return True, None

    def _bootstrap_dsl_object(self, local_recipe):

        if (path_utils.basename_filtered(local_recipe)) in self.circular_tracker:
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

        self.circular_tracker.append(path_utils.basename_filtered(local_recipe))
        return True, dsl

    def _translate_dsl_into_jobs(self, dsl):

        self.depth_counter += 1
        if self.depth_counter > RECIPE_INCLUDES_DEPTH_LIMITER:
            return False, "Base recipe file [%s]: depth limit exceeded." % self.recipe

        namespace = None
        jobs = []

        # recipe namespace (for tasks/plugins)
        var_rn = dsl.get_vars("recipe_namespace")
        if len(var_rn) > 1:
            return False, "Recipe's recipe_namespace has been specified multiple times."
        elif len(var_rn) == 1:
            namespace_path = var_rn[0][1]
            namespace_opt = var_rn[0][2]
            namespace_opt_v = True # exclusive mode (default)
            for opts in namespace_opt:
                if opts[0] == "inclusive":
                    namespace_opt_v = False # disable exclusive mode
            namespace = (namespace_path, namespace_opt_v)

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
            v, r = _get_job_instance(job_params, namespace)
            if not v:
                return False, r
            new_job = r(ctx, job_params)

            for var in dsl.get_all_vars(ctx):

                task_params = _convert_dsl_opts_into_py_map(var[2])

                v, r = _get_task_instance(var[1], namespace)
                if not v:
                    return False, r

                new_task = r(var[0], task_params)
                new_job.add_task(new_task)

            jobs.append(new_job)

        self.depth_counter -= 1
        return True, jobs

    def _lowercase_str_option_value_filter(self, opt_val):
        return opt_val.lower()

    def _lowercase_bool_option_value_filter(self, opt_val):
        local_opt_val = opt_val.lower()
        if local_opt_val == "yes":
            return True
        elif local_opt_val == "no":
            return False
        return None

    def _get_launch_options_helper(self, dsl, option, valid_values, value_filter_function):

        local_option = None

        var_rn = dsl.get_vars(option)
        if len(var_rn) > 1: # has been specified more than once. fail.
            return False, "Recipe's %s option has been specified more than once." % option
        elif len(var_rn) == 1: # has been specified once in the recipe file
            unfiltered_val = var_rn[0][1]
            filtered_val = value_filter_function(unfiltered_val)
            if valid_values is not None:
                if not filtered_val in valid_values:
                    return False, "Recipe's %s option has an invalid value: [%s]" % (option, unfiltered_val)
            local_option = filtered_val

        return True, local_option

    def _get_launch_options_from_recipe(self, dsl):

        local_early_abort = None
        local_time_delay = None
        local_signal_delay = None
        local_execution_delay = None

        # early abort option
        v, r = self._get_launch_options_helper(dsl, "early-abort", [True, False], self._lowercase_bool_option_value_filter)
        if not v:
            return False, r
        local_early_abort = r

        # time delay option
        v, r = self._get_launch_options_helper(dsl, "time-delay", None, self._lowercase_str_option_value_filter)
        if not v:
            return False, r
        local_time_delay = r

        # signal delay option
        v, r = self._get_launch_options_helper(dsl, "signal-delay", None, self._lowercase_str_option_value_filter)
        if not v:
            return False, r
        local_signal_delay = r

        # execution delay option
        v, r = self._get_launch_options_helper(dsl, "execution-delay", None, self._lowercase_str_option_value_filter)
        if not v:
            return False, r
        local_execution_delay = r

        return True, launch_jobs.RunOptions(early_abort=local_early_abort, time_delay=local_time_delay, signal_delay=local_signal_delay, execution_delay=local_execution_delay)

    def _resolve_options(self, options):

        # resolve/validate options, particularly between requested (commandline-specified) options, and recipe-specified options
        local_options = launch_jobs.RunOptions() # default options
        if self.requested_options is None:
            if options is None:
                return True, local_options
            local_options.early_abort = _conditional_write(local_options.early_abort, options.early_abort)
            local_options.time_delay = _conditional_write(local_options.time_delay, options.time_delay)
            local_options.signal_delay = _conditional_write(local_options.signal_delay, options.signal_delay)
            local_options.execution_delay = _conditional_write(local_options.execution_delay, options.execution_delay)
            return True, local_options

        local_options.early_abort = _conditional_write(local_options.early_abort, self.requested_options.early_abort)
        local_options.time_delay = _conditional_write(local_options.time_delay, self.requested_options.time_delay)
        local_options.signal_delay = _conditional_write(local_options.signal_delay, self.requested_options.signal_delay)
        local_options.execution_delay = _conditional_write(local_options.execution_delay, self.requested_options.execution_delay)

        local_options.early_abort = _conditional_write(local_options.early_abort, options.early_abort)
        if options.early_abort is not None and self.requested_options.early_abort is not None:
            print("%sWarning: the [early-abort] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.early_abort, terminal_colors.TTY_WHITE))

        local_options.time_delay = _conditional_write(local_options.time_delay, options.time_delay)
        if options.time_delay is not None and self.requested_options.time_delay is not None:
            print("%sWarning: the [time-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.time_delay, terminal_colors.TTY_WHITE))

        local_options.signal_delay = _conditional_write(local_options.signal_delay, options.signal_delay)
        if options.signal_delay is not None and self.requested_options.signal_delay is not None:
            print("%sWarning: the [signal-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.signal_delay, terminal_colors.TTY_WHITE))

        local_options.execution_delay = _conditional_write(local_options.execution_delay, options.execution_delay)
        if options.execution_delay is not None and self.requested_options.execution_delay is not None:
            print("%sWarning: the [execution-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.execution_delay, terminal_colors.TTY_WHITE))

        return True, local_options

    def _get_exec_name_from_recipe(self, dsl):

        var_rn = dsl.get_vars("execution-name")
        if len(var_rn) > 1:
            return False, "Recipe's execution-name has been specified more than once."
        elif len(var_rn) == 1:
            return True, (var_rn[0][1])
        return True, None

    def _resolve_exec_name(self, requested_execution_name, recipe_execution_name):

        local_exec_name = None

        local_exec_name = _conditional_write(local_exec_name, requested_execution_name)
        local_exec_name = _conditional_write(local_exec_name, recipe_execution_name)

        if requested_execution_name is not None and recipe_execution_name is not None:
            print("%sWarning: the [execution-name] has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_exec_name, terminal_colors.TTY_WHITE))

        return True, local_exec_name

def test_jobs_from_recipe_file(recipe_file, execution_name=None, requested_options=None):
    recipe_processor = RecipeProcessor(recipe_file, requested_options)
    return recipe_processor.test(execution_name)

def run_jobs_from_recipe_file(recipe_file, execution_name=None, requested_options=None):
    recipe_processor = RecipeProcessor(recipe_file, requested_options)
    return recipe_processor.run(execution_name)

def assemble_requested_options(_early_abort, _time_delay, _signal_delay, _execution_delay):
    return launch_jobs.RunOptions(early_abort=_early_abort, time_delay=_time_delay, signal_delay=_signal_delay, execution_delay=_execution_delay)

def menu_test_recipe(recipe_file, execution_name, requested_options):

    v, r = test_jobs_from_recipe_file(recipe_file, execution_name, requested_options)
    if not v:
        err_msg = r
        if len(err_msg) == 1:
            err_msg = err_msg[0]
        print("%sTesting of recipe [%s] failed: [%s]%s" % (terminal_colors.TTY_RED, recipe_file, err_msg, terminal_colors.TTY_WHITE))
    else:
        print("%sTesting of recipe [%s] succeeded.%s" % (terminal_colors.TTY_GREEN, recipe_file, terminal_colors.TTY_WHITE))

def menu_run_recipe(recipe_file, execution_name, requested_options):

    v, r = run_jobs_from_recipe_file(recipe_file, execution_name, requested_options)
    if not v:
        err_msg = r
        if len(err_msg) == 1:
            err_msg = err_msg[0]
        print("%sExecution of recipe [%s] failed: [%s]%s" % (terminal_colors.TTY_RED, recipe_file, err_msg, terminal_colors.TTY_WHITE))
    else:
        print("%sExecution of recipe [%s] succeeded.%s" % (terminal_colors.TTY_GREEN, recipe_file, terminal_colors.TTY_WHITE))

def puaq():
    print("Usage: %s [--test recipe.t20 | --run recipe.t20] --execution-name the-execution-name --early-abort yes/no --time-delay the-time-delay --signal-delay the-signal-delay --execution-delay the-execution-delay" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()
    params = sys.argv[1:]

    operation = None
    recipe_next = False
    recipe_file = None

    # launch_jobs options
    execution_name = None
    execution_name_next = False
    early_abort = None
    early_abort_next = False
    time_delay = None
    time_delay_next = False
    signal_delay = None
    signal_delay_next = False
    execution_delay = None
    execution_delay_next = False

    for p in params:

        if recipe_next:
            recipe_next = False
            recipe_file = p
            continue

        if execution_name_next:
            execution_name_next = False
            execution_name = p
            continue

        if early_abort_next:
            early_abort_next = False
            if p == "yes":
                early_abort = True
            elif p == "no":
                early_abort = False
            else:
                print("Option [--early-abort] received an invalid value: [%s]. Valid values are [yes/no]" % p)
                sys.exit(1)
            continue

        if time_delay_next:
            time_delay_next = False
            time_delay = p
            continue

        if signal_delay_next:
            signal_delay_next = False
            signal_delay = p
            continue

        if execution_delay_next:
            execution_delay_next = False
            execution_delay = p
            continue

        if p == "--test":
            if operation is not None:
                print("Operation should only be specified once (either --test or --run)")
                sys.exit(1)
            operation = "test"
            recipe_next = True
        elif p == "--run":
            if operation is not None:
                print("Operation should only be specified once (either --test or --run)")
                sys.exit(1)
            operation = "run"
            recipe_next = True
        elif p == "--execution-name":
            execution_name_next = True
        elif p == "--early-abort":
            early_abort_next = True
        elif p == "--time-delay":
            time_delay_next = True
        elif p == "--signal-delay":
            signal_delay_next = True
        elif p == "--execution-delay":
            execution_delay_next = True
        else:
            print("Invalid commandline argument: [%s]" % p)
            sys.exit(1)

    req_opts = assemble_requested_options(early_abort, time_delay, signal_delay, execution_delay)

    if operation == "test":
        menu_test_recipe(recipe_file, execution_name, req_opts)
    elif operation == "run":
        menu_run_recipe(recipe_file, execution_name, req_opts)
    else:
        print("Invalid operation: [%s]" % operation)
        sys.exit(1)
