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

class Test_GRIPPER_broken_string(unittest.TestCase):
    """
    Test Gripper for mechanical issues
    """
    test = TestBase('test_GRIPPER_broken_string')

    def test_broken_string(self):
        """
        Check range of servo motion for broken string
        """
        servo = stretch_body.stretch_gripper.StretchGripper()
        self.assertTrue(servo.startup(), msg='Not able to connect to servo stretch_gripper')
        self.assertTrue(servo.do_ping(), msg='Not able to ping servo stretch_gripper')
        servo.pull_status()
        x0=servo.status['pos']
        print('Starting at position %f (rad)'%x0)
        servo.enable_pwm()
        servo.set_pwm(servo.params['pwm_homing'][0])
        ts = time.time()
        time.sleep(1.0)
        timeout = False
        pos_log=[x0]

        while servo.motor.is_moving() and not timeout:
            #print(servo.motor.is_moving())
            timeout = time.time() - ts > 10.0
            time.sleep(0.1)
            servo.pull_status()
            pos_log.append(servo.status['pos'])
            print("Pos: %f"%servo.status['pos'])
        servo.stop()
        print('Test stopped at position %f (rad)'%pos_log[-1])
        print('Motion stopped in %f seconds'%(time.time()-ts))
        servo.set_pwm(0)
        if timeout:
            self.test.add_hint('Gripper servo motion did not stop during homing. Possible broken string')
        self.assertFalse(timeout,msg='Gripper servo motion did not stop during homing. Possible broken string')
        self.test.log_data('stretch_gripper_pos_log', pos_log)

test_suite = TestSuite(test=Test_GRIPPER_broken_string.test,failfast=False)
test_suite.addTest(Test_GRIPPER_broken_string('test_broken_string'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
