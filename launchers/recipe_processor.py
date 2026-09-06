#!/usr/bin/env python

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

ERROR_CODE_NONE = 0
ERROR_CODE_INPUT = 1
ERROR_CODE_SOFT_FAIL = 2
ERROR_CODE_HARD_FAIL = 3

# minimal automation framework
# dsltype20-based recipes are supported, syntax as follows:
#
# [
# @job1 {job_options}
# * task1 {task_options} = "sample_echo_true.py"
# ]
#
# this would be a recipe file with only one job, which itself has only one task (task1)
# tasks can be "freestanding" (i.e. they don't require being a member of any context), and nested
# contexts are supported - examples below:
#
# * freestanding-task {task_options} = "sample_echo_true.py"
#
# [
# @job1 {job_options}
#
#     [
#     @nested-job2
#     * another-task = "sample_echo_true.py"
#     ]
#
# ]
#
# job options (job_options in the example above) are inherited/merged downwards onto the job's tasks.
# a recipe is deemed successful if (and only if) every single task in every single job
# succeeded (some exceptions may apply - see below)
#
# recipes can be configured by adding certain variables to a metajob called "mvtools_recipe_processor_config"
# by default, task scripts are searched for inside MVTOOLS/launchers/launch_jobs_plugins/tasks
# this can be changed by adding the following config variable to the recipe config metajob:
#
# [
# @mvtools_recipe_processor_config
# * namespace = "/home/user/custom_mvtools_launch_jobs_plugins"
# ]
#
# it operates in two modes: exclusive mode (which is the default) and inclusive mode.
# in exclusive mode, scripts will only be searched inside the specified path. in inclusive
# mode, scripts will first be searched inside the built-in plugins
# folder (MVTOOLS/launchers/launch_jobs_plugins/tasks), and if its not found there, then, and
# only then, the custom path will be searched. example:
# * namespace {inclusive} = "/home/user/custom_mvtools_launch_jobs_plugins"
# it is not necessary to explicitly set "exclusive" to activate the exclusive mode, because it is the default.
#
# it is possible to define launch_jobs's execution options either via commandline
# arguments (requested options) or using config variables inside the recipe's metajob (which
# will overwrite the commandline options when specified):
#
# [
# @mvtools_recipe_processor_config
# * execution-name = "exec-name"
# * early-abort = "yes"
# * time-delay = "1h"
# * signal-delay = "sig-name"
# * execution-delay = "exec-name"
# ]
#
# * execution-name # this will define the execution name that will be written to the launch_jobs toolbus database
#
# * early-abort # "yes" or "no" are accepted - exclusively
# this will specify whether an execution should be aborted whenever any job fails. the execution
# itself will be deemed a failure upon any job failure, but with this option enabled, the execution
# will nonetheless continue until there are no more jobs in the list.
#
# * time-delay # defines a pre-execution delay. examples: "7h", "30m", "15".
#
# * signal-delay # defines a toolbus internal signal to be waited for before starting this
# execution. the signal gets consumed upon availability.
#
# * execution-delay # defines a toolbus launch_jobs database-registered execution name
# to be waited for before starting this execution. this will cause this execution to be delayed *until*
# the defined execution name is concluded (i.e. has bee removed from launch_jobs's toolbus database)
#
# it is possible to override the standard job (jobs/standard_job.py) default implementation
# by using the following syntax:
#
# [
# @mvtools_recipe_processor_config
# * custom-job-implementation {job1} = "custom_job_impl.py"
# ]
#
# [
# @job1
# * task1 = "sample_echo_true.py"
# ]
#
# [
# @job2
# * task1 = "sample_echo_true.py"
# ]
#
# in the example above, job1's implementation would be replaced with "custom_job_impl.py", whereas the default
# job implementation would be preserved for job2.
# it is also possible to replace the implementation of the main/"invisible" job (the underlying job that parents
# "freestanding" tasks, and all other jobs as well) - by using the following syntax:
#
# [
# @mvtools_recipe_processor_config
# * custom-main-job-implementation = "custom_job_impl.py"
# ]
#

def _has_incl_opt(opts):
    for o in opts:
        if o.name == "inclusive":
            return True
    return False

def _translate_namespace_mode(mode_val):
    if mode_val:
        return "exclusive"
    else:
        return "inclusive"

