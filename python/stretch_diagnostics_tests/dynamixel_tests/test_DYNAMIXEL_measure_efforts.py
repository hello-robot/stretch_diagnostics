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

class Test_DYNAMIXEL_measure_efforts(unittest.TestCase):
    """
    Test Dynamixel efforts to check for mechanical issues
    """
    test = TestBase('test_DYNAMIXEL_measure_efforts')
    effort_limits = {'head_pan':[-5.0,5.0],'head_tilt':[-10.0,20.0],'stretch_gripper':[-45,5],'wrist_yaw':[-10.0,10.0]}

    def measure_effort(self,servo,joint,duration,y_range,lim_lower=None,lim_upper=None):
        self.assertTrue(servo.startup(),msg='Not able to connect to servo %s'%joint)
        self.assertTrue(servo.do_ping(), msg='Not able to ping servo %s' % joint)
        servo.pull_status()
        if servo.params['req_calibration'] and not servo.is_calibrated:
            servo.home()
        self.assertFalse(servo.params['req_calibration'] and not servo.is_calibrated, msg='Joint %srequires calibration. Home joint and try again.' % joint)

        if lim_lower is None:
            lim_lower = min(servo.ticks_to_world_rad(servo.params['range_t'][0]),
                            servo.ticks_to_world_rad(servo.params['range_t'][1]))
        if lim_upper is None:
            lim_upper = max(servo.ticks_to_world_rad(servo.params['range_t'][0]),
                        servo.ticks_to_world_rad(servo.params['range_t'][1]))

        print('Joint limits of: %f to %f'%(lim_lower,lim_upper))
        servo.move_to(lim_lower)
        servo.wait_until_at_setpoint(timeout=6.0)

        #Go pos direction
        servo.pull_status()
        image_fn = self.test.test_result_dir + '/'+'%s_effort_to_upper_limit%s.png' % (joint,self.test.timestamp)
        s=Scope_Log_Sensor(duration=duration, y_range=y_range, title='%s effort to upper limit'%joint, num_points=100, image_fn=image_fn,delay=.01)
        servo.move_to(lim_upper,servo.params['motion']['slow']['vel'],servo.params['motion']['slow']['accel'])
        log={'pos':[],'effort':[]}
        min_eff=0
        max_eff=0
        while s.step(servo.status['effort']):
            log['pos'].append(servo.status['pos'])
            log['effort'].append(servo.status['effort'])
            max_eff=max(log['effort'][-1],max_eff)
            min_eff = min(log['effort'][-1], min_eff)
            #print('Joint: %s. Pos %f. Effort (pct): %f'%(joint,log['pos'][-1],log['effort'][-1]))
            servo.pull_status()


        #Go neg direction
        servo.pull_status()
        image_fn = self.test.test_result_dir + '/'+'%s_effort_to_lower_limit%s.png' % (joint,self.test.timestamp)
        s=Scope_Log_Sensor(duration=duration, y_range=[-50, 50.0], title='%s effort to lower limit'%joint, num_points=100, image_fn=image_fn,delay=.01)
        servo.move_to(lim_lower,servo.params['motion']['slow']['vel'],servo.params['motion']['slow']['accel'])
        log={'pos':[],'effort':[]}
        min_eff=0
        max_eff=0
        while s.step(servo.status['effort']):
            log['pos'].append(servo.status['pos'])
            log['effort'].append(servo.status['effort'])
            max_eff=max(log['effort'][-1],max_eff)
            min_eff = min(log['effort'][-1], min_eff)
            #print('Joint: %s. Pos %f. Effort (pct): %f'%(joint,log['pos'][-1],log['effort'][-1]))
            servo.pull_status()

        eb = (min_eff > self.effort_limits[joint][0]) and (max_eff < self.effort_limits[joint][1])
        msg='Effort of %f|%f for %s required exceeds limits of %f|%f. Check for mechanical obstruction'%(min_eff,max_eff,joint,self.effort_limits[joint][0],self.effort_limits[joint][1])
        self.assertTrue(eb,msg=msg)
        return log

    def test_measure_effort_head_pan(self):
        """
        Measure efforts to move head_pan through joint range
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_pan', chain=None)
        data=self.measure_effort(servo,'head_pan',duration=8.0,y_range=[-50, 50.0])
        self.test.log_data('head_pan_effort_to_limits', data)
        servo.stop()

    def test_measure_effort_head_tilt(self):
        """
        Measure efforts to move head_tilt through joint range
        """
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='head_tilt', chain=None)
        data=self.measure_effort(servo,'head_tilt',duration=5.0,y_range=[-50, 50.0])
        self.test.log_data('head_tilt_effort_to_limits', data)
        servo.stop()

    def test_measure_effort_stretch_gripper(self):
        """
        Measure efforts to move stretch_gripper through joint range
        """
        servo = stretch_body.stretch_gripper.StretchGripper()
        data=self.measure_effort(servo,'stretch_gripper',duration=10.0,y_range=[-50, 50.0],lim_lower=servo.poses['open'],lim_upper=servo.poses['close'])
        self.test.log_data('stretch_gripper_effort_to_limits', data)
        servo.stop()

    def test_measure_effort_wrist_yaw(self):
        """
        Measure efforts to move wrist_yaw through joint range
        """
        print()
        click.secho('Ensure wrist yaw is free to move through its range of motion. Hit enter when ready', fg="yellow")
        input()
        servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name='wrist_yaw', chain=None)
        data = self.measure_effort(servo, 'wrist_yaw', duration=7.0, y_range=[-50, 50.0])
        self.test.log_data('wrist_yaw_effort_to_limits', data)
        servo.stop()

test_suite = TestSuite(test=Test_DYNAMIXEL_measure_efforts.test,failfast=False)
test_suite.addTest(Test_DYNAMIXEL_measure_efforts('test_measure_effort_head_pan'))
test_suite.addTest(Test_DYNAMIXEL_measure_efforts('test_measure_effort_head_tilt'))
test_suite.addTest(Test_DYNAMIXEL_measure_efforts('test_measure_effort_stretch_gripper'))
test_suite.addTest(Test_DYNAMIXEL_measure_efforts('test_measure_effort_wrist_yaw'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
