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
import click
import time
import stretch_body.pimu as pimu

class Test_STEPPER_power(unittest.TestCase):
    """
    Test Stepper motors if it is being powered
    """
    test = TestBase('test_STEPPER_power')

    def check_stepper_power(self,stepper_name,xd):
        """
        Check that the stepper motors have a non-zero current during the movement
        """
        motor=stretch_body.stepper.Stepper('/dev/'+stepper_name)
        self.assertTrue(motor.startup())
        motor.disable_sync_mode()
        motor.set_command(motor.MODE_POS_TRAJ_INCR,x_des=xd, stiffness=1)
        motor.push_command()
        time.sleep(0.5)
        motor.pull_status()
        status = motor.status
        self.test.log_data(f"{stepper_name}_status", status)
        self.assertGreater(status['current'], 0.000000000001, f"{stepper_name} has a zero current, check power cable.")
        motor.stop()

    def test_sync_right_wheel(self):
        "Check that sync is working for the right wheel"
        self.check_stepper_power('hello-motor-right-wheel',xd=0.1)

    def test_sync_left_wheel(self):
        "Check that sync is working for the left wheel"
        self.check_stepper_power('hello-motor-left-wheel',xd=0.1)

    def test_sync_arm(self):
        "Check that sync is working for the arm"
        click.secho('Ensure ARM is not near its hardstop. Hit enter when ready', fg="yellow")
        input()
        self.check_stepper_power('hello-motor-arm',xd=0.1)

    def test_sync_lift(self):
        "Check that sync is working for the lift"
        click.secho('Ensure LIFT is not near its hardstop. Hit enter when ready', fg="yellow")
        input()
        self.check_stepper_power('hello-motor-lift',xd=0.1)

test_suite = TestSuite(test=Test_STEPPER_power.test,failfast=False)
test_suite.addTest(Test_STEPPER_power('test_sync_right_wheel'))
test_suite.addTest(Test_STEPPER_power('test_sync_left_wheel'))
test_suite.addTest(Test_STEPPER_power('test_sync_arm'))
test_suite.addTest(Test_STEPPER_power('test_sync_lift'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
