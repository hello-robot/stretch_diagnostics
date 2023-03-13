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
import stretch_body.pimu as pimu

class Test_STEPPER_sync(unittest.TestCase):
    """
    Test Stepper calibration data consistency
    """
    test = TestBase('test_STEPPER_sync')

    def stepper_sync(self,joint,xd,error_thresh):
        """
        Check that stepper motion halts on runstop
        """
        p=pimu.Pimu()
        self.assertTrue(p.startup())
        p.runstop_event_reset()
        p.push_command()

        log={'sync_x0':0,'sync_x1':0,'sync_x2':0}
        print('Testing sync on stepper %s'%joint)
        motor=stretch_body.stepper.Stepper('/dev/'+joint)
        self.assertTrue(motor.startup())

        print('Enabling sync and checking for small motion...')
        motor.pull_status()
        log['sync_x0']=motor.status['pos']
        motor.enable_sync_mode()
        motor.push_command()

        motor.set_command(motor.MODE_POS_TRAJ_INCR,x_des=xd)
        motor.push_command()
        time.sleep(1.5)

        motor.pull_status()
        log['sync_x1'] = motor.status['pos']

        p.trigger_motor_sync()
        time.sleep(1.5)

        motor.pull_status()
        log['sync_x2'] = motor.status['pos']

        self.test.log_data('test_sync_' + joint, log)

        #Check that no motion before pimu trigger
        error = abs(log['sync_x0'] - log['sync_x1'])
        msg = '%s: Waiting on sync and motion of %f (rad) relative to expected of %f' % (joint, error, 0)
        print(msg)
        self.assertTrue(error < error_thresh, msg=msg)  # Within error_thresh radians

        # Check that motion after pimu trigger
        error = abs(abs(log['sync_x1'] - log['sync_x2'])-xd)
        msg = '%s: Triggered sync and motion of %f (rad) relative to expected of %f' % (joint,abs(log['sync_x1'] - log['sync_x2']), xd)
        print(msg)
        self.assertTrue(error < error_thresh, msg=msg)  # Within error_thresh radians
        motor.stop()

    def test_sync_right_wheel(self):
        "Check that sync is working for the right wheel"
        self.stepper_sync('hello-motor-right-wheel',xd=1.0,error_thresh=0.2)

    def test_sync_left_wheel(self):
        "Check that sync is working for the left wheel"
        self.stepper_sync('hello-motor-left-wheel',xd=1.0,error_thresh=0.2)

    def test_sync_arm(self):
        "Check that sync is working for the arm"
        click.secho('Ensure ARM is not near its hardstop. Hit enter when ready', fg="yellow")
        input()
        self.stepper_sync('hello-motor-arm',xd=0.5,error_thresh=0.1)

    def test_sync_lift(self):
        "Check that sync is working for the lift"
        click.secho('Ensure LIFT is not near its hardstop. Hit enter when ready', fg="yellow")
        input()
        self.stepper_sync('hello-motor-lift',xd=0.5,error_thresh=0.2)

test_suite = TestSuite(test=Test_STEPPER_sync.test,failfast=False)
test_suite.addTest(Test_STEPPER_sync('test_sync_right_wheel'))
test_suite.addTest(Test_STEPPER_sync('test_sync_left_wheel'))
test_suite.addTest(Test_STEPPER_sync('test_sync_arm'))
test_suite.addTest(Test_STEPPER_sync('test_sync_lift'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
