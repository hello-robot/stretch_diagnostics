#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import Scope_Log_Sensor
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.dynamixel_hello_XL430
import stretch_body.dynamixel_XL430
import stretch_body.stretch_gripper
import time
from stretch_body.hello_utils import deg_to_rad,rad_to_deg
import click
class Test_DYNAMIXEL_check_zero_position(unittest.TestCase):
    """
    Test Dynamixel range of motions match expectations
    """
    test = TestBase('test_DYNAMIXEL_check_zero_position')

    def check_zero_position(self,servo,joint,prompt):
        self.assertTrue(servo.do_ping(), msg='Not able to ping servo %s' % joint)
        servo.disable_torque()
        click.secho(prompt, fg="yellow")
        input()
        servo.pull_status()
        bad_zero = abs(servo.status['pos'])>deg_to_rad(10.0)
        print('Measured zero_t of %f for %s. YAML zero_t of %f ticks'%(servo.status['pos_ticks'],joint, servo.params['zero_t']))
        print('Difference of %f degrees' % rad_to_deg(servo.status['pos']))
        msg = 'Measured zero_t of %f for %s is not near YAML zero_t of %f ticks. Check joint for mechanical issues and parameter settings.' % (servo.status['pos_ticks'],joint, servo.params['zero_t'])
        self.test.log_data(joint+'_measured_zero_t', servo.status['pos_ticks'])
        self.test.log_data(joint+'_yaml_zero_t', servo.params['zero_t'])
        self.assertFalse(bad_zero, msg=msg)
        servo.stop()

    def test_check_zero_position_head_tilt(self):
        """
        Check that head_tilt zero is approximately correct
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_tilt', chain=None)
        servo.startup()
        self.check_zero_position(servo,'head_tilt','Manually rotate head_tilt so that camera is pointing straight forward\nHit enter when ready.')


    def test_check_zero_position_head_pan(self):
        """
        Check that head_pan zero is approximately correct
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_pan', chain=None)
        servo.startup()
        self.check_zero_position(servo,'head_pan','Manually rotate head_pan so that camera is pointing straight forward\nHit enter when ready.')


    def test_check_zero_position_wrist_yaw(self):
        """
        Check that wrist_yaw zero is approximately correct
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='wrist_yaw', chain=None)
        servo.startup()
        if not servo.is_calibrated:
            servo.home()
        self.assertTrue(servo.is_calibrated,msg='Joint wrist_yaw requires calibration. Home joint and try again.')
        self.check_zero_position(servo,'wrist_yaw','Manually rotate wrist yaw so that gripper is pointing straight forward\nHit enter when ready.')


test_suite = TestSuite(test=Test_DYNAMIXEL_check_zero_position.test,failfast=False)

test_suite.addTest(Test_DYNAMIXEL_check_zero_position('test_check_zero_position_head_pan'))
test_suite.addTest(Test_DYNAMIXEL_check_zero_position('test_check_zero_position_head_tilt'))
test_suite.addTest(Test_DYNAMIXEL_check_zero_position('test_check_zero_position_wrist_yaw'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
