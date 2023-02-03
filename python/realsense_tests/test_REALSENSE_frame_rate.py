#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_helpers import Dmesg_monitor, get_rs_details
from colorama import Fore, Style
from subprocess import Popen, PIPE, STDOUT
import time
import numpy as np
import click
import stretch_body.robot
import subprocess
from tabulate import tabulate


def create_config_target_hi_res():
    f = open('/tmp/d435i_confg.cfg', "w+")
    config_script = ["DEPTH,1280,720,30,Z16,0",
                     "COLOR,1920,1080,30,RGB8,0",
                     "ACCEL,1,1,63,MOTION_XYZ32F",
                     "GYRO,1,1,200,MOTION_XYZ32F"]

    header = ["STREAM", "WIDTH", "HEIGHT", "FPS", "FORMAT", "STREAM_INDEX"]
    config_data = []
    check_log.append("Camera Stream Config:")
    for ll in config_script:
        f.write(ll + "\n")
        config_data.append(ll.split(','))
    config_table = str(tabulate(config_data, headers=header, tablefmt='github')).split('\n')

    f.close()
    target = {'duration': 31,
              'nframe': 900,
              'margin': 16,
              'streams': {
                  'Color': {'target': 900, 'sampled': 0},
                  'Depth': {'target': 900, 'sampled': 0},
                  'Accel': {'target': 900, 'sampled': 0},
                  'Gyro': {'target': 900, 'sampled': 0}}}
    return target


def create_config_target_low_res():
    f = open('/tmp/d435i_confg.cfg', "w+")
    config_script = ["DEPTH,424,240,30,Z16,0",
                     "COLOR,424,240,30,RGB8,0",
                     "ACCEL,1,1,63,MOTION_XYZ32F",
                     "GYRO,1,1,200,MOTION_XYZ32F"]

    header = ["STREAM", "WIDTH", "HEIGHT", "FPS", "FORMAT", "STREAM_INDEX"]
    config_data = []
    for ll in config_script:
        f.write(ll + "\n")
        config_data.append(ll.split(','))
    config_table = str(tabulate(config_data, headers=header, tablefmt='github')).split('\n')

    f.close()
    target = {'duration': 31,
              'nframe': 900,
              'margin': 16,
              'streams': {
                  'Color': {'target': 900, 'sampled': 0},
                  'Depth': {'target': 900, 'sampled': 0},
                  'Accel': {'target': 900, 'sampled': 0},
                  'Gyro': {'target': 900, 'sampled': 0}}}
    return target


class Test_REALSENSE_frame_rate(unittest.TestCase):
    """
    Testing the frame rate capture performance of realsense
    """

    # test object is always expected within a TestCase Class
    test = TestBase('test_REALSENSE_cable')
    test.add_hint("Realsense cable might be having issues.")

    @classmethod
    def setUpClass(self):
        dmesg_log_fn = "{}/{}_{}.log".format(self.test.results_directory_test_specific,
                                             "dmesg",
                                             self.test.timestamp)
        self.dmesg = Dmesg_monitor(print_new_msg=True, log_fn=dmesg_log_fn)
        self.dmesg.start()

    @classmethod
    def tearDownClass(self):
        self.dmesg.stop()
        print("\nCollected DMESG")
        print("---------------")
        for l in self.dmesg.output_list:
            print(l)

    def test_USB3_2_connection(self):
        """
        Check that Realsense camera is on USB3.2 connection
        """
        out = Popen("rs-enumerate-devices| grep Usb | grep 3.2", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                    close_fds=True).stdout.read()

        if len(out):
            print('Confirmed USB 3.2 connection to realsense device')
        else:
            self.add_hint('Did not find USB 3.2 connection to realsense device')
        self.assertIsNot(len(out), 0, msg='Did not find USB 3.2 connection to realsense device')

    def test_realsense_on_usb_bus(self):
        """
        Check that Realsense camera is on USB bus.
        """
        print('---- Checking for Intel D435i ----')
        cmd = "lsusb -d 8086:0b3a"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        if returned_value != 0:
            self.test.add_hint('Realsense D435i not found at USB Bus')
        self.assertEqual(returned_value, 0)

    def test_realsense_details(self):
        """
        Capture realsense details and log
        """
        d = get_rs_details()
        if d is None:
            self.test.add_hint('Not able to launch Realsense driver. It may be conflicting with ROS')
        self.assertIsNotNone(d)
        self.test.log_data('realsense_details', d)

    def test_frame_rate_high_res(self):
        pass

    def test_frame_rate_low_res(self):
        pass


test_suite = TestSuite(test=Test_REALSENSE_frame_rate.test, failfast=False)
test_suite.addTest(Test_REALSENSE_frame_rate('test_USB3_2_connection'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_realsense_on_usb_bus'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_realsense_details'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_frame_rate_high_res'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_frame_rate_low_res'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
