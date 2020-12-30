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

        sample_custom_echo_true_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_script_contents += "class CustomTask(launch_jobs.BaseTask):\n"
        sample_custom_echo_true_script_contents += "    def __init__(self, params=None):\n"
        sample_custom_echo_true_script_contents += "        self.params = params\n"
        sample_custom_echo_true_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_script_contents += "        return \"sample_custom_echo_true\"\n"
        sample_custom_echo_true_script_contents += "    def run_task(self):\n"
        sample_custom_echo_true_script_contents += "        return True, None\n"
        self.sample_custom_echo_true_script_file = path_utils.concat_path(self.test_dir, "sample_custom_echo_true.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file, sample_custom_echo_true_script_contents)

        recipe_test_contents1 = "[\n@test-job\n* task1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file1 = path_utils.concat_path(self.test_dir, "recipe_test1.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file1, recipe_test_contents1)

        recipe_test_contents2 = "[\n@test-job\n* task1 = \"nonexistent.py\"\n]"
        self.recipe_test_file2 = path_utils.concat_path(self.test_dir, "recipe_test2.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file2, recipe_test_contents2)

        recipe_test_contents3 = "[\n@test-job\n* task1 = \"sample_echo_false.py\"\n]"
        self.recipe_test_file3 = path_utils.concat_path(self.test_dir, "recipe_test3.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file3, recipe_test_contents3)

        recipe_test_contents4 = "* recipe_namespace = \"%s\"\n" % self.test_dir
        recipe_test_contents4 += "[\n@test-job\n* task1 = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_script_file)
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

if __name__ == '__main__':
    unittest.main()