def _lowercase_str_option_value_filter(opt_val):
    return opt_val.lower()

def _lowercase_bool_option_value_filter(opt_val):
    local_opt_val = opt_val.lower()
    if local_opt_val == "yes":
        return True
    elif local_opt_val == "no":
        return False
    return None

def _conditional_write(source1, source2):
    if source2 is not None:
        return source2
    return source1

def _convert_opt_values_to_param_values(input_opt_value):
    # backwards compatibility (towards plugins)
    if len(input_opt_value) == 0:
        return None
    elif len(input_opt_value) == 1:
        return input_opt_value[0]
    else:
        return input_opt_value

def _convert_dsl_opts_into_py_map(options):
    result = {}
    for o in options:
        result[o.name] = _convert_opt_values_to_param_values(o.values)
    return result

def _get_custom_job_from_opts_and_leftovers_as_params(opts):
    custom_impl = None
    param_map = {}
    for o in opts:
        if o.name == "impl":
            if len(o.values) != 1:
                return False, "A custom job implementation, when used, must be specified with a single value."
            custom_impl = o.values[0]
        else:
            param_map[o.name] = _convert_opt_values_to_param_values(o.values)
    return True, (custom_impl, param_map)

def _get_scripts_path(namespace = None):

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

def _get_task_instance(task_script, namespace = None):

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

    v, r = _get_scripts_path(namespace)
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

def _get_job_instance(job_script, namespace = None):

    if job_script is None:
        return True, standard_job.StandardJob

    if namespace is None:
        return _get_job_instance_delegate(job_script, None)

    if namespace[1]: # exclusive mode - only the custom namespace is tried
        return _get_job_instance_delegate(job_script, namespace[0])
    else: # inclusive mode - first the built-in namespace is tried, and if that fails, then the custom namespace is tried
        v, r = _get_job_instance_delegate(job_script, None)
        if not v:
            return _get_job_instance_delegate(job_script, namespace[0])
        return v, r

def _get_job_instance_delegate(job_script, namespace):

    v, r = _get_scripts_path(namespace)
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

