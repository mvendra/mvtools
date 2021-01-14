#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import recipe_processor

class RecipeProcessorTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

        self.namespace1 = path_utils.concat_path(self.test_dir, "namespace1")
        os.mkdir(self.namespace1)
        self.namespace2 = path_utils.concat_path(self.test_dir, "namespace2")
        os.mkdir(self.namespace2)

        sample_custom_echo_true_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_script_contents += "        return \"sample_custom_echo_true\"\n"
        sample_custom_echo_true_script_contents += "    def run_task(self):\n"
        sample_custom_echo_true_script_contents += "        return True, None\n"
        self.sample_custom_echo_true_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_echo_true.py")
        self.sample_custom_echo_true_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_echo_true.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file_namespace1, sample_custom_echo_true_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file_namespace2, sample_custom_echo_true_script_contents)

        sample_custom_echo_true_params_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_params_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_params_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_params_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_params_script_contents += "        return \"sample_custom_echo_true_params\"\n"
        sample_custom_echo_true_params_script_contents += "    def run_task(self):\n"
        sample_custom_echo_true_params_script_contents += "        if \"test\" in self.params:\n"
        sample_custom_echo_true_params_script_contents += "            return True, None\n"
        sample_custom_echo_true_params_script_contents += "        else:\n"
        sample_custom_echo_true_params_script_contents += "            return False, None\n"
        self.sample_custom_echo_true_params_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_echo_true_params.py")
        self.sample_custom_echo_true_params_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_echo_true_params.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_params_script_file_namespace1, sample_custom_echo_true_params_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_params_script_file_namespace2, sample_custom_echo_true_params_script_contents)

        sample_custom_job_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_job_script_contents += "import launch_jobs\n\n"
        sample_custom_job_script_contents += "class CustomJob(launch_jobs.BaseJob):\n"
        sample_custom_job_script_contents += "    def get_desc(self):\n"
        sample_custom_job_script_contents += "        return \"CustomJob\"\n"
        sample_custom_job_script_contents += "    def add_task(self, task):\n"
        sample_custom_job_script_contents += "        self.task_list.append(task)\n"
        sample_custom_job_script_contents += "    def run_job(self):\n"
        sample_custom_job_script_contents += "        if len(self.task_list) % 2 == 0:\n"
        sample_custom_job_script_contents += "            return True, None\n"
        sample_custom_job_script_contents += "        else:\n"
        sample_custom_job_script_contents += "            return False, None\n"
        self.sample_custom_job_script_file_namespace1 = path_utils.concat_path(self.namespace1, "sample_custom_job.py")
        self.sample_custom_job_script_file_namespace2 = path_utils.concat_path(self.namespace2, "sample_custom_job.py")
        create_and_write_file.create_file_contents(self.sample_custom_job_script_file_namespace1, sample_custom_job_script_contents)
        create_and_write_file.create_file_contents(self.sample_custom_job_script_file_namespace2, sample_custom_job_script_contents)

        recipe_test_contents1 = "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file1 = path_utils.concat_path(self.test_dir, "recipe_test1.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file1, recipe_test_contents1)

        recipe_test_contents2 = "[\n@test-job\n* task1 = \"nonexistent.py\"\n]"
        self.recipe_test_file2 = path_utils.concat_path(self.test_dir, "recipe_test2.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file2, recipe_test_contents2)

        recipe_test_contents3 = "[\n@test-job\n* task1 = \"sample_echo_false.py\"\n]"
        self.recipe_test_file3 = path_utils.concat_path(self.test_dir, "recipe_test3.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file3, recipe_test_contents3)

        recipe_test_contents4 = "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents4 += "[\n@test-job\n* task1 = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file4 = path_utils.concat_path(self.test_dir, "recipe_test4.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file4, recipe_test_contents4)

        recipe_test_contents5 = "[\n@test-job1\n* task1 = \"sample_echo_true.py\"\n]\n"
        recipe_test_contents5 += "[\n@test-job2\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file5 = path_utils.concat_path(self.test_dir, "recipe_test5.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file5, recipe_test_contents5)

        recipe_test_contents6 = "[\n@test-job1\n* task1 = \"sample_echo_true.py\"\n]\n"
        recipe_test_contents6 += "[\n@test-job2\n* task1 = \"sample_echo_false.py\"\n]"
        self.recipe_test_file6 = path_utils.concat_path(self.test_dir, "recipe_test6.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file6, recipe_test_contents6)

        recipe_test_contents7 = "* include_recipe = \"%s\"\n" % self.recipe_test_file3
        recipe_test_contents7 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file7 = path_utils.concat_path(self.test_dir, "recipe_test7.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file7, recipe_test_contents7)

        self.recipe_test_file8_1 = path_utils.concat_path(self.test_dir, "recipe_test8_1.t20")
        self.recipe_test_file8_2 = path_utils.concat_path(self.test_dir, "recipe_test8_2.t20")
        self.recipe_test_file8_3 = path_utils.concat_path(self.test_dir, "recipe_test8_3.t20")

        recipe_test_contents8_1 = "* include_recipe = \"%s\"\n" % self.recipe_test_file8_2
        recipe_test_contents8_1 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        create_and_write_file.create_file_contents(self.recipe_test_file8_1, recipe_test_contents8_1)

        recipe_test_contents8_2 = "* include_recipe = \"%s\"\n" % self.recipe_test_file8_3
        recipe_test_contents8_2 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        create_and_write_file.create_file_contents(self.recipe_test_file8_2, recipe_test_contents8_2)

        recipe_test_contents8_3 = "* include_recipe = \"%s\"\n" % self.recipe_test_file8_2
        recipe_test_contents8_3 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        create_and_write_file.create_file_contents(self.recipe_test_file8_3, recipe_test_contents8_3)

        recipe_test_contents9 = "* include_recipe = \"%s\"\n" % self.recipe_test_file1
        recipe_test_contents9 += "* include_recipe = \"%s\"\n" % self.recipe_test_file4
        recipe_test_contents9 += "* include_recipe = \"%s\"\n" % self.recipe_test_file5
        recipe_test_contents9 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file9 = path_utils.concat_path(self.test_dir, "recipe_test9.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file9, recipe_test_contents9)

        recipe_test_contents10 = "* include_recipe = \"%s\"\n" % self.recipe_test_file9
        recipe_test_contents10 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file10 = path_utils.concat_path(self.test_dir, "recipe_test10.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file10, recipe_test_contents10)

        recipe_test_contents11 = "* include_recipe = \"%s\"\n" % self.recipe_test_file7
        recipe_test_contents11 += "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file11 = path_utils.concat_path(self.test_dir, "recipe_test11.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file11, recipe_test_contents11)

        recipe_test_contents12 = "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents12 += "[\n@test-job {test}\n* task1 = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_params_script_file_namespace1)
        self.recipe_test_file12 = path_utils.concat_path(self.test_dir, "recipe_test12.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file12, recipe_test_contents12)

        recipe_test_contents13 = "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents13 += "[\n@test-job\n* task1 {test} = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_params_script_file_namespace1)
        self.recipe_test_file13 = path_utils.concat_path(self.test_dir, "recipe_test13.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file13, recipe_test_contents13)

        recipe_test_contents14 = "* early_abort = \"false\"\n"
        recipe_test_contents14 += "[\n@test-job-1\n"
        recipe_test_contents14 += "* task1 = \"sample_echo_false.py\"\n"
        recipe_test_contents14 += "]\n"
        recipe_test_contents14 += "[\n@test-job-2\n"
        recipe_test_contents14 += "* task1 = \"sample_echo_false.py\"\n"
        recipe_test_contents14 += "]"
        self.recipe_test_file14 = path_utils.concat_path(self.test_dir, "recipe_test14.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file14, recipe_test_contents14)

        recipe_test_contents15 = "* early_abort = \"true\"\n"
        recipe_test_contents15 += "* early_abort = \"false\"\n"
        recipe_test_contents15 += "[\n@test-job-1\n"
        recipe_test_contents15 += "* task1 = \"sample_echo_true.py\"\n"
        recipe_test_contents15 += "]"
        self.recipe_test_file15 = path_utils.concat_path(self.test_dir, "recipe_test15.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file15, recipe_test_contents15)

        recipe_test_contents16 = "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents16 += "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents16 += "[\n@test-job\n* task1 = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_script_file_namespace1)
        self.recipe_test_file16 = path_utils.concat_path(self.test_dir, "recipe_test16.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file16, recipe_test_contents16)

        recipe_test_contents17 = "* recipe_namespace = \"%s\"\n" % self.namespace2
        recipe_test_contents17 += "* include_recipe = \"%s\"\n" % self.recipe_test_file4
        recipe_test_contents17 += "[\n@test-job\n* task1 {test} = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_params_script_file_namespace2)
        self.recipe_test_file17 = path_utils.concat_path(self.test_dir, "recipe_test17.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file17, recipe_test_contents17)

        recipe_test_contents18 = "* recipe_namespace = \"%s\"\n" % self.namespace1
        recipe_test_contents18 += "[\n@test-job {mvtools_recipe_processor_plugin_job: \"%s\"}\n* task1 = \"%s\"\n]" % (os.path.basename(self.sample_custom_job_script_file_namespace1), os.path.basename(self.sample_custom_echo_true_script_file_namespace1))
        self.recipe_test_file18 = path_utils.concat_path(self.test_dir, "recipe_test18.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file18, recipe_test_contents18)

        recipe_test_contents19 = "* recipe_namespace = \"%s\"\n" % self.namespace2
        recipe_test_contents19 += "[\n@test-job {mvtools_recipe_processor_plugin_job: \"%s\"}\n* task1 = \"%s\"\n* task2 = \"%s\"\n]" % (os.path.basename(self.sample_custom_job_script_file_namespace1), os.path.basename(self.sample_custom_echo_true_script_file_namespace2), os.path.basename(self.sample_custom_echo_true_script_file_namespace2))
        self.recipe_test_file19 = path_utils.concat_path(self.test_dir, "recipe_test19.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file19, recipe_test_contents19)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("recipe_processor_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

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

    def testRecipeProcessorIncludesOneFalse(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file7)
        self.assertFalse(v)

    def testRecipeProcessorCircularDependency(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file8_1)
        self.assertFalse(v)

    def testRecipeProcessorDepthLimit_BreadthTest(self):
        ridl = recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER
        try:
            recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER = 2
            v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file9)
            self.assertTrue(v)
        finally:
            recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER = ridl

    def testRecipeProcessorDepthLimit_DepthTest(self):
        ridl = recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER
        try:
            recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER = 2
            v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file10)
            self.assertFalse(v)
        finally:
            recipe_processor.RECIPE_INCLUDES_DEPTH_LIMITER = ridl

    def testRecipeProcessorThirdDegreeFalse(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file11)
        self.assertFalse(v)

    def testRecipeProcessorCustomNamespaceCustomJobParams(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file12)
        self.assertTrue(v)

    def testRecipeProcessorCustomNamespaceCustomTaskParams(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file13)
        self.assertTrue(v)

    def testRecipeProcessorRecipeNoEarlyAbort(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file14)
        self.assertEqual(len(r), 2) # two job executions
        self.assertFalse(v)

    def testRecipeProcessorRecipeDoubleEarlyAbort(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file15)
        self.assertFalse(v)

    def testRecipeProcessorDoubleCustomNamespace(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file16)
        self.assertFalse(v)

    def testRecipeProcessorCustomNamespaceIncludesAnotherCustomNamespace(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file17)
        self.assertTrue(v)

    def testRecipeProcessorCustomJobCustomNamespace1(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file18)
        self.assertFalse(v)

    def testRecipeProcessorCustomJobCustomNamespace2(self):
        v, r = recipe_processor.run_jobs_from_recipe_file(self.recipe_test_file19)
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
