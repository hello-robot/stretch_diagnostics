#!/usr/bin/env python3
import stretch_diagnostics.test_helpers as test_helpers
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.firmware_updater as firmware_updater
import sys


class Test_SIMPLE_firmware(unittest.TestCase):
    """
    Test firmware versions of PCBAs
    """
    test = TestBase('test_SIMPLE_firmware')
    use_device = {'hello-motor-arm': True, 'hello-motor-right-wheel': True, 'hello-motor-left-wheel': True,
                'hello-pimu': True, 'hello-wacc': True, 'hello-motor-lift': True}
    r = firmware_updater.FirmwareRecommended(use_device)
    
    def test_firmware_log_versions(self):
        """
            Log versions of installed firmware
        """

        # Log recommendations
        old_stdout = sys.stdout
        log_fn = self.test.test_result_dir + '/firmware_versions_%s.log' % self.test.timestamp
        print('Logging current firmware version to %s' % log_fn)
        log_file = open(log_fn, "w")
        sys.stdout = log_file
        self.r.pretty_print()
        sys.stdout = old_stdout
        log_file.close()
    
    def check_firmware_version(self, device_name):
        v=self.r.fw_installed.is_device_valid(device_name)
        if not v:
            self.assertTrue(0,'Firmware device not valid for device %s'%device_name)

        version = self.r.fw_installed.get_version(device_name)
        if self.r.recommended[device_name]!=None:
            if not self.r.recommended[device_name] == version:
                m='Firmware for %s not at latest version. See REx_firmware_updater.py'%device_name
                self.assertTrue(0,m)
    
    def test_arm_firmware(self):
        """
        Check Firmware of hello-motor-arm
        """
        self.check_firmware_version('hello-motor-arm')
    
    def test_right_wheel_firmware(self):
        """
        Check Firmware of hello-motor-right-wheel
        """
        self.check_firmware_version('hello-motor-right-wheel')
    
    def test_left_wheel_firmware(self):
        """
        Check Firmware of hello-motor-left-wheel
        """
        self.check_firmware_version('hello-motor-left-wheel')
    
    def test_pimu_firmware(self):
        """
        Check Firmware of hello-pimu
        """
        self.check_firmware_version('hello-pimu')
    
    def test_wacc_firmware(self):
        """
        Check Firmware of hello-wacc
        """
        self.check_firmware_version('hello-wacc')
    
    def test_lift_firmware(self):
        """
        Check Firmware of hello-motor-lift
        """
        self.check_firmware_version('hello-motor-lift')


test_suite = TestSuite(test=Test_SIMPLE_firmware.test,failfast=False)
test_suite.addTest(Test_SIMPLE_firmware('test_firmware_log_versions'))
test_suite.addTest(Test_SIMPLE_firmware('test_arm_firmware'))
test_suite.addTest(Test_SIMPLE_firmware('test_right_wheel_firmware'))
test_suite.addTest(Test_SIMPLE_firmware('test_left_wheel_firmware'))
test_suite.addTest(Test_SIMPLE_firmware('test_pimu_firmware'))
test_suite.addTest(Test_SIMPLE_firmware('test_wacc_firmware'))
test_suite.addTest(Test_SIMPLE_firmware('test_lift_firmware'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
