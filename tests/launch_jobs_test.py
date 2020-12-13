#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import launch_jobs

class CustomStepTrue(launch_jobs.BaseStep):
    def desc(self):
        return "CustomStepTrue"
    def run_step(self):
        return True, None

class CustomStepFalse(launch_jobs.BaseStep):
    def desc(self):
        return "CustomStepFalse"
    def run_step(self):
        return False, None

class CustomStepParams(launch_jobs.BaseStep):
    def desc(self):
        return "CustomStepParams"
    def run_step(self):
        if self.params["test"]:
            return True, None
        else:
            return False, None

class CustomStepParams1And2(launch_jobs.BaseStep):
    def desc(self):
        return "CustomStepParams"
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

        job1 = launch_jobs.BaseJob({"test": True})
        job1.add_step(CustomStepParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomStepParams2(self):

        job1 = launch_jobs.BaseJob({"test": False})
        job1.add_step(CustomStepParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomStepParams3(self):

        job1 = launch_jobs.BaseJob({"cause-except": True})
        job1.add_step(CustomStepParams())

        try:
            v, r = launch_jobs.run_job_list([job1])
        except KeyError:
            pass
        except:
            self.fail("Unexpected exception")

    def testLaunchJobsCustomStepParams4(self):

        job1 = launch_jobs.BaseJob({"test1": True})
        job1.add_step(CustomStepParams1And2({"test2": True}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomStepParams5(self):

        job1 = launch_jobs.BaseJob({"test": True})
        job1.add_step(CustomStepParams({"test": False}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

if __name__ == '__main__':
    unittest.main()
