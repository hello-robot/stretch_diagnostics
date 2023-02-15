#!/usr/bin/env python3
import unittest
import psutil
import subprocess
import time
import os
import signal
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_CPU_usage_temp(unittest.TestCase):
    """
    This stress-tests the CPU and monitors its usage and temperature.
    """

    test = TestBase('test_CPU_usage_temp')

    @classmethod
    def setUpClass(self):
        print('Starting CPU stress test. This test will take 40 seconds.')
        subprocess.Popen("stress -c 4", shell=True)

    @classmethod
    def tearDownClass(self):
        for line in os.popen("ps ax | grep stress | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid), signal.SIGKILL)

    def test_CPU_usage(self):
        """
        Test CPU usage is within acceptable limits
        """
        
        time.sleep(15)
        # Calling psutil.cpu_precent() for 4 seconds
        usage = psutil.cpu_percent(4)
        print('The CPU usage is: {}%'.format(usage))

        self.test.log_data('test_cpu_usage', usage)

        self.assertLess(usage, 55,"CPU usage of %f already high. Kill all running processes before running diagnostics."%usage)

    def test_CPU_temp(self):
        """
        Test CPU temperature is within acceptable limits
        """
        
        time.sleep(20)
        temperature = psutil.sensors_temperatures()['coretemp'][0][1]
        print('The CPU temperature is: ', '{} degC'.format(temperature))

        self.test.log_data('test_cpu_temperature', temperature)
        
        self.assertLess(temperature, 90, 'CPU temp of %f already high. Kill all running processes before running diagnostics.'%temperature)


test_suite = TestSuite(test=Test_CPU_usage_temp.test, failfast=False)

test_suite.addTest(Test_CPU_usage_temp('test_CPU_usage'))
test_suite.addTest(Test_CPU_usage_temp('test_CPU_temp'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
