#!/usr/bin/env python3
import stretch_diagnostics.test_helpers as test_helpers
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.stepper
import stretch_body.hello_utils as hu
import stretch_factory.firmware_updater as firmware_updater
import sys
class Test_SIMPLE_firmware(unittest.TestCase):
    """
    Test firmware versions of PCBAs
    """
    test = TestBase('test_SIMPLE_firmware')


    def test_firmware_log_versions(self):
        """
            Log versions of installed firmware
        """
        use_device = {'hello-motor-arm': True, 'hello-motor-right-wheel': True, 'hello-motor-left-wheel': True,
                      'hello-pimu': True, 'hello-wacc': True, 'hello-motor-lift': True}
        r = firmware_updater.RecommendedFirmware(use_device)
        # Log recommendations
        old_stdout = sys.stdout
        log_fn = self.test.test_result_dir + '/firmware_versions_%s.log' % self.test.timestamp
        print('Logging current firmware version to %s' % log_fn)
        log_file = open(log_fn, "w")
        sys.stdout = log_file
        r.pretty_print()
        sys.stdout = old_stdout
        log_file.close()
    def test_firmware_version(self):
        """
            Check if at recommended firmware versions
        """
        use_device = {'hello-motor-arm': True, 'hello-motor-right-wheel': True, 'hello-motor-left-wheel': True,
                      'hello-pimu': True, 'hello-wacc': True, 'hello-motor-lift': True}
        r = firmware_updater.RecommendedFirmware(use_device)
        #Check for issues
        all_valid=True
        all_up_to_date=True
        for device_name in r.recommended.keys():
            v=r.fw_installed.is_device_valid(device_name)
            if not v:
                all_valid=False
                self.assertTrue(0,'Firmware device not valid for device %s'%device_name)

            version = r.fw_installed.get_version(device_name)
            if r.recommended[device_name]!=None:
                if not r.recommended[device_name] == version:
                    all_up_to_date=False
                    m='Firmware for %s not at latest version. See REx_firmware_updater.py'%device_name
                    self.assertTrue(0,m)

        self.assertTrue(all_valid,msg='Not all devices on bus')
        self.assertTrue(all_up_to_date, 'Firmware not up to date on all devices')

test_suite = TestSuite(test=Test_SIMPLE_firmware.test,failfast=False)
test_suite.addTest(Test_SIMPLE_firmware('test_firmware_log_versions'))
test_suite.addTest(Test_SIMPLE_firmware('test_firmware_version'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
