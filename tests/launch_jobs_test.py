#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import launch_jobs

class CustomStepTrue(launch_jobs.BaseStep):
    def run_step(self):
        return True, None

class CustomStepFalse(launch_jobs.BaseStep):
    def run_step(self):
        return False, None

class CustomStepParams(launch_jobs.BaseStep):
    def run_step(self):
        if self.params["test"]:
            return True, None
        else:
            return False, None

class CustomStepParams1And2(launch_jobs.BaseStep):
    def run_step(self):
        if self.params["test1"] and self.params["test2"]:
            return True, None
        else:
            return False, None

class LaunchJobsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

        sample_custom_echo_true_script_contents = "#!/usr/bin/env python3\n\n"
        sample_custom_echo_true_script_contents += "import launch_jobs\n\n"
        sample_custom_echo_true_script_contents += "class CustomStep(launch_jobs.BaseStep):\n"
        sample_custom_echo_true_script_contents += "    def __init__(self, params=None):\n"
        sample_custom_echo_true_script_contents += "        self.params = params\n"
        sample_custom_echo_true_script_contents += "    def get_desc(self):\n"
        sample_custom_echo_true_script_contents += "        return \"sample_custom_echo_true\"\n"
        sample_custom_echo_true_script_contents += "    def run_step(self):\n"
        sample_custom_echo_true_script_contents += "        return True, None\n"
        self.sample_custom_echo_true_script_file = path_utils.concat_path(self.test_dir, "sample_custom_echo_true.py")
        create_and_write_file.create_file_contents(self.sample_custom_echo_true_script_file, sample_custom_echo_true_script_contents)

        recipe_test_contents1 = "[\n@test-job\n* step1 = \"sample_echo_true.py\"\n]"
        self.recipe_test_file1 = path_utils.concat_path(self.test_dir, "recipe_test1.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file1, recipe_test_contents1)

        recipe_test_contents2 = "[\n@test-job\n* step1 = \"nonexistent.py\"\n]"
        self.recipe_test_file2 = path_utils.concat_path(self.test_dir, "recipe_test2.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file2, recipe_test_contents2)

        recipe_test_contents3 = "[\n@test-job\n* step1 = \"sample_echo_false.py\"\n]"
        self.recipe_test_file3 = path_utils.concat_path(self.test_dir, "recipe_test3.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file3, recipe_test_contents3)

        recipe_test_contents4 = "* recipe_namespace = \"%s\"\n" % self.test_dir
        recipe_test_contents4 += "[\n@test-job\n* step1 = \"%s\"\n]" % os.path.basename(self.sample_custom_echo_true_script_file)
        self.recipe_test_file4 = path_utils.concat_path(self.test_dir, "recipe_test4.t20")
        create_and_write_file.create_file_contents(self.recipe_test_file4, recipe_test_contents4)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("launch_jobs_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLaunchJobsVanilla(self):

        job1 = launch_jobs.BaseJob()
        job1.add_step(launch_jobs.BaseStep())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomStep1(self):

        job1 = launch_jobs.BaseJob()
        job1.add_step(CustomStepTrue())

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomStep2(self):

        job1 = launch_jobs.BaseJob()
        job1.add_step(CustomStepTrue())
        job1.add_step(CustomStepFalse())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomStepParams1(self):

        job1 = launch_jobs.BaseJob(params={"test": True})
        job1.add_step(CustomStepParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomStepParams2(self):

        job1 = launch_jobs.BaseJob(params={"test": False})
        job1.add_step(CustomStepParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomStepParams3(self):

        job1 = launch_jobs.BaseJob(params={"cause-except": True})
        job1.add_step(CustomStepParams())

        try:
            v, r = launch_jobs.run_job_list([job1])
        except KeyError:
            pass
        except:
            self.fail("Unexpected exception")

    def testLaunchJobsCustomStepParams4(self):

        job1 = launch_jobs.BaseJob(params={"test1": True})
        job1.add_step(CustomStepParams1And2(params={"test2": True}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomStepParams5(self):

        job1 = launch_jobs.BaseJob(params={"test": True})
        job1.add_step(CustomStepParams(params={"test": False}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsRecipeVanilla(self):

        v, r = launch_jobs.run_jobs_from_recipe_file(self.recipe_test_file1)
        self.assertTrue(v)

    def testLaunchJobsRecipeNonexistentScript(self):

        v, r = launch_jobs.run_jobs_from_recipe_file(self.recipe_test_file2)
        self.assertFalse(v)

    def testLaunchJobsRecipeOneStepReturnsFalse(self):

        v, r = launch_jobs.run_jobs_from_recipe_file(self.recipe_test_file3)
        self.assertFalse(v)

    def testLaunchJobsRecipeCustomNamespace(self):

        v, r = launch_jobs.run_jobs_from_recipe_file(self.recipe_test_file4)
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
