#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_wellness.test_base import TestBase
from stretch_wellness.test_runner import TestRunner
from stretch_wellness.test_suite import TestSuite
from stretch_wellness.test_helpers import get_rs_details
import unittest
import subprocess

class Test_SIMPLE_realsense_status(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_realsense_status')
    test.hint = []

    def test_realsense_on_usb_bus(self):
        """
        Check that Realsense camera is on USB bus.
        """
        print('---- Checking for Intel D435i ----')
        cmd = "lsusb -d 8086:0b3a"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        returned_value=1
        if returned_value!=0:
            self.test.add_hint('Realsense not on bus. Check camera cables')
        self.assertEqual(returned_value,0)

    def test_realsense_details(self):
        """
        Capture realsense details and log
        """
        d=get_rs_details()
        d=None
        if d is None:
            self.test.add_hint('Realsense driver may be conflicting with ROS. Reboot and try again')
        self.assertIsNotNone(d)
        self.test.log_data('realsense_details',d)

test_suite = TestSuite(test=Test_SIMPLE_realsense_status.test,failfast=False)
test_suite.addTest(Test_SIMPLE_realsense_status('test_realsense_on_usb_bus'))
test_suite.addTest(Test_SIMPLE_realsense_status('test_realsense_details'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
