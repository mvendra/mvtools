#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import mvtools_exception
import mvtools_envvars

import toolbus
import standard_job
import launch_jobs

class aux_test_context():
    def __init__(self):
        self.call_stack = []

class CustomJob(launch_jobs.BaseJob):
    def add_entry(self, task):
        add_list = []
        for k in self.params:
            if k not in task.params:
                add_list.append(k)
        for k in add_list:
            task.params[k] = self.params[k]
        self.entries_list.append(task)
        return True, None
    def run_job(self, feedback_object, execution_name=None, options=None):
        res = True
        for t in self.entries_list:
            if t.get_type() == launch_jobs.BASE_TYPE_TASK: # UT's CustomJob impl does not support nested jobs (yet)
                res &= (t.run_task(feedback_object, execution_name))[0]
        return res, None

class CustomTaskTrue(launch_jobs.BaseTask):
    def run_task(self, feedback_object, execution_name=None):
        if "internal_testing_context" in self.params:
            test_ctx = self.params["internal_testing_context"]
            test_ctx.call_stack.append("CustomTaskTrue.run_task,%s" % self.name)
        return True, None

class CustomTaskFalse(launch_jobs.BaseTask):
    def run_task(self, feedback_object, execution_name=None):
        if "internal_testing_context" in self.params:
            test_ctx = self.params["internal_testing_context"]
            test_ctx.call_stack.append("CustomTaskFalse.run_task,%s" % self.name)
        return False, None

class CustomTaskParams(launch_jobs.BaseTask):
    def run_task(self, feedback_object, execution_name=None):
        if self.params["test"]:
            return True, None
        else:
            return False, None

class CustomTaskParams1And2(launch_jobs.BaseTask):
    def run_task(self, feedback_object, execution_name=None):
        if self.params["test1"] and self.params["test2"]:
            return True, None
        else:
            return False, None

class CustomTaskException(launch_jobs.BaseTask):
    def run_task(self, feedback_object, execution_name=None):
        raise mvtools_exception.mvtools_exception("test-showstopper")
        return True, None

