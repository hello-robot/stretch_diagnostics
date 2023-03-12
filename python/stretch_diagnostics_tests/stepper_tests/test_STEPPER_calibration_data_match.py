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

    def stepper_calibration_data_match(self,s):
        """
        Check that encoder calibration YAML matches what's in flash
        """
        m = stretch_body.stepper.Stepper(usb='/dev/' + s)
        self.assertTrue(m.startup(), msg='Not able to startup stepper %s' % s)
        print('Comparing flash data and encoder data for %s. This will take a minute...' % s)
        log={}
        log['yaml_data']=m.read_encoder_calibration_from_YAML()
        log['flash_data']=m.read_encoder_calibration_from_flash()
        #time.sleep(1.0)
        #m.turn_rpc_interface_on()
        #m.stop()
        log['match']=(log['yaml_data'] == log['flash_data'])
        self.check_if_calibration_corrupted(log['flash_data'])
        self.assertTrue(log['match'],'Encoder calibration in flash for %s does not match that in YAML. See REx_stepper_calibration_flash_to_YAML.py' % s)
        self.test.log_data('encoder_calibration_%s'%s, log)

    def check_if_calibration_corrupted(self, data):
        """
        Function to check if the collected data is corrupt
        """
        Target_data_len = 16384
        self.test.log_params('target_data_len', Target_data_len)
        self.assertEqual(len(data), Target_data_len, msg='Incorrect encoder data length.')

        cnt = 0
        for d in data:
            if d == float(0):
                cnt = cnt + 1
        self.assertGreaterEqual(Target_data_len / 2,cnt, msg='Invalid Encoder Data. Non-zero data expected.')

    def test_calibration_data_match_lift(self):
        """
        Check that LIFT encoder calibration YAML matches what's in flash
        """
        print()
        click.secho('Lift may drop. Place clamp under lift. Hit enter when ready', fg="yellow")
        input()
        self.stepper_calibration_data_match('hello-motor-lift')

    def test_calibration_data_match_arm(self):
        """
        Check that ARM encoder calibration YAML matches what's in flash
        """
        self.stepper_calibration_data_match('hello-motor-arm')

    def test_calibration_data_match_left_wheel(self):
        """
        Check that LEFT WHEEL encoder calibration YAML matches what's in flash
        """
        self.stepper_calibration_data_match('hello-motor-left-wheel')

    def test_calibration_data_match_right_wheel(self):
        """
        Check that RIGHT WHEEL encoder calibration YAML matches what's in flash
        """
        self.stepper_calibration_data_match('hello-motor-right-wheel')

    def test_stepper_startup_after_flash_read(self):
        for s in self.steppers:
            m = stretch_body.stepper.Stepper(usb='/dev/' + s)
            self.assertTrue(m.startup(), msg='Not able to startup stepper %s' % s)
            #m.stop()


test_suite = TestSuite(test=Test_STEPPER_calibration_data_match.test,failfast=False)
test_suite.addTest(Test_STEPPER_calibration_data_match('test_calibration_data_match_lift'))
test_suite.addTest(Test_STEPPER_calibration_data_match('test_calibration_data_match_arm'))
test_suite.addTest(Test_STEPPER_calibration_data_match('test_calibration_data_match_right_wheel'))
test_suite.addTest(Test_STEPPER_calibration_data_match('test_calibration_data_match_left_wheel'))
#test_suite.addTest(Test_STEPPER_calibration_data_match('test_stepper_startup_after_flash_read'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
