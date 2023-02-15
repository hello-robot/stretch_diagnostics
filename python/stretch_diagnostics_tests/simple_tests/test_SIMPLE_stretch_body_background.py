#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import serial
import fcntl

class Test_SIMPLE_stretch_body_background(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_stretch_body_background')

    def test_stretch_body_background(self):
        """
        Check for background processes blocking serial ports
        """
        robot_devices = {'/dev/hello-wacc': False,
                         '/dev/hello-motor-left-wheel': False,
                         '/dev/hello-pimu': False,
                         '/dev/hello-lrf': False,
                         '/dev/hello-dynamixel-head': False,
                         '/dev/hello-dynamixel-wrist': False,
                         '/dev/hello-motor-arm': False,
                         '/dev/hello-motor-right-wheel': False,
                         '/dev/hello-motor-lift': False}
        for d in robot_devices:
            try:
                ser = serial.Serial(d)
                if ser.isOpen():
                    try:
                        fcntl.flock(ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except IOError:
                        robot_devices[d]=True
            except OSError:
                pass

        self.test.log_data('robot_devices_on_bus',robot_devices)

        for d in robot_devices:
            print('Device %s on bus: %d' %(d,robot_devices[d]))
            self.assertFalse(robot_devices[d], msg='Port %s is busy. Another Stretch Body process is already running' % d)


test_suite = TestSuite(test=Test_SIMPLE_stretch_body_background.test,failfast=False)
test_suite.addTest(Test_SIMPLE_stretch_body_background('test_stretch_body_background'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
