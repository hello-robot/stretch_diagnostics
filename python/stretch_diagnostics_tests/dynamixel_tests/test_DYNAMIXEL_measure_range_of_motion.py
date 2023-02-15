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
import click

class Test_DYNAMIXEL_measure_range_of_motion(unittest.TestCase):
    """
    Test Dynamixel range of motions match expectations
    """
    test = TestBase('test_DYNAMIXEL_measure_range_of_motion')
    range_t_nominal = {'head_pan':[67.0, 3870.0],'head_tilt':[1726.0, 3347.0],'wrist_yaw':[44.0, 9140.0],'stretch_gripper':[0, 8186]} #TODO: Numbers based on a Stretch 2 (2001), may differ for RE1.

    def measure_range(self,servo,joint):
        self.assertTrue(servo.startup(),msg='Not able to connect to servo %s'%joint)
        self.assertTrue(servo.do_ping(), msg='Not able to ping servo %s' % joint)
        servo.pull_status()

        dr=abs(servo.params['range_t'][0]-servo.params['range_t'][1])
        dn = abs(self.range_t_nominal[joint][0] - self.range_t_nominal[joint][1])
        bad_yaml_range = abs(dr-dn)>0.1*dr #within 10%
        msg='YAML |range_t|=%f for %s is not near expected |range_t| of %f ticks. Try running REx_calibrate_range.py --%s.'%(dn,joint,dr,joint)
        self.assertFalse(bad_yaml_range,msg=msg)

        servo.params['req_calibration'] = 1

        success, measured = servo.home(single_stop=False, move_to_zero=True, delay_at_stop=1.0, save_calibration=False,set_homing_offset=False)
        self.assertTrue(success,msg='Failed to measure joint range')

        dr = abs(measured[0] - measured[1])
        bad_yaml_range = abs(dr-dn)>0.1*dr #within 10%
        msg = 'Measured |range_t|=%f for %s is not near expected |range_t| of %f ticks. Try running REx_calibrate_range.py --%s' % (dn,joint, dr,joint)
        self.assertFalse(bad_yaml_range, msg=msg)

        servo.stop()

        return measured,servo.params['range_t']

    def test_measure_range_head_pan(self):
        """
        Measure range of motion for head_pan
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_pan', chain=None)
        measured,yaml=self.measure_range(servo,'head_pan')
        self.test.log_data('measured_range_t', list(measured))
        self.test.log_data('yaml_range_t', list(yaml))

    def test_measure_range_head_tilt(self):
        """
        Measure range of motion for head_tilt
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_tilt', chain=None)
        measured,yaml=self.measure_range(servo,'head_tilt')
        self.test.log_data('measured_range_t', list(measured))
        self.test.log_data('yaml_range_t', list(yaml))

    def test_measure_range_wrist_yaw(self):
        """
        Measure range of motion for wrist_yaw
        """
        print()
        click.secho('Ensure wrist yaw is free to move through its range of motion. Hit enter when ready', fg="yellow")
        input()
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='wrist_yaw', chain=None)
        measured,yaml=self.measure_range(servo,'wrist_yaw')
        self.test.log_data('measured_range_t', list(measured))
        self.test.log_data('yaml_range_t', list(yaml))

test_suite = TestSuite(test=Test_DYNAMIXEL_measure_range_of_motion.test,failfast=False)

test_suite.addTest(Test_DYNAMIXEL_measure_range_of_motion('test_measure_range_head_pan'))
test_suite.addTest(Test_DYNAMIXEL_measure_range_of_motion('test_measure_range_head_tilt'))
test_suite.addTest(Test_DYNAMIXEL_measure_range_of_motion('test_measure_range_wrist_yaw'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
