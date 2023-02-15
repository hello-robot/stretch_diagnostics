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

# Include all the known kernel non problematic messages here
# index     1:no.occured 2:no.Acceptable_Occurances 3:Message
known_msgs = [[0, 30, 'uvcvideo: Failed to query (GET_CUR) UVC control'],
              [0, 15, 'Non-zero status (-71) in video completion handler'],
              [0, 15, 'No report with id 0xffffffff found'],
              [0, 10, 'uvcvideo: Found UVC 1.50 device Intel(R) RealSense(TM) Depth Camera 435'],
              [0, 5, 'uvcvideo: Unable to create debugfs'],
              [0, 4, 'hid-sensor-hub'],
              [0, 6, 'input: Intel(R) RealSense(TM) Depth Ca'],
              [0, 1, 'uvcvideo: Failed to resubmit video URB (-1).'],
              [0, 1, 'Netfilter messages via NETLINK v0.30.'],
              [0, 1, 'USB disconnect']]


def scan_head_sequence(robot):
    """
    Head Pan Tilt Sequence for 30s
    """
    robot.head.home()
    time.sleep(1)

    n = 15
    delay = 0.1
    tilt_moves = np.linspace(-1.57, 0, n)
    pan_moves = np.linspace(1.57, -3.14, n)

    for j in range(0, 3):
        for i in range(n):
            robot.head.move_to('head_tilt', tilt_moves[i])
            robot.head.move_to('head_pan', pan_moves[i])
            time.sleep(delay)
        time.sleep(0.8)

        for i in range(n):
            robot.head.move_to('head_tilt', np.flip(tilt_moves)[i])
            robot.head.move_to('head_pan', np.flip(pan_moves)[i])
            time.sleep(delay)
        time.sleep(0.8)

        for i in range(n):
            robot.head.move_to('head_tilt', np.flip(tilt_moves)[i])
            robot.head.move_to('head_pan', pan_moves[i])
            time.sleep(delay)
        time.sleep(0.8)

        for i in range(n):
            robot.head.move_to('head_tilt', tilt_moves[i])
            robot.head.move_to('head_pan', np.flip(pan_moves)[i])
            time.sleep(delay)
        time.sleep(0.8)

    robot.head.home()


class Test_REALSENSE_cable(unittest.TestCase):
    """
    Testing the functioning of the Realsense cable
    """

    # test object is always expected within a TestCase Class
    test = TestBase('test_REALSENSE_cable')


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

        self.assertIsNot(len(out), 0, msg='Did not find USB 3.2 connection to realsense device')

    def test_realsense_on_usb_bus(self):
        """
        Check that Realsense camera is on USB bus.
        """
        print('---- Checking for Intel D435i ----')
        cmd = "lsusb -d 8086:0b3a"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        self.assertEqual(returned_value, 0,'Realsense D435i not found at USB Bus')

    def test_realsense_details(self):
        """
        Capture realsense details and log
        """
        d = get_rs_details()
        self.assertIsNotNone(d,'Not able to launch Realsense driver. It may be conflicting with ROS')
        self.test.log_data('realsense_details', d)

    def check_dmesg(self, msgs):
        unknown_msgs = []
        excessive_msgs = []
        unexpected_msgs = []
        no_error = True
        for m in msgs:
            if len(m):
                found = False
                for i in range(len(known_msgs)):
                    if m.find(known_msgs[i][2]) != -1:
                        found = True
                        known_msgs[i][0] = known_msgs[i][0] + 1
                if not found:
                    unknown_msgs.append(m)
        for i in range(len(known_msgs)):
            if known_msgs[i][0] >= known_msgs[i][1]:

                print(Fore.YELLOW + '[Warning] Excessive dmesg warnings (%d) of: %s' % (
                known_msgs[i][0], known_msgs[i][2]))
                excessive_msgs.append(known_msgs[i][2])
                no_error = False
        if len(unknown_msgs):
            print('[Warning] Unexpected dmesg warnings (%d)' % len(unknown_msgs))
            unexpected_msgs = unknown_msgs
            no_error = False
            for i in unknown_msgs:
                print(i)
        if no_error:
            print(Fore.GREEN + '[Pass] No unexpected dmesg warnings')
        print(Style.RESET_ALL)
        self.test.log_data("excessive_dmesgs", excessive_msgs)
        self.test.log_data("unexpected_dmesgs", unexpected_msgs)
        self.assertTrue(no_error, "Errors captured in DMESGs.")

    def test_monitor_dmesg_with_head_motion(self):
        """
        Move head pan-tilt continuously for 30s and observe USB messages in DMESG
        """
        robot = stretch_body.robot.Robot()
        input(click.style(
            "Make sure the head is free to move without obstructions. The head will spin for 2 minutes. Press ENTER",
            fg="yellow", bold=True))
        print("Started Head rotation....")
        self.assertTrue(robot.startup(), "Unable to startup the robot")
        scan_head_sequence(robot)
        scan_head_sequence(robot)
        scan_head_sequence(robot)
        scan_head_sequence(robot)
        robot.stop()
        print("Stoped Head rotation....")
        self.check_dmesg(self.dmesg.output_list)


test_suite = TestSuite(test=Test_REALSENSE_cable.test, failfast=False)
test_suite.addTest(Test_REALSENSE_cable('test_USB3_2_connection'))
test_suite.addTest(Test_REALSENSE_cable('test_realsense_on_usb_bus'))
test_suite.addTest(Test_REALSENSE_cable('test_realsense_details'))
test_suite.addTest(Test_REALSENSE_cable('test_monitor_dmesg_with_head_motion'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
