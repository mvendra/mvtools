#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture

import toolbus
import launch_jobs

class CustomTaskTrue(launch_jobs.BaseTask):
    def run_task(self):
        return True, None

class CustomTaskFalse(launch_jobs.BaseTask):
    def run_task(self):
        return False, None

class CustomTaskParams(launch_jobs.BaseTask):
    def run_task(self):
        if self.params["test"]:
            return True, None
        else:
            return False, None

class CustomTaskParams1And2(launch_jobs.BaseTask):
    def run_task(self):
        if self.params["test1"] and self.params["test2"]:
            return True, None
        else:
            return False, None

class CustomJob(launch_jobs.BaseJob):
    def add_task(self, task):
        task.params = launch_jobs._merge_params_downwards(self.params, task.params)
        self.task_list.append(task)
        return True, None
    def run_job(self, execution_name=None):
        res = True
        for t in self.task_list:
            res &= (t.run_task())[0]
        return res, None

class LaunchJobsTest(unittest.TestCase):

    def setUp(self):
        self.environ_copy = os.environ.copy()
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

        if not mvtools_test_fixture.setEnv(toolbus.TOOLBUS_ENVVAR, self.test_dir):
            return False, "Failed setting up the %s env var for testing." % toolbus.TOOLBUS_ENVVAR

        return True, ""

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_copy)
        shutil.rmtree(self.test_base_dir)

    def testLaunchJobsVanilla(self):

        job1 = CustomJob()
        job1.add_task(launch_jobs.BaseTask())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomTask1(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomTask2(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())
        job1.add_task(CustomTaskFalse())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomTaskParams1(self):

        job1 = CustomJob(params={"test": True})
        job1.add_task(CustomTaskParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomTaskParams2(self):

        job1 = CustomJob(params={"test": False})
        job1.add_task(CustomTaskParams())

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsCustomTaskParams3(self):

        job1 = CustomJob(params={"cause-except": True})
        job1.add_task(CustomTaskParams())

        try:
            v, r = launch_jobs.run_job_list([job1])
        except KeyError:
            pass
        except:
            self.fail("Unexpected exception")

    def testLaunchJobsCustomTaskParams4(self):

        job1 = CustomJob(params={"test1": True})
        job1.add_task(CustomTaskParams1And2(params={"test2": True}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertTrue(v)

    def testLaunchJobsCustomTaskParams5(self):

        job1 = CustomJob(params={"test": True})
        job1.add_task(CustomTaskParams(params={"test": False}))

        v, r = launch_jobs.run_job_list([job1])
        self.assertFalse(v)

    def testLaunchJobsRunOptions1(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskFalse())

        job2 = CustomJob()
        job2.add_task(CustomTaskFalse())

        job_list = [job1, job2]

        v, r = launch_jobs.run_job_list(job_list)
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testLaunchJobsRunOptionsEarlyAbort1(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskFalse())

        job2 = CustomJob()
        job2.add_task(CustomTaskFalse())

        job_list = [job1, job2]

        v, r = launch_jobs.run_job_list(job_list, options=launch_jobs.RunOptions(early_abort=False))
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testLaunchJobsRunOptionsEarlyAbort2(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())

        job2 = CustomJob()
        job2.add_task(CustomTaskTrue())

        job_list = [job1, job2]

        v, r = launch_jobs.run_job_list(job_list, options=launch_jobs.RunOptions(early_abort=False))
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testLaunchJobsRunOptionsTimeDelay1(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())

        job_list = [job1]

        v, r = launch_jobs.run_job_list(job_list, options=launch_jobs.RunOptions(time_delay="2s"))
        self.assertTrue(v)

    def testLaunchJobsRunOptionsSignalDelay1(self):

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())

        job_list = [job1]

        v, r = toolbus.set_signal("mvtools-launch-jobs-test-signal-delay-option", "set")
        self.assertTrue(v)

        v, r = launch_jobs.run_job_list(job_list, options=launch_jobs.RunOptions(signal_delay="mvtools-launch-jobs-test-signal-delay-option"))
        self.assertTrue(v)

    def testLaunchJobsRunOptionsExecutionDelay1(self):

        first_exec = "first-exec"

        job1 = CustomJob()
        job1.add_task(CustomTaskTrue())

        job_list = [job1]

        v, r = launch_jobs.run_job_list(job_list, first_exec)
        self.assertTrue(v)

        v, r = launch_jobs.run_job_list(job_list, options=launch_jobs.RunOptions(execution_delay=first_exec))
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
