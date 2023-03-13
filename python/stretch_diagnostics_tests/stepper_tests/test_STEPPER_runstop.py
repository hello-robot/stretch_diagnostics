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

class Test_STEPPER_runstop(unittest.TestCase):
    """
    Test Stepper calibration data consistency
    """
    test = TestBase('test_STEPPER_runstop')

    def stepper_runstop(self,joint,xd,error_thresh):
        """
        Check that stepper motion halts on runstop
        """
        p=pimu.Pimu()
        self.assertTrue(p.startup())
        log={'runstop_off_x0':0,'runstop_off_x1':0,'runstop_on_x0':0,'runstop_on_x1':0}
        print('Testing runstop on stepper %s'%joint)
        motor=stretch_body.stepper.Stepper('/dev/'+joint)
        self.assertTrue(motor.startup())
        motor.disable_sync_mode()
        motor.push_command()

        motor.pull_status()
        log['runstop_off_x0']=motor.status['pos']
        print('Reseting runstop and checking for small motion...')

        p.runstop_event_reset()
        p.push_command()

        motor.set_command(motor.MODE_POS_TRAJ_INCR,x_des=xd)
        motor.push_command()
        time.sleep(1.5)
        motor.pull_status()
        log['runstop_off_x1'] = motor.status['pos']
        self.test.log_data('test_runstop_'+joint, log)
        error=abs(abs(log['runstop_off_x1']-log['runstop_off_x0'])-xd)
        msg='%s: Runstop off and motion of %f (rad) relative to expected of %f'%(joint,abs(log['runstop_off_x1']-log['runstop_off_x0']),xd)
        print(msg)
        self.assertTrue(error<error_thresh,msg=msg) #Within error_thresh radians

        print('Triggering runstop and checking for no motion...')
        p.runstop_event_trigger()
        p.push_command()
        time.sleep(0.5)
        motor.pull_status()
        log['runstop_on_x0']=motor.status['pos']
        motor.set_command(motor.MODE_POS_TRAJ_INCR, x_des=xd)
        motor.push_command()
        time.sleep(1.5)
        motor.pull_status()
        log['runstop_on_x1'] = motor.status['pos']
        self.test.log_data('test_runstop_' + joint, log)
        error = abs(log['runstop_on_x1'] - log['runstop_on_x0'])
        msg = '%s: Runstop on and motion of %f (rad) relative to expected of %f' % (joint,error, 0)
        print(msg)
        self.assertTrue(error < error_thresh, msg=msg)  # Within error_thresh radians
        p.runstop_event_reset()
        p.push_command()
        motor.stop()

    def test_runstop_right_wheel(self):
        "Check that runstop is working for the right wheel"
        self.stepper_runstop('hello-motor-right-wheel',xd=1.0,error_thresh=0.2)

    def test_runstop_left_wheel(self):
        "Check that runstop is working for the left wheel"
        self.stepper_runstop('hello-motor-left-wheel',xd=1.0,error_thresh=0.2)

    def test_runstop_arm(self):
        "Check that runstop is working for the arm"
        print()
        click.secho('Ensure arm is not at a hardstop. Hit enter when ready', fg="yellow")
        input()
        self.stepper_runstop('hello-motor-arm',xd=0.5,error_thresh=0.1)

    def test_runstop_lift(self):
        "Check that runstop is working for the lift"
        print()
        click.secho('Ensure lift is not at a hardstop. Hit enter when ready', fg="yellow")
        input()
        self.stepper_runstop('hello-motor-lift',xd=0.5,error_thresh=0.2)

test_suite = TestSuite(test=Test_STEPPER_runstop.test,failfast=False)
test_suite.addTest(Test_STEPPER_runstop('test_runstop_right_wheel'))
test_suite.addTest(Test_STEPPER_runstop('test_runstop_left_wheel'))
test_suite.addTest(Test_STEPPER_runstop('test_runstop_arm'))
test_suite.addTest(Test_STEPPER_runstop('test_runstop_lift'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
