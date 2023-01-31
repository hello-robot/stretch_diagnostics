#!/usr/bin/env python3
import unittest
import psutil
import subprocess
import time
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_CPU_usage_temp(unittest.TestCase):
    """
    This stress-tests the CPU and monitors its usage and temperature.
    """

    test = TestBase('test_CPU_usage_temp')
    test.add_hint("This test is for monitoring CPU usage and temperature.")

    @classmethod
    def setUpClass(self):
        print('Starting CPU stress test. This test will take 20 seconds.')
        subprocess.Popen("stress -c 4 --timeout 20s", shell=True)

        pass

    @classmethod
    def tearDownClass(self):

        pass

    def test_CPU_usage(self):
        """
        Test CPU usage is within acceptable limits
        """
        
        time.sleep(14)
        # Calling psutil.cpu_precent() for 4 seconds
        usage = psutil.cpu_percent(4)
        print('The CPU usage is: ', usage)

        self.test.log_data('test_cpu_usage', usage)

        if usage > 55: # CPU usage must be less than 55%
            self.test.add_hint("Kill all running processes before running diagnostics.")
        self.assertLess(usage, 55)

    def test_CPU_temp(self):
        """
        Test CPU temperature is within acceptable limits
        """
        
        time.sleep(14)
        temperature = psutil.sensors_temperatures()
        print('The CPU temperature is: ', temperature['coretemp'][0][1])

        self.test.log_data('test_cpu_temperature', temperature)

        if temperature > 90: # CPU temperature must be less than 90 deg C
            self.test.add_hint("Kill all running processes before running diagnostics.")
            self.test.add_hint("Monitor CPU temperature and ensure CPU fan turns on.")
        
        self.assertLess(temperature, 90)


test_suite = TestSuite(test=Test_CPU_usage_temp.test, failfast=False)

test_suite.addTest(Test_CPU_usage_temp('test_CPU_usage'))
test_suite.addTest(Test_CPU_usage_temp('test_CPU_temp'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