class LaunchJobsTest(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("launch_jobs_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        v, r = mvtools_envvars.mvtools_envvar_write_toolbus_base(self.test_dir)
        if not v:
            return False, "Failed setting up toolbus envvar for testing."

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def testLaunchJobsVanilla(self):

        job1 = CustomJob()
        job1.add_entry(launch_jobs.BaseTask())

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertFalse(v)

    def testLaunchJobsVanillaNestedCustomJob(self):

        job1 = CustomJob()
        job2 = CustomJob()

        job1.add_entry(CustomTaskTrue())
        job2.add_entry(CustomTaskTrue())

        job1.add_entry(job2)

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertTrue(v)

    def testLaunchJobsVanillaNestedStandard(self):

        job1 = standard_job.StandardJob()
        job2 = standard_job.StandardJob()

        job1.add_entry(CustomTaskTrue())
        job2.add_entry(CustomTaskTrue())

        job1.add_entry(job2)

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertTrue(v)

    def testLaunchJobsVanillaNestedStandardFalse(self):

        job1 = standard_job.StandardJob()
        job2 = standard_job.StandardJob()

        job1.add_entry(CustomTaskTrue())
        job2.add_entry(CustomTaskFalse())

        job1.add_entry(job2)

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertFalse(v)

    def testLaunchJobsBigNestedStandard(self):

        test_ctx = aux_test_context()
        main_job = standard_job.StandardJob("main_job")

        job1 = standard_job.StandardJob("job1")
        job2 = standard_job.StandardJob("job2")
        job3 = standard_job.StandardJob("job3")

        task1 = CustomTaskTrue("task1")
        task2 = CustomTaskTrue("task2")
        task3 = CustomTaskTrue("task3")
        task4 = CustomTaskTrue("task4")

        task1.params["internal_testing_context"] = test_ctx
        task2.params["internal_testing_context"] = test_ctx
        task3.params["internal_testing_context"] = test_ctx
        task4.params["internal_testing_context"] = test_ctx

        main_job.add_entry(task1)
        job1.add_entry(task2)
        job2.add_entry(task3)
        job3.add_entry(task4)

        job2.add_entry(job3)
        main_job.add_entry(job1)
        main_job.add_entry(job2)

        v, r = launch_jobs.begin_execution(main_job, print)
        self.assertTrue(v)
        self.assertEqual(test_ctx.call_stack, ["CustomTaskTrue.run_task,task1", "CustomTaskTrue.run_task,task2", "CustomTaskTrue.run_task,task3", "CustomTaskTrue.run_task,task4"])

    def testLaunchJobsNestedStandardFailed(self):

        test_ctx = aux_test_context()
        main_job = standard_job.StandardJob("main_job")

        job1 = standard_job.StandardJob("job1")
        job2 = standard_job.StandardJob("job2")

        task1 = CustomTaskTrue("task1")
        task2 = CustomTaskFalse("task2")

        task1.params["internal_testing_context"] = test_ctx
        task2.params["internal_testing_context"] = test_ctx

        job1.add_entry(task1)
        job2.add_entry(task2)

        main_job.add_entry(job1)
        main_job.add_entry(job2)

        v, r = launch_jobs.begin_execution(main_job, print)
        self.assertFalse(v)
        self.assertEqual(test_ctx.call_stack, ["CustomTaskTrue.run_task,task1", "CustomTaskFalse.run_task,task2"])

    def testLaunchJobsCustomTask1(self):

        job1 = CustomJob()
        job1.add_entry(CustomTaskTrue())

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertTrue(v)

    def testLaunchJobsCustomTask2(self):

        job1 = CustomJob()
        job1.add_entry(CustomTaskTrue())
        job1.add_entry(CustomTaskFalse())

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertFalse(v)

    def testLaunchJobsCustomTaskParams1(self):

        job1 = CustomJob()
        job1.params["test"] = True
        job1.add_entry(CustomTaskParams())

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertTrue(v)

    def testLaunchJobsCustomTaskParams2(self):

        job1 = CustomJob()
        job1.params["test"] = False
        job1.add_entry(CustomTaskParams())

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertFalse(v)

    def testLaunchJobsCustomTaskParams3(self):

        job1 = CustomJob()
        job1.params["cause-except"] = True
        job1.add_entry(CustomTaskParams())

        try:
            v, r = launch_jobs.begin_execution(job1, print)
        except KeyError:
            pass
        except:
            self.fail("Unexpected exception")

    def testLaunchJobsCustomTaskParams4(self):

        job1 = CustomJob()
        job1.params["test1"] = True
        task1 = CustomTaskParams1And2()
        task1.params["test2"] = True
        job1.add_entry(task1)

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertTrue(v)

    def testLaunchJobsCustomTaskParams5(self):

        job1 = CustomJob()
        job1.params["test"] = True
        task1 = CustomTaskParams()
        task1.params["test"] = False
        job1.add_entry(task1)

        v, r = launch_jobs.begin_execution(job1, print)
        self.assertFalse(v)

    def testLaunchJobsTaskException1(self):

        job1 = standard_job.StandardJob("test job")
        job1.add_entry(CustomTaskException("test task"))

        v, r = launch_jobs.begin_execution(job1, print, "test-exec")
        self.assertFalse(v)

    def testLaunchJobsRunOptions1(self):

        main_job = standard_job.StandardJob()
        test_ctx = aux_test_context()

        task1 = CustomTaskFalse()
        task1.params["internal_testing_context"] = test_ctx

        job1 = standard_job.StandardJob()
        job1.add_entry(task1)

        job2 = standard_job.StandardJob()
        job2.add_entry(task1)

        main_job.add_entry(job1)
        main_job.add_entry(job2)

        v, r = launch_jobs.begin_execution(main_job, print)
        self.assertFalse(v)
        self.assertEqual(test_ctx.call_stack, ["CustomTaskFalse.run_task,None"])

    def testLaunchJobsRunOptionsEarlyAbort1(self):

        main_job = standard_job.StandardJob()
        test_ctx = aux_test_context()

        task1 = CustomTaskFalse()
        task1.params["internal_testing_context"] = test_ctx

        job1 = standard_job.StandardJob()
        job1.add_entry(task1)

        job2 = standard_job.StandardJob()
        job2.add_entry(task1)

        main_job.add_entry(job1)
        main_job.add_entry(job2)

        v, r = launch_jobs.begin_execution(main_job, print, options=launch_jobs.RunOptions(early_abort=False))
        self.assertFalse(v)
        self.assertEqual(test_ctx.call_stack, ["CustomTaskFalse.run_task,None", "CustomTaskFalse.run_task,None"])

    def testLaunchJobsRunOptionsEarlyAbort2(self):

        main_job = standard_job.StandardJob()
        test_ctx = aux_test_context()

        task1 = CustomTaskTrue()
        task1.params["internal_testing_context"] = test_ctx

        job1 = standard_job.StandardJob()
        job1.add_entry(task1)

        job2 = standard_job.StandardJob()
        job2.add_entry(task1)

        main_job.add_entry(job1)
        main_job.add_entry(job2)

        v, r = launch_jobs.begin_execution(main_job, print, options=launch_jobs.RunOptions(early_abort=False))
        self.assertTrue(v)
        self.assertEqual(test_ctx.call_stack, ["CustomTaskTrue.run_task,None", "CustomTaskTrue.run_task,None"])

    def testLaunchJobsRunOptionsTimeDelay1(self):

        job1 = CustomJob()
        job1.add_entry(CustomTaskTrue())

        v, r = launch_jobs.begin_execution(job1, print, options=launch_jobs.RunOptions(time_delay="2s"))
        self.assertTrue(v)

    def testLaunchJobsRunOptionsSignalDelay1(self):

        job1 = CustomJob()
        job1.add_entry(CustomTaskTrue())

        v, r = toolbus.set_signal("mvtools-launch-jobs-test-signal-delay-option", "set")
        self.assertTrue(v)

        v, r = launch_jobs.begin_execution(job1, print, options=launch_jobs.RunOptions(signal_delay="mvtools-launch-jobs-test-signal-delay-option"))
        self.assertTrue(v)

    def testLaunchJobsRunOptionsExecutionDelay1(self):

        first_exec = "first-exec"

        job1 = CustomJob()
        job1.add_entry(CustomTaskTrue())

        v, r = launch_jobs.begin_execution(job1, print, first_exec)
        self.assertTrue(v)

        v, r = launch_jobs.begin_execution(job1, print, options=launch_jobs.RunOptions(execution_delay=first_exec))
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
