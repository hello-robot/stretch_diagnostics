#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.pimu
import stretch_body.hello_utils as hu
import time
import click
import stretch_body.scope as scope
import os
import signal
import subprocess
from stretch_diagnostics.test_helpers import Scope_Log_Sensor
class test_POWER_battery_loading(unittest.TestCase):
    """
    Test if charger is working
    """
    test = TestBase('test_POWER_battery_loading')

    def start_stress(self):
        print('Starting stress')
        subprocess.Popen("stress -c 4", shell=True)

    def kill_stress(self):
        print('Killing stress')
        for line in os.popen("ps ax | grep stress | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid), signal.SIGKILL)


    def test_battery_loading(self):
        """
        Check if supply mode voltage is OK
        """
        data={}
        p=stretch_body.pimu.Pimu()
        self.assertTrue(p.startup(),'Failed to startup Pimu')
        p.pull_status()

        print()
        click.secho('Unplug charger from robot.', fg="yellow")
        click.secho('This test will take ~60s.', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()

        #Measure no load voltage
        image_fn = self.test.test_result_dir + '/battery_no_load_voltage_%s.png' % self.test.timestamp
        sls=Scope_Log_Sensor(duration=10.0,y_range=[9,14.0],title='No charger, no load voltage (V)',num_points=100, image_fn=image_fn, start_fn=None, start_fn_ts=None,end_fn=None, end_fn_ts=None)
        while sls.step(p.status['voltage']):
            p.pull_status()
        data['voltage_no_load'] = sls.avg
        data['voltage_no_load_data']=sls.data

        v_min=10.5

        low_voltage=sls.avg<v_min
        msg='Average no load voltage of %f below expected of %f. Batteries may be dischaged or damaged.'%(sls.avg,v_min)
        self.assertFalse(low_voltage,msg=msg)

        #Measure loaded voltage
        image_fn = self.test.test_result_dir + '/battery_stress_load_voltage_%s.png' % self.test.timestamp
        sls = Scope_Log_Sensor(duration=60.0, y_range=[9, 14.0], title='No charger, stress load voltage (V)', num_points=300,
                               image_fn=image_fn, start_fn=self.start_stress, start_fn_ts=2.0,end_fn=self.kill_stress,end_fn_ts=55.0)
        while sls.step(p.status['voltage']):
            p.pull_status()
        data['voltage_stress_load'] = sls.avg
        data['voltage_stress_load_data']=sls.data

        low_voltage = sls.avg < v_min
        msg = 'Average loaded voltage of %f below expected of %f. Batteries may be dischaged or damaged.' % (sls.avg, v_min)
        self.assertFalse(low_voltage, msg=msg)

        self.test.log_data('test_battery_loading', data)

        p.stop()


test_suite = TestSuite(test=test_POWER_battery_loading.test,failfast=False)
test_suite.addTest(test_POWER_battery_loading('test_battery_loading'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
