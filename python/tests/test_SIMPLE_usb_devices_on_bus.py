#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_system_health.test_utils import Health_Test
from stretch_system_health.test_utils import Health_TestRunner, Heatlh_TestSuite
import unittest

class Test_SIMPLE_usb_devices_on_bus(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = Health_Test('test_SIMPLE_usb_devices_on_bus')

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

        for k in robot_devices.keys():
            with self.subTest(msg=k):
                self.assertTrue(robot_devices[k], msg='{} Not found'.format(k))
        print(yaml.dump(robot_devices))
        self.test.log_data('devices_on_usb',robot_devices)

test_suite = Health_TestSuite(bringup_test=Test_SIMPLE_usb_devices_on_bus.bringup_test)
test_suite.addTest(Test_SIMPLE_usb_devices_on_bus('test_usb_devices_on_bus'))

if __name__ == '__main__':
    runner = Health_TestRunner(test_suite)
    runner.run()
