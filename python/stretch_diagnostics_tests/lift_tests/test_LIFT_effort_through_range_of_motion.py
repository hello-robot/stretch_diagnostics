#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import Scope_Sensor_vs_Sensor
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.lift
import stretch_body.hello_utils as hu
import time
import click

class test_LIFT_effort_through_range_of_motion(unittest.TestCase):
    """
    Check if lift can move through its range-of-motion using nominal currents
    """
    test = TestBase('test_LIFT_effort_through_range_of_motion')

    def test_effort_through_range_of_motion(self):
        """
        Check if arm can move through its range-of-motion using nominal currents
        """
        data = {}
        l = stretch_body.lift.Lift()
        self.assertTrue(l.startup(),'Unable to startup lift')
        #Move through manually set mechanical limits without any safty protections on
        #Log what the worst case motor effort is required
        #Also don't require homing to be done as that may be broken

        l.motor.enable_safety()
        l.motor.disable_sync_mode()
        l.motor.disable_guarded_mode()
        l.push_command()

        #First collect physical hardstop postions
        click.secho('Manually move lift to fully lowered position', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        l.pull_status()
        data['x_lower_manual']=l.status['pos']
        xr=l.motor.status['pos']

        click.secho('Manually move lift to fully raised position', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        l.pull_status()
        data['x_raise_manual'] = l.status['pos']
        xe=l.motor.status['pos']

        l.motor.set_motion_limits(xr,xe)
        l.push_command()

        #Check if physical range of motion reasonable
        data['range_of_motion_m']=abs(data['x_raise_manual']-data['x_lower_manual'])
        lim0=l.params['calibration_range_bounds'][0]-.005
        lim1 = l.params['calibration_range_bounds'][1] + .005
        in_bounds = data['range_of_motion_m']>lim0 and data['range_of_motion_m']<lim1
        msg_in_bounds = 'Manual range of motion of %f compared to expected of %f to %f'%(data['range_of_motion_m'],lim0,lim1)
        print(msg_in_bounds)

        eff_min=0
        eff_max=0
        # Move in first direction and collect pos vs effort
        sls = Scope_Sensor_vs_Sensor(yrange=[-100.0, 100], title='Lower LIft Effort (pct) vs Position (m) ')
        #Move to fully lowered (from motor API so don't require homing to be working)
        l.motor.set_command(mode=l.motor.MODE_POS_TRAJ,x_des=xr)
        l.push_command()
        ts=time.time()
        while time.time()-ts<12.0:
            l.pull_status()
            sls.step(l.status['pos']-l.motor_rad_to_translate_m(xr),l.motor.status['effort_pct'])
            eff_min=min(eff_min,l.motor.status['effort_pct'])
            eff_max=max(eff_max,l.motor.status['effort_pct'])
            #print('Pos %f | Effort %f'%(l.status['pos'],l.motor.status['effort_pct']))
            time.sleep(0.01)
        data['log_lower_pos']=sls.data_x
        data['log_lower_effort'] = sls.data_y
        image_fn = self.test.test_result_dir + '/lift_lower_effort_vs_pos_%s.png' % self.test.timestamp
        sls.savefig(image_fn)

        # Move in second direction and collect pos vs effort
        sls2 = Scope_Sensor_vs_Sensor(yrange=[-100.0, 100], title='Raise Lift Effort (pct) vs Position (m) ')
        # Move to fully raiseed (from motor API so don't require homing to be working)
        l.motor.set_command(mode=l.motor.MODE_POS_TRAJ, x_des=xe)
        l.push_command()
        ts = time.time()
        while time.time() - ts < 12.0:
            l.pull_status()
            sls2.step(l.status['pos']-l.motor_rad_to_translate_m(xr), l.motor.status['effort_pct'])
            eff_min=min(eff_min,l.motor.status['effort_pct'])
            eff_max=max(eff_max,l.motor.status['effort_pct'])
            #print('Pos %f | Effort %f' % (l.status['pos'], l.motor.status['effort_pct']))
            time.sleep(0.01)
        data['log_raise_pos'] = sls2.data_x
        data['log_raise_effort'] = sls2.data_y
        image_fn = self.test.test_result_dir + '/lift_raise_effort_vs_pos_%s.png' % self.test.timestamp
        sls2.savefig(image_fn)

        data['min_effort_pct']=eff_min
        data['max_effort_pct'] = eff_max
        print('Min effort of: %f . Max effort of %f'%(eff_min,eff_max))
        data['contact_thresh_max']=l.params['contact_models']['effort_pct']['contact_thresh_max']
        data['contact_thresh_homing'] = l.params['contact_models']['effort_pct']['contact_thresh_homing']
        print('Guarded contact efforts of %f to %f'%(l.params['contact_models']['effort_pct']['contact_thresh_max'][0],l.params['contact_models']['effort_pct']['contact_thresh_max'][1]))
        print('Homing guarded contact efforts of %f to %f' % (l.params['contact_models']['effort_pct']['contact_thresh_homing'][0],l.params['contact_models']['effort_pct']['contact_thresh_homing'][1]))
        click.secho('Data collection done.', fg="yellow")
        click.secho('Hit enter to finish', fg="yellow")
        input()

        self.test.log_data('test_effort_through_range_of_motion', data)

        l.stop()
        self.assertTrue(in_bounds, msg_in_bounds)




test_suite = TestSuite(test=test_LIFT_effort_through_range_of_motion.test,failfast=False)
test_suite.addTest(test_LIFT_effort_through_range_of_motion('test_effort_through_range_of_motion'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