DEPTH_TRACKER_LIMIT = 200
class RecipeProcessor:

    def __init__(self, recipe, namespace, requested_options):
        self.recipe = recipe
        self.namespace = namespace
        self.requested_options = requested_options

    def test(self, entrypoint, requested_execution_name = None):

        dsl = None
        jobs = None
        options = None
        exec_name = None
        entrypoint_context_cache = None

        v, r = self._bootstrap_dsl_object()
        if not v:
            return False, r
        dsl = r

        v, r = self._preload_entrypoint_from_dsl(dsl, entrypoint)
        if not v:
            return False, r
        entrypoint_context_cache = r

        v, r = self._get_exec_name_from_recipe(entrypoint_context_cache)
        if not v:
            return False, r
        exec_name = r

        v, r = self._resolve_exec_name(requested_execution_name, exec_name)
        if not v:
            return False, r
        exec_name = r

        v, r = self._get_launch_options_from_recipe(entrypoint_context_cache)
        if not v:
            return False, r
        options = r

        v, r = self._resolve_options(options)
        if not v:
            return False, r
        options = r

        v, r = self._build_jobtree_from_dsl(dsl, entrypoint_context_cache)
        if not v:
            return False, r
        jobs = r

        return True, (jobs, options, exec_name)

    def run(self, entrypoint, requested_execution_name = None):

        v, r = self.test(entrypoint, requested_execution_name)
        if not v:
            return False, r

        mainjob = r[0]
        options = r[1]
        exec_name = r[2]

        v, r = launch_jobs.begin_execution(mainjob, print, exec_name, options)
        return v, r

    def _bootstrap_dsl_object(self):

        if not os.path.exists(self.recipe):
            return False, "Recipe file [%s] does not exist." % self.recipe

        file_contents = None
        with open(self.recipe) as f:
            file_contents = f.read()
        if file_contents is None or file_contents == "":
            return False, "Recipe file [%s]'s contents are invalid." % self.recipe

        dsl_opts = dsl_type20.DSLType20_Config(expand_envvars = True, expand_user = True, allow_var_dupes = True, inherit_options = True, var_decorator = "* ")
        dsl = dsl_type20.DSLType20(dsl_opts)

        v, r = dsl.parse(file_contents)
        if not v:
            return False, r

        return True, dsl

    def _preload_entrypoint_from_dsl(self, dsl, entrypoint):

        if entrypoint is None:
            entrypoint = "main"

        # read out main/entrypoint metadata
        v, r = dsl.get_all_variables(entrypoint)
        return v, r

    def __load_tasks_onto_job(self, dsl, source_ctx_name, target_job):

        # read out current job's task
        v, r = dsl.get_all_variables(source_ctx_name)
        if not v:
            return False, r
        source_entries = r

        for entry in source_entries:

            if len(entry.variable.values) != 1:
                return False, "Invalid task source specification (must be a single value): [%s]" % entry.variable.values

            v, r = _get_task_instance(entry.variable.values[0], self.namespace)
            if not v:
                return False, r
            new_task = r(entry.variable.name, _convert_dsl_opts_into_py_map(entry.options))
            target_job.add_entry(new_task)

        return True, None

    def __load_new_job(self, dsl, source_var, parent_job):

        # select sub job implementation
        v, r = _get_custom_job_from_opts_and_leftovers_as_params(source_var.options)
        if not v:
            return False, r
        job_impl_to_use, job_params = r

        for val in source_var.variable.values:

            if not len(val) > 1:
                return False, "Invalid job name: [%s]" % val

            if not val[0] == "@":
                return False, "Invalid job name (specified without prefixed @ sign: [%s]" % val

            # instantiate new/current job
            v, r = _get_job_instance(job_impl_to_use, self.namespace)
            if not v:
                return False, r
            new_job = r(val[1:], job_params)

            # load up tasks onto the new job
            v, r = self.__load_tasks_onto_job(dsl, val[1:], new_job)
            if not v:
                return False, r

            parent_job.add_entry(new_job)

        return True, None

    def _build_jobtree_from_dsl(self, dsl, entrypoint_context_cache):

        namespace_switch = self.namespace is not None
        main_job = None

        for var in entrypoint_context_cache:

            if var.variable.name == "main-job-impl":

                if main_job is not None:
                    return False, "A custom implementation for the main job, when specified, must precede any job definitions in the entrypoint (main job), and only be defined once."

                if len(var.variable.values) != 1:
                    return False, "A custom implementation for the main job, when specified, must be given as a single value."

                # instantiate main job with custom implementation
                v, r = _get_job_instance(var.variable.values[0], self.namespace)
                if not v:
                    return False, r
                main_job = r(None, _convert_dsl_opts_into_py_map(var.options))

            elif var.variable.name == "namespace":

                if len(var.variable.values) != 1:
                    return False, "One (and only one) custom namespace must/may be specified per entry."

                namespace_mode = True # exclusive mode - the default
                if _has_incl_opt(var.options):
                    namespace_mode = False
                self.namespace = (var.variable.values[0], namespace_mode)
                if namespace_switch:
                    print("%sWarning: the [--namespace] switch has been overridden by the recipe with value [%s {%s}]%s" % (terminal_colors.TTY_YELLOW, self.namespace[0], _translate_namespace_mode(self.namespace[1]), terminal_colors.get_standard_color()))

            elif var.variable.name == "job":

                if main_job is None: # instantiate main job with the default if needed
                    v, r = _get_job_instance(None, self.namespace)
                    if not v:
                        return False, r
                    main_job = r()

                v, r = self.__load_new_job(dsl, var, main_job)
                if not v:
                    return False, r

        return True, main_job

    def _get_launch_options_helper(self, previous, var_src, valid_values, value_filter_function):

        if previous is not None:
            return False, "Recipe's %s option has been specified more than once." % var_src.name

        local_option = None

        if len(var_src.values) != 1:
            return False, "Recipe's %s option, when specified, must be specified with one and only one value." % var_src.name

        unfiltered_val = var_src.values[0]
        filtered_val = value_filter_function(unfiltered_val)

        if valid_values is not None:
            if not filtered_val in valid_values:
                return False, "Recipe's %s option has an invalid value: [%s]" % (var_src.name, unfiltered_val)
        local_option = filtered_val

        return True, local_option

    def _get_launch_options_from_recipe(self, entrypoint_context_cache):

        local_early_abort = None
        local_time_delay = None
        local_signal_delay = None
        local_execution_delay = None

        for var in entrypoint_context_cache:

            if var.variable.name == "early-abort":

                # early abort option
                v, r = self._get_launch_options_helper(local_early_abort, var.variable, [True, False], _lowercase_bool_option_value_filter)
                if not v:
                    return False, r
                local_early_abort = r

            elif var.variable.name == "time-delay":

                # time delay option
                v, r = self._get_launch_options_helper(local_time_delay, var.variable, None, _lowercase_str_option_value_filter)
                if not v:
                    return False, r
                local_time_delay = r

            elif var.variable.name == "signal-delay":

                # signal delay option
                v, r = self._get_launch_options_helper(local_signal_delay, var.variable, None, _lowercase_str_option_value_filter)
                if not v:
                    return False, r
                local_signal_delay = r

            elif var.variable.name == "execution-delay":

                # execution delay option
                v, r = self._get_launch_options_helper(local_execution_delay, var.variable, None, _lowercase_str_option_value_filter)
                if not v:
                    return False, r
                local_execution_delay = r

        return True, launch_jobs.RunOptions(early_abort = local_early_abort, time_delay = local_time_delay, signal_delay = local_signal_delay, execution_delay = local_execution_delay)

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
            print("%sWarning: the [early-abort] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.early_abort, terminal_colors.get_standard_color()))

        local_options.time_delay = _conditional_write(local_options.time_delay, options.time_delay)
        if options.time_delay is not None and self.requested_options.time_delay is not None:
            print("%sWarning: the [time-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.time_delay, terminal_colors.get_standard_color()))

        local_options.signal_delay = _conditional_write(local_options.signal_delay, options.signal_delay)
        if options.signal_delay is not None and self.requested_options.signal_delay is not None:
            print("%sWarning: the [signal-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.signal_delay, terminal_colors.get_standard_color()))

        local_options.execution_delay = _conditional_write(local_options.execution_delay, options.execution_delay)
        if options.execution_delay is not None and self.requested_options.execution_delay is not None:
            print("%sWarning: the [execution-delay] option has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_options.execution_delay, terminal_colors.get_standard_color()))

        return True, local_options

    def _get_exec_name_from_recipe(self, entrypoint_context_cache):

        local_exec_name = None

        for var in entrypoint_context_cache:

            if var.variable.name == "execution-name":

                if local_exec_name is not None:
                    return False, "A custom execution name, when specified, can only be specified once."

                if len(var.variable.values) != 1:
                    return False, "A custom execution name, when specified, must contain one and only one value."

                local_exec_name = var.variable.values[0]

        return True, local_exec_name

    def _resolve_exec_name(self, requested_execution_name, recipe_execution_name):

        local_exec_name = None

        local_exec_name = _conditional_write(local_exec_name, requested_execution_name)
        local_exec_name = _conditional_write(local_exec_name, recipe_execution_name)

        if requested_execution_name is not None and recipe_execution_name is not None:
            print("%sWarning: the [execution-name] has been overridden by the recipe with value [%s]%s" % (terminal_colors.TTY_YELLOW, local_exec_name, terminal_colors.get_standard_color()))

        return True, local_exec_name

def test_jobs_from_recipe_file(recipe_file, entrypoint = None, execution_name = None, namespace = None, requested_options = None):
    recipe_processor = RecipeProcessor(recipe_file, namespace, requested_options)
    return recipe_processor.test(entrypoint, execution_name)

def run_jobs_from_recipe_file(recipe_file, entrypoint = None, execution_name = None, namespace = None, requested_options = None):
    recipe_processor = RecipeProcessor(recipe_file, namespace, requested_options)
    return recipe_processor.run(entrypoint, execution_name)

def assemble_requested_options(_early_abort, _time_delay, _signal_delay, _execution_delay):
    return launch_jobs.RunOptions(early_abort = _early_abort, time_delay = _time_delay, signal_delay = _signal_delay, execution_delay = _execution_delay)

def menu_test_recipe(recipe_file, entrypoint, execution_name, namespace, requested_options):

    v, r = test_jobs_from_recipe_file(recipe_file, entrypoint, execution_name, namespace, requested_options)
    if not v:
        err_msg = r
        if len(err_msg) == 1:
            err_msg = err_msg[0]
        print("%sTesting of recipe [%s] failed: [%s]%s" % (terminal_colors.TTY_RED, recipe_file, err_msg, terminal_colors.get_standard_color()))
    else:
        print("%sTesting of recipe [%s] succeeded.%s" % (terminal_colors.TTY_GREEN, recipe_file, terminal_colors.get_standard_color()))

def menu_run_recipe(recipe_file, entrypoint, execution_name, namespace, requested_options):

    v, r = run_jobs_from_recipe_file(recipe_file, entrypoint, execution_name, namespace, requested_options)
    if not v:
        print("%sExecution of recipe [%s] failed: [%s]%s" % (terminal_colors.TTY_RED, recipe_file, r, terminal_colors.get_standard_color()))
        sys.exit(ERROR_CODE_HARD_FAIL)
    if r:
        print("%sExecution of recipe [%s] succeeded - with warnings.%s" % (terminal_colors.TTY_YELLOW_BOLD, recipe_file, terminal_colors.get_standard_color()))
        sys.exit(ERROR_CODE_SOFT_FAIL)
    print("%sExecution of recipe [%s] succeeded.%s" % (terminal_colors.TTY_GREEN, recipe_file, terminal_colors.get_standard_color()))
    sys.exit(ERROR_CODE_NONE)

def puaq(selfhelp):
    print("Usage: %s [--help] [--test recipe.t20 | --run recipe.t20] --entrypoint the-recipe-entrypoint-context --execution-name the-execution-name --namespace the-namespace --namespace-mode inclusive/exclusive --early-abort yes/no --time-delay the-time-delay --signal-delay the-signal-delay --execution-delay the-execution-delay" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(ERROR_CODE_NONE)
    else:
        sys.exit(ERROR_CODE_INPUT)

if __name__ == "__main__":

    params = sys.argv[1:]
    if "--help" in params:
        puaq(True)

    if len(params) < 2:
        puaq(False)

    # recipe_processor options
    operation = None
    recipe_next = False
    recipe_file = None
    entrypoint_next = False
    entrypoint = None

    # launch_jobs options
    execution_name = None
    execution_name_next = False
    namespace = None
    namespace_next = False
    namespace_mode = True # exclusive mode (the default)
    namespace_mode_next = False
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

        if entrypoint_next:
            entrypoint_next = False
            entrypoint = p
            continue

        if execution_name_next:
            execution_name_next = False
            execution_name = p
            continue

        if namespace_next:
            namespace_next = False
            namespace = p
            continue

        if namespace_mode_next:
            namespace_mode_next = False
            if p == "inclusive":
                namespace_mode = False
            elif p == "exclusive":
                namespace_mode = True
            else:
                print("Option [--namespace-mode] received an invalid value: [%s]. Valid values are [inclusive/exclusive]" % p)
                sys.exit(ERROR_CODE_INPUT)
            continue

        if early_abort_next:
            early_abort_next = False
            if p == "yes":
                early_abort = True
            elif p == "no":
                early_abort = False
            else:
                print("Option [--early-abort] received an invalid value: [%s]. Valid values are [yes/no]" % p)
                sys.exit(ERROR_CODE_INPUT)
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
                sys.exit(ERROR_CODE_INPUT)
            operation = "test"
            recipe_next = True
        elif p == "--run":
            if operation is not None:
                print("Operation should only be specified once (either --test or --run)")
                sys.exit(ERROR_CODE_INPUT)
            operation = "run"
            recipe_next = True
        elif p == "--entrypoint":
            entrypoint_next = True
        elif p == "--execution-name":
            execution_name_next = True
        elif p == "--namespace":
            namespace_next = True
        elif p == "--namespace-mode":
            namespace_mode_next = True
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
            sys.exit(ERROR_CODE_INPUT)

    req_opts = assemble_requested_options(early_abort, time_delay, signal_delay, execution_delay)

    if namespace is not None:
        namespace = (namespace, namespace_mode)

    if operation == "test":
        menu_test_recipe(recipe_file, entrypoint, execution_name, namespace, req_opts)
    elif operation == "run":
        menu_run_recipe(recipe_file, entrypoint, execution_name, namespace, req_opts)
    else:
        print("Invalid operation: [%s]" % operation)
        sys.exit(ERROR_CODE_INPUT)

    sys.exit(ERROR_CODE_NONE)
