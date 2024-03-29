#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import toolbus
import mvtools_envvars

import recipe_processor

def FileHasContents(filename, contents):
    if not os.path.exists(filename):
        return False
    local_contents = ""
    with open(filename, "r") as f:
        local_contents = f.read()
    if local_contents == contents:
        return True
    return False

class RecipeProcessorTest(unittest.TestCase):

    def setUp(self):
        self.mvtools_envvars_inst = mvtools_envvars.Mvtools_Envvars()
        v, r = self.mvtools_envvars_inst.make_copy_environ()
        if not v:
            self.tearDown()
            self.fail(r)
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("recipe_processor_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        v, r = mvtools_envvars.mvtools_envvar_write_toolbus_base(self.test_dir)
        if not v:
            return False, "Failed setting up toolbus envvar for testing."

        self.namespace1 = path_utils.concat_path(self.test_dir, "namespace1")
        os.mkdir(self.namespace1)
        self.namespace2 = path_utils.concat_path(self.test_dir, "namespace2")
        os.mkdir(self.namespace2)

        sample_custom_echo_true_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_script_contents += "        return \"sample_custom_echo_true\"\n"
        sample_custom_echo_true_script_contents += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_custom_echo_true_script_contents += "        return True, None\n"
        self.sample_custom_echo_true_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_echo_true_plugin.py")
        self.sample_custom_echo_true_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_echo_true_plugin.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file_namespace1, sample_custom_echo_true_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file_namespace2, sample_custom_echo_true_script_contents)

        sample_custom_echo_true_params_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_params_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_params_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_params_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_params_script_contents += "        return \"sample_custom_echo_true_params\"\n"
        sample_custom_echo_true_params_script_contents += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_custom_echo_true_params_script_contents += "        if \"test\" in self.params:\n"
        sample_custom_echo_true_params_script_contents += "            return True, None\n"
        sample_custom_echo_true_params_script_contents += "        else:\n"
        sample_custom_echo_true_params_script_contents += "            return False, None\n"
        self.sample_custom_echo_true_params_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_echo_true_params.py")
        self.sample_custom_echo_true_params_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_echo_true_params.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_params_script_file_namespace1, sample_custom_echo_true_params_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_params_script_file_namespace2, sample_custom_echo_true_params_script_contents)

        sample_custom_exe_name_contents1 = "#!/usr/bin/env python3\n\n"
        sample_custom_exe_name_contents1 += "import launch_jobs\n"
        sample_custom_exe_name_contents1 += "import toolbus\n\n"
        sample_custom_exe_name_contents1 += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_exe_name_contents1 += "    def get_desc(self):\n"
        sample_custom_exe_name_contents1 += "        return \"sample_custom_exe_name_1\"\n"
        sample_custom_exe_name_contents1 += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_custom_exe_name_contents1 += "        v, r = toolbus.bootstrap_custom_toolbus_db(execution_name)\n"
        sample_custom_exe_name_contents1 += "        if not v:\n"
        sample_custom_exe_name_contents1 += "            return False, \"Failure in test infrastructure: [%s]\" % r\n"
        sample_custom_exe_name_contents1 += "        v, r = toolbus.set_field(execution_name, \"test-ctx-custom\", \"test-var-name\", \"test-var-val\", [])\n"
        sample_custom_exe_name_contents1 += "        if not v:\n"
        sample_custom_exe_name_contents1 += "            return False, \"Failure in test infrastructure: [%s]\" % r\n"
        sample_custom_exe_name_contents1 += "        return True, None\n"
        self.sample_custom_exe_name_contents_file1 = path_utils.concat_path(self.test_dir, "sample_custom_exe_name1.py")
        create_and_write_file.create_file_contents(self.sample_custom_exe_name_contents_file1, sample_custom_exe_name_contents1)

        sample_custom_exe_name_contents2 = "#!/usr/bin/env python3\n\n"
        sample_custom_exe_name_contents2 += "import launch_jobs\n"
        sample_custom_exe_name_contents2 += "import toolbus\n\n"
        sample_custom_exe_name_contents2 += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_exe_name_contents2 += "    def get_desc(self):\n"
        sample_custom_exe_name_contents2 += "        return \"sample_custom_exe_name_2\"\n"
        sample_custom_exe_name_contents2 += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_custom_exe_name_contents2 += "        v, r = toolbus.get_field(execution_name, \"test-ctx-custom\", \"test-var-name\")\n"
        sample_custom_exe_name_contents2 += "        if not v:\n"
        sample_custom_exe_name_contents2 += "            return False, \"Failure in test infrastructure: [%s]\" % r\n"
        sample_custom_exe_name_contents2 += "        if r[1] == \"test-var-val\":\n"
        sample_custom_exe_name_contents2 += "            return True, None\n"
        sample_custom_exe_name_contents2 += "        return False, r\n"
        self.sample_custom_exe_name_contents_file2 = path_utils.concat_path(self.test_dir, "sample_custom_exe_name2.py")
        create_and_write_file.create_file_contents(self.sample_custom_exe_name_contents_file2, sample_custom_exe_name_contents2)

        sample_custom_echo_true_repeated_params_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_repeated_params_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_repeated_params_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_repeated_params_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_repeated_params_script_contents += "        return \"sample_custom_echo_true_repeated_params\"\n"
        sample_custom_echo_true_repeated_params_script_contents += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_custom_echo_true_repeated_params_script_contents += "        if not \"test\" in self.params:\n"
        sample_custom_echo_true_repeated_params_script_contents += "            return False, None\n"
        sample_custom_echo_true_repeated_params_script_contents += "        if not isinstance(self.params[\"test\"], list):\n"
        sample_custom_echo_true_repeated_params_script_contents += "            return False, None\n"
        sample_custom_echo_true_repeated_params_script_contents += "        return True, None\n"
        self.sample_custom_echo_true_repeated_params_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_echo_true_repeated_params.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_repeated_params_script_file_namespace1, sample_custom_echo_true_repeated_params_script_contents)

        sample_echo_true_plugin_dupe_contents = "#!/usr/bin/env python3\n\n"
        sample_echo_true_plugin_dupe_contents += "import launch_jobs\n\n"
        sample_echo_true_plugin_dupe_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_echo_true_plugin_dupe_contents += "    def get_desc(self):\n"
        sample_echo_true_plugin_dupe_contents += "        return \"sample_echo_true_plugin_dupe\"\n"
        sample_echo_true_plugin_dupe_contents += "    def run_task(self, feedback_object, execution_name=None):\n"
        sample_echo_true_plugin_dupe_contents += "        if \"dupe-check\" in self.params:\n"
        sample_echo_true_plugin_dupe_contents += "            return True, None\n"
        sample_echo_true_plugin_dupe_contents += "        return False, \"dupe-check was not specified\"\n"
        self.sample_echo_true_plugin_dupe_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_echo_true_plugin.py")
        create_and_write_file.create_file_contents(self.sample_echo_true_plugin_dupe_file_namespace2, sample_echo_true_plugin_dupe_contents)

        sample_custom_job_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_job_script_contents += "import launch_jobs\n\n"
        sample_custom_job_script_contents += "class CustomJob(launch_jobs.BaseJob):\n"
        sample_custom_job_script_contents += "    def get_desc(self):\n"
        sample_custom_job_script_contents += "        return \"CustomJob\"\n"
        sample_custom_job_script_contents += "    def add_entry(self, task):\n"
        sample_custom_job_script_contents += "        self.entries_list.append(task)\n"
        sample_custom_job_script_contents += "    def run_job(self, feedback_object, execution_name=None, options=None):\n"
        sample_custom_job_script_contents += "        if len(self.entries_list) % 2 == 0:\n"
        sample_custom_job_script_contents += "            return True, None\n"
        sample_custom_job_script_contents += "        else:\n"
        sample_custom_job_script_contents += "            return False, None\n"
        self.sample_custom_job_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_job.py")
        self.sample_custom_job_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_job.py")
        create_and_write_file.create_file_contents(self.sample_custom_job_script_file_namespace1, sample_custom_job_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_job_script_file_namespace2, sample_custom_job_script_contents)

        self.recipe_test_contents1 = "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file1 = path_utils.concat_path(self.test_dir, "recipe_test1.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file1, self.recipe_test_contents1)

        recipe_test_contents2 = "[\n@test-job\n* task1 = \"nonexistent.py\"\n]"
        self.recipe_test_file2 = path_utils.concat_path(self.test_dir, "recipe_test2.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file2, recipe_test_contents2)

        recipe_test_contents3 = "[\n@test-job\n* task1 = \"sample_echo_false_plugin.py\"\n]"
        self.recipe_test_file3 = path_utils.concat_path(self.test_dir, "recipe_test3.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file3, recipe_test_contents3)

        recipe_test_contents4 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents4 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents4 += "]\n"
        recipe_test_contents4 += "[\n@test-job\n* task1 = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file4 = path_utils.concat_path(self.test_dir, "recipe_test4.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file4, recipe_test_contents4)

        recipe_test_contents5 = "[\n@test-job1\n* task1 = \"sample_echo_true_plugin.py\"\n]\n"
        recipe_test_contents5 += "[\n@test-job2\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file5 = path_utils.concat_path(self.test_dir, "recipe_test5.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file5, recipe_test_contents5)

        recipe_test_contents6 = "[\n@test-job1\n* task1 = \"sample_echo_true_plugin.py\"\n]\n"
        recipe_test_contents6 += "[\n@test-job2\n* task1 = \"sample_echo_false_plugin.py\"\n]"
        self.recipe_test_file6 = path_utils.concat_path(self.test_dir, "recipe_test6.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file6, recipe_test_contents6)

        recipe_test_contents7 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents7 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents7 += "]\n"
        recipe_test_contents7 += "[\n@test-job {test}\n* task1 = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_params_script_file_namespace1)
        self.recipe_test_file7 = path_utils.concat_path(self.test_dir, "recipe_test7.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file7, recipe_test_contents7)

        recipe_test_contents8 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents8 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents8 += "]\n"
        recipe_test_contents8 += "[\n@test-job\n* task1 {test} = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_params_script_file_namespace1)
        self.recipe_test_file8 = path_utils.concat_path(self.test_dir, "recipe_test8.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file8, recipe_test_contents8)

        self.recipe_test_9_callstack = path_utils.concat_path(self.test_dir, "recipe_test_9_callstack.txt")
        recipe_test_contents9 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents9 += "* early-abort = \"no\"\n"
        recipe_test_contents9 += "]\n"
        recipe_test_contents9 += "[\n@test-job-1\n"
        recipe_test_contents9 += "* task1 {target_file: \"%s\" / mode: \"a\" / content: \"task1\"} = \"writefile_plugin.py\"\n" % self.recipe_test_9_callstack
        recipe_test_contents9 += "* task-fail = \"sample_echo_false_plugin.py\"\n"
        recipe_test_contents9 += "]\n"
        recipe_test_contents9 += "[\n@test-job-2\n"
        recipe_test_contents9 += "* task2 {target_file: \"%s\" / mode: \"a\" / content: \"task2\"} = \"writefile_plugin.py\"\n" % self.recipe_test_9_callstack
        recipe_test_contents9 += "]"
        self.recipe_test_file9 = path_utils.concat_path(self.test_dir, "recipe_test9.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file9, recipe_test_contents9)

        recipe_test_contents10 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents10 += "* early-abort = \"yes\"\n"
        recipe_test_contents10 += "* early-abort = \"no\"\n"
        recipe_test_contents10 += "]\n"
        recipe_test_contents10 += "[\n@test-job-1\n"
        recipe_test_contents10 += "* task1 = \"sample_echo_true_plugin.py\"\n"
        recipe_test_contents10 += "]"
        self.recipe_test_file10 = path_utils.concat_path(self.test_dir, "recipe_test10.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file10, recipe_test_contents10)

        recipe_test_contents11 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents11 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents11 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents11 += "]\n"
        recipe_test_contents11 += "[\n@test-job\n* task1 = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file11 = path_utils.concat_path(self.test_dir, "recipe_test11.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file11, recipe_test_contents11)

        recipe_test_contents12 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents12 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents12 += "* custom-job-implementation {test-job} = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_job_script_file_namespace1)
        recipe_test_contents12 += "]\n"
        recipe_test_contents12 += "[\n@test-job\n* task1 = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file12 = path_utils.concat_path(self.test_dir, "recipe_test12.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file12, recipe_test_contents12)

        recipe_test_contents13 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents13 += "* recipe-namespace = \"%s\"\n" % self.namespace2
        recipe_test_contents13 += "* custom-job-implementation {test-job} = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_job_script_file_namespace1)
        recipe_test_contents13 += "]\n"
        recipe_test_contents13 += "[\n@test-job\n* task1 = \"%s\"\n* task2 = \"%s\"\n]" % (path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace2), path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace2))
        self.recipe_test_file13 = path_utils.concat_path(self.test_dir, "recipe_test13.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file13, recipe_test_contents13)

        recipe_test_contents14 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents14 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents14 += "* custom-main-job-implementation = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_job_script_file_namespace1)
        recipe_test_contents14 += "]\n"
        recipe_test_contents14 += "[\n@test-job1\n* task1 = \"%s\"\n]\n" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        recipe_test_contents14 += "[\n@test-job2\n* task1 = \"%s\"\n]\n" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file14 = path_utils.concat_path(self.test_dir, "recipe_test14.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file14, recipe_test_contents14)

        recipe_test_contents15 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents15 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents15 += "* custom-main-job-implementation = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_job_script_file_namespace1)
        recipe_test_contents15 += "]\n"
        recipe_test_contents15 += "[\n@test-job1\n* task1 = \"%s\"\n]\n" % path_utils.basename_filtered(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file15 = path_utils.concat_path(self.test_dir, "recipe_test15.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file15, recipe_test_contents15)

        recipe_test_contents16 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents16 += "* execution-name = \"test-exec-name\"\n"
        recipe_test_contents16 += "]\n"
        recipe_test_contents16 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file16 = path_utils.concat_path(self.test_dir, "recipe_test16.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file16, recipe_test_contents16)

        recipe_test_contents17 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents17 += "* execution-name = \"test-exec-name1\"\n"
        recipe_test_contents17 += "* execution-name = \"test-exec-name2\"\n"
        recipe_test_contents17 += "]\n"
        recipe_test_contents17 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file17 = path_utils.concat_path(self.test_dir, "recipe_test17.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file17, recipe_test_contents17)

        recipe_test_contents18 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents18 += "* time-delay = \"2s\"\n"
        recipe_test_contents18 += "]\n"
        recipe_test_contents18 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file18 = path_utils.concat_path(self.test_dir, "recipe_test18.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file18, recipe_test_contents18)

        recipe_test_contents19 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents19 += "* time-delay = \"2s\"\n"
        recipe_test_contents19 += "* time-delay = \"3s\"\n"
        recipe_test_contents19 += "]\n"
        recipe_test_contents19 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file19 = path_utils.concat_path(self.test_dir, "recipe_test19.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file19, recipe_test_contents19)

        recipe_test_contents20 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents20 += "* signal-delay = \"test-signal\"\n"
        recipe_test_contents20 += "]\n"
        recipe_test_contents20 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file20 = path_utils.concat_path(self.test_dir, "recipe_test20.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file20, recipe_test_contents20)

        recipe_test_contents21 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents21 += "* signal-delay = \"test-signal1\"\n"
        recipe_test_contents21 += "* signal-delay = \"test-signal2\"\n"
        recipe_test_contents21 += "]\n"
        recipe_test_contents21 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file21 = path_utils.concat_path(self.test_dir, "recipe_test21.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file21, recipe_test_contents21)

        recipe_test_contents22 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents22 += "* execution-delay = \"test-exec-name\"\n"
        recipe_test_contents22 += "]\n"
        recipe_test_contents22 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file22 = path_utils.concat_path(self.test_dir, "recipe_test22.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file22, recipe_test_contents22)

        recipe_test_contents23 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents23 += "* execution-delay = \"test-exec1\"\n"
        recipe_test_contents23 += "* execution-delay = \"test-exec2\"\n"
        recipe_test_contents23 += "]\n"
        recipe_test_contents23 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file23 = path_utils.concat_path(self.test_dir, "recipe_test23.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file23, recipe_test_contents23)

        recipe_test_contents24 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents24 += "* recipe-namespace = \"%s\"\n" % self.test_dir
        recipe_test_contents24 += "]\n"
        recipe_test_contents24 += "[\n@test-job-1\n"
        recipe_test_contents24 += "* task1 = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_exe_name_contents_file1)
        recipe_test_contents24 += "]\n"
        recipe_test_contents24 += "[\n@test-job-2\n"
        recipe_test_contents24 += "* task2 = \"%s\"\n" % path_utils.basename_filtered(self.sample_custom_exe_name_contents_file2)
        recipe_test_contents24 += "]"
        self.recipe_test_file24 = path_utils.concat_path(self.test_dir, "recipe_test24.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file24, recipe_test_contents24)

        recipe_test_contents25 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents25 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents25 += "]\n"
        recipe_test_contents25 += "[\n@test-job\n* task1 {test: (\"val1\", \"val2\")} = \"%s\"\n]" % path_utils.basename_filtered(self.sample_custom_echo_true_repeated_params_script_file_namespace1)
        self.recipe_test_file25 = path_utils.concat_path(self.test_dir, "recipe_test25.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file25, recipe_test_contents25)

        recipe_test_contents26 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents26 += "* recipe-namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents26 += "]\n"
        recipe_test_contents26 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file26 = path_utils.concat_path(self.test_dir, "recipe_test26.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file26, recipe_test_contents26)

        recipe_test_contents27 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents27 += "* recipe-namespace {inclusive} = \"%s\"\n" % self.namespace2
        recipe_test_contents27 += "]\n"
        recipe_test_contents27 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file27 = path_utils.concat_path(self.test_dir, "recipe_test27.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file27, recipe_test_contents27)

        recipe_test_contents28 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents28 += "* recipe-namespace = \"%s\"\n" % self.namespace2
        recipe_test_contents28 += "]\n"
        recipe_test_contents28 += "[\n@test-job\n* task1 = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file28 = path_utils.concat_path(self.test_dir, "recipe_test28.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file28, recipe_test_contents28)

        recipe_test_contents29 = "[\n@%s\n" % recipe_processor.RECIPE_PROCESSOR_CONFIG_METAJOB
        recipe_test_contents29 += "* recipe-namespace = \"%s\"\n" % self.namespace2
        recipe_test_contents29 += "]\n"
        recipe_test_contents29 += "[\n@test-job\n* task1 {dupe-check} = \"sample_echo_true_plugin.py\"\n]"
        self.recipe_test_file29 = path_utils.concat_path(self.test_dir, "recipe_test29.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file29, recipe_test_contents29)

        self.recipe_test_30_callstack = path_utils.concat_path(self.test_dir, "recipe_test_30_callstack.txt")
        recipe_test_contents30 = "* task1 {target_file: \"%s\" / mode: \"a\" / content: \"task1\"} = \"writefile_plugin.py\"\n" % self.recipe_test_30_callstack
        recipe_test_contents30 += "[\n"
        recipe_test_contents30 += "@job1\n"
        recipe_test_contents30 += "* task2 {target_file: \"%s\" / mode: \"a\" / content: \"task2\"} = \"writefile_plugin.py\"\n" % self.recipe_test_30_callstack
        recipe_test_contents30 += "[\n"
        recipe_test_contents30 += "@job2\n"
        recipe_test_contents30 += "* task3 {target_file: \"%s\" / mode: \"a\" / content: \"task3\"} = \"writefile_plugin.py\"\n" % self.recipe_test_30_callstack
        recipe_test_contents30 += "]\n"
        recipe_test_contents30 += "* task4 {target_file: \"%s\" / mode: \"a\" / content: \"task4\"} = \"writefile_plugin.py\"\n" % self.recipe_test_30_callstack
        recipe_test_contents30 += "]\n"
        recipe_test_contents30 += "* task5 {target_file: \"%s\" / mode: \"a\" / content: \"task5\"} = \"writefile_plugin.py\"\n" % self.recipe_test_30_callstack
        self.recipe_test_file30 = path_utils.concat_path(self.test_dir, "recipe_test30.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file30, recipe_test_contents30)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def testRecipeProcessorVanilla(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file1)
        self.assertTrue(v)

    def testRecipeProcessorNonexistentScript(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file2)
        self.assertFalse(v)

    def testRecipeProcessorOneTaskReturnsFalse(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file3)
        self.assertFalse(v)

    def testRecipeProcessorCustomNamespace(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file4)
        self.assertTrue(v)

    def testRecipeProcessor2JobsBothSucceed(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file5)
        self.assertTrue(v)

    def testRecipeProcessor2JobsOneFails(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file6)
        self.assertFalse(v)

    def testRecipeProcessorCustomNamespaceCustomJobParams(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file7)
        self.assertTrue(v)

    def testRecipeProcessorCustomNamespaceCustomTaskParams(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file8)
        self.assertTrue(v)

    def testRecipeProcessorRecipeNoEarlyAbort(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file9)
        self.assertFalse(v)
        self.assertTrue(FileHasContents(self.recipe_test_9_callstack, "task1task2"))

    def testRecipeProcessorRecipeDoubleEarlyAbort(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file10)
        self.assertFalse(v)

    def testRecipeProcessorDoubleCustomNamespace(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file11)
        self.assertFalse(v)

    def testRecipeProcessorCustomJobCustomNamespace1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file12)
        self.assertFalse(v)

    def testRecipeProcessorCustomJobCustomNamespace2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file13)
        self.assertTrue(v)

    def testRecipeProcessorCustomMainJobCustomNamespace1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file14)
        self.assertTrue(v)

    def testRecipeProcessorCustomMainJobCustomNamespace1Fails(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file15)
        self.assertFalse(v)

    def testRecipeProcessorCustomExecutionName1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file16)
        self.assertTrue(v)

    def testRecipeProcessorCustomExecutionName2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file17)
        self.assertFalse(v)

    def testRecipeProcessorTimeDelay1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file18)
        self.assertTrue(v)

    def testRecipeProcessorTimeDelay2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file19)
        self.assertFalse(v)

    def testRecipeProcessorSignalDelay1(self):
        v, r = toolbus.set_signal("test-signal", "set")
        self.assertTrue(v)
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file20)
        self.assertTrue(v)

    def testRecipeProcessorSignalDelay2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file21)
        self.assertFalse(v)

    def testRecipeProcessorExecutionDelay1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file16)
        self.assertTrue(v)
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file22)
        self.assertTrue(v)

    def testRecipeProcessorExecutionDelay2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file23)
        self.assertFalse(v)

    def testRecipeProcessorCustomTaskUseExecutionName(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file24)
        self.assertTrue(v)

    def testRecipeProcessorStringlistParam(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file25)
        self.assertTrue(v)

    def testRecipeProcessorNamespaceExclusiveNotFound(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file26)
        self.assertFalse(v)

    def testRecipeProcessorNamespaceInclusiveIsFoundAtBuiltInsFirst(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file27)
        self.assertTrue(v)

    def testRecipeProcessorNamespaceExclusiveIsFoundButFails(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file28)
        self.assertFalse(v)

    def testRecipeProcessorNamespaceExclusiveIsFoundAndDoesWork(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file29)
        self.assertTrue(v)

    def testRecipeProcessorNestedJobsDepthFail(self):
        stashed_depth_limit = recipe_processor.DEPTH_TRACKER_LIMIT
        recipe_processor.DEPTH_TRACKER_LIMIT = 1
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file30)
        self.assertFalse(v)
        recipe_processor.DEPTH_TRACKER_LIMIT = stashed_depth_limit

    def testRecipeProcessorNestedJobs(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file30)
        self.assertTrue(v)
        self.assertTrue(FileHasContents(self.recipe_test_30_callstack, "task1task2task3task4task5"))

    def testRecipeProcessorBlankFilename(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blanksub_blankfile = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blanksub_blankfile))
        self.assertTrue(create_and_write_file.create_file_contents(blanksub_blankfile, self.recipe_test_contents1))
        self.assertTrue(os.path.exists(blanksub_blankfile))

        v, r = recipe_processor.run_jobs_from_recipe_file(blanksub_blankfile)
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
