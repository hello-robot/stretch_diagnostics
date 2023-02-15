#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest

class Test_SIMPLE_usb_devices_on_bus(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_usb_devices_on_bus')

    def test_ttyACMx_devices_on_bus(self):
        """
        Verify if all the hello-* usb devices are present in the bus
        """
        ttyACM_devices = {'/dev/ttyACM0': False,
                         '/dev/ttyACM1': False,
                         '/dev/ttyACM2': False,
                         '/dev/ttyACM3': False,
                         '/dev/ttyACM4': False,
                         '/dev/ttyACM5': False}

        listOfFiles = os.listdir('/dev')
        pattern = "hello*"
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                ttyACM_devices[entry] = True

        for k in ttyACM_devices:
            with self.subTest(msg=k):
                self.assertTrue(ttyACM_devices[k], msg='{} Not found'.format(k))
        print(yaml.dump(ttyACM_devices))
        self.test.log_data('devices_on_usb',ttyACM_devices)
    def test_usb_devices_on_bus(self):
        """
        Verify if all the hello-* usb devices are present in the bus
        """
        robot_devices = {'hello-wacc': False,
                         'hello-motor-left-wheel': False,
                         'hello-pimu': False,
                         'hello-lrf': False,
                         'hello-dynamixel-head': False,
                         'hello-dynamixel-wrist': False,
                         'hello-motor-arm': False,
                         'hello-motor-right-wheel': False,
                         'hello-motor-lift': False,
                         'hello-respeaker': False}

        listOfFiles = os.listdir('/dev')
        pattern = "hello*"
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                robot_devices[entry] = True

        for k in robot_devices:
            with self.subTest(msg=k):
                self.assertTrue(robot_devices[k], msg='{} Not found'.format(k))
        print(yaml.dump(robot_devices))
        self.test.log_data('devices_on_usb',robot_devices)

test_suite = TestSuite(test=Test_SIMPLE_usb_devices_on_bus.test,failfast=False)
test_suite.addTest(Test_SIMPLE_usb_devices_on_bus('test_usb_devices_on_bus'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
