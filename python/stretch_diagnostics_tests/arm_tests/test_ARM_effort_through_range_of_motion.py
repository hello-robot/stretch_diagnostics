#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import Scope_Sensor_vs_Sensor
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_body.arm
import time
import click

class test_ARM_effort_through_range_of_motion(unittest.TestCase):
    """
    Check if arm can move through its range-of-motion using nominal currents
    """
    test = TestBase('test_ARM_effort_through_range_of_motion')

    def test_effort_through_range_of_motion(self):
        """
        Check if arm can move through its range-of-motion using nominal currents
        """
        data = {}
        a = stretch_body.arm.Arm()
        self.assertTrue(a.startup(),'Unable to startup arm')
        #Move through manually set mechanical limits without any safty protections on
        #Log what the worst case motor effort is required
        #Also don't require homing to be done as that may be broken
        a.motor.enable_safety()
        a.motor.disable_sync_mode()
        a.motor.disable_guarded_mode()
        a.push_command()

        #First collect physical hardstop postions
        click.secho('Manually move arm to fully retracted position', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        a.pull_status()
        data['x_retract_manual']=a.status['pos']
        xr=a.motor.status['pos']

        click.secho('Manually move arm to fully extended position', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        a.pull_status()
        data['x_extend_manual'] = a.status['pos']
        xe=a.motor.status['pos']

        a.motor.set_motion_limits(xr,xe)
        a.push_command()

        #Check if physical range of motion reasonable
        data['range_of_motion_m']=abs(data['x_extend_manual']-data['x_retract_manual'])
        lim0=a.params['calibration_range_bounds'][0]-.005
        lim1 = a.params['calibration_range_bounds'][1] + .005
        in_bounds = data['range_of_motion_m']>lim0 and data['range_of_motion_m']<lim1
        msg_in_bounds = 'Manual range of motion of %f compared to expected of %f to %f'%(data['range_of_motion_m'],lim0,lim1)
        print(msg_in_bounds)

        eff_min=0
        eff_max=0
        # Move in first direction and collect pos vs effort
        sls = Scope_Sensor_vs_Sensor(yrange=[-100.0, 100], title='Retract Effort (pct) vs Position (m) ')
        #Move to fully retracted (from motor API so don't require homing to be working)
        a.motor.set_command(mode=a.motor.MODE_POS_TRAJ,x_des=xr)
        a.push_command()
        ts=time.time()
        while time.time()-ts<6.0:
            a.pull_status()
            sls.step(a.status['pos']-a.motor_rad_to_translate_m(xr),a.motor.status['effort_pct'])
            eff_min=min(eff_min,a.motor.status['effort_pct'])
            eff_max=max(eff_max,a.motor.status['effort_pct'])
            #print('Pos %f | Effort %f'%(a.status['pos'],a.motor.status['effort_pct']))
            time.sleep(0.01)
        data['log_retract_pos']=sls.data_x
        data['log_retract_effort'] = sls.data_y
        image_fn = self.test.test_result_dir + '/arm_retraction_effort_vs_pos_%s.png' % self.test.timestamp
        sls.savefig(image_fn)

        # Move in second direction and collect pos vs effort
        sls2 = Scope_Sensor_vs_Sensor(yrange=[-100.0, 100], title='Extension Effort (pct) vs Position (m) ')
        # Move to fully extended (from motor API so don't require homing to be working)
        a.motor.set_command(mode=a.motor.MODE_POS_TRAJ, x_des=xe)
        a.push_command()
        ts = time.time()
        while time.time() - ts < 6.0:
            a.pull_status()
            sls2.step(a.status['pos']-a.motor_rad_to_translate_m(xr), a.motor.status['effort_pct'])
            eff_min=min(eff_min,a.motor.status['effort_pct'])
            eff_max=max(eff_max,a.motor.status['effort_pct'])
            #print('Pos %f | Effort %f' % (a.status['pos'], a.motor.status['effort_pct']))
            time.sleep(0.01)
        data['log_extend_pos'] = sls2.data_x
        data['log_extend_effort'] = sls2.data_y
        image_fn = self.test.test_result_dir + '/arm_extension_effort_vs_pos_%s.png' % self.test.timestamp
        sls2.savefig(image_fn)

        data['contact_thresh_max']=a.params['contact_models']['effort_pct']['contact_thresh_max']
        data['contact_thresh_homing'] = a.params['contact_models']['effort_pct']['contact_thresh_homing']
        data['min_effort_pct']=eff_min
        data['max_effort_pct'] = eff_max
        print('Min effort of: %f . Max effort of %f'%(eff_min,eff_max))
        print('Guarded contact efforts of %f to %f'%(a.params['contact_models']['effort_pct']['contact_thresh_max'][0],a.params['contact_models']['effort_pct']['contact_thresh_max'][1]))
        print('Homing guarded contact efforts of %f to %f' % (a.params['contact_models']['effort_pct']['contact_thresh_homing'][0],a.params['contact_models']['effort_pct']['contact_thresh_homing'][1]))
        click.secho('Data collection done.', fg="yellow")
        click.secho('Hit enter to finish', fg="yellow")
        input()

        self.test.log_data('test_effort_through_range_of_motion', data)

        a.stop()
        self.assertTrue(in_bounds, msg_in_bounds)


test_suite = TestSuite(test=test_ARM_effort_through_range_of_motion.test,failfast=False)
test_suite.addTest(test_ARM_effort_through_range_of_motion('test_effort_through_range_of_motion'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
