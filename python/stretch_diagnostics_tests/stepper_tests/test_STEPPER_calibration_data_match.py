#!/usr/bin/env python3
import stretch_diagnostics.test_helpers as test_helpers
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.stepper
import stretch_body.hello_utils as hu
import os
import  click
import time

class Test_STEPPER_calibration_data_match(unittest.TestCase):
    """
    Test Stepper calibration data consistency
    """
    test = TestBase('test_STEPPER_calibration_data_match')
    test.add_hint('Possible issue with stepper at udev / hardware / driver level')
    steppers = ['hello-motor-arm']#'hello-motor-right-wheel','hello-motor-left-wheel','hello-motor-arm','hello-motor-lift']


    def test_stepper_calibration_data_match(self):
        """
        Check that encoder calibration YAML matches what's in flash
        """
        all_match = True
        calibration_data_match_log = {}
        for s in self.steppers:
            if s=='hello-motor-lift':
                print()
                click.secho('Lift may drop. Place clamp under lift. Hit enter when ready', fg="yellow")
                input()
            m = stretch_body.stepper.Stepper(usb='/dev/' + s)
            self.assertTrue(m.startup(), msg='Not able to startup stepper %s' % s)
            print('Comparing flash data and encoder data for %s. This will take a minute...' % s)
            yaml_data=m.read_encoder_calibration_from_YAML()
            flash_data=m.read_encoder_calibration_from_flash()
            #time.sleep(1.0)
            #m.turn_rpc_interface_on()
            #m.stop()
            calibration_data_match_log[s]=(yaml_data == flash_data)
            if not calibration_data_match_log[s]:
                all_match = False
                self.test.add_hint('Encoder calibration in flash for %s does not match that in YAML. See REx_stepper_calibration_flash_to_YAML.py' % s)
        self.assertTrue(all_match, msg='Stepper calibration data is not consistent. Repair needed.')
        self.test.log_data('encoder_calibration_files', calibration_data_match_log)

    def test_stepper_startup_after_flash_read(self):
        for s in self.steppers:
            m = stretch_body.stepper.Stepper(usb='/dev/' + s)
            self.assertTrue(m.startup(), msg='Not able to startup stepper %s' % s)
            #m.stop()


test_suite = TestSuite(test=Test_STEPPER_calibration_data_match.test,failfast=False)
test_suite.addTest(Test_STEPPER_calibration_data_match('test_stepper_calibration_data_match'))
#test_suite.addTest(Test_STEPPER_calibration_data_match('test_stepper_startup_after_flash_read'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
