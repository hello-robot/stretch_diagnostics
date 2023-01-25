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

class test_POWER_battery_loading(unittest.TestCase):
    """
    Test if charger is working
    """
    test = TestBase('test_POWER_battery_loading')


    def scope_current(self,pimu,duration=3.0,title='Current',image_fn=None,start_fn=None, start_fn_ts=None,end_fn=None,end_fn_ts=None,num_points=100):
        ts=time.time()
        i=[]
        s = scope.Scope(num_points=num_points,yrange=[0, 6.0], title=title)
        dt=time.time()-ts
        while dt<duration:
            if start_fn_ts is not None and dt>start_fn_ts and start_fn is not None:
                start_fn()
                start_fn=None
            if end_fn_ts is not None and dt>end_fn_ts and end_fn is not None:
                end_fn()
                end_fn=None
            pimu.pull_status()
            i.append(pimu.status['current'])
            s.step_display(pimu.status['current'])
            time.sleep(0.1)
            dt=time.time() - ts
        if image_fn is not None:
            s.savefig(image_fn)
        return i,sum(i)/len(i)

    def scope_voltage(self,pimu,duration=3.0,title='Voltage',image_fn=None,start_fn=None, start_fn_ts=None,end_fn=None,end_fn_ts=None,num_points=100):
        ts=time.time()
        v=[]
        s = scope.Scope(num_points=num_points,yrange=[9, 14], title=title)
        dt=time.time()-ts
        while dt<duration:
            if start_fn_ts is not None and dt>start_fn_ts and start_fn is not None:
                start_fn()
                start_fn=None
            if end_fn_ts is not None and dt>end_fn_ts and end_fn is not None:
                end_fn()
                end_fn=None
            pimu.pull_status()
            v.append(pimu.status['voltage'])
            s.step_display(pimu.status['voltage'])
            time.sleep(0.1)
            dt=time.time() - ts
        if image_fn is not None:
            s.savefig(image_fn)
        return v,sum(v)/len(v)

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
        self.assertTrue(p.startup())

        print()
        click.secho('Unplug charger from robot.', fg="yellow")
        click.secho('This test will take ~60s.', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        image_fn = self.test.test_result_dir + '/battery_no_load_voltage_%s.png' % self.test.timestamp
        log,avg=self.scope_voltage(p,10.0,title='No load voltage (V)',image_fn=image_fn)
        data['voltage_no_load'] = avg
        self.test.log_data('test_battery_loading', data)

        image_fn = self.test.test_result_dir + '/battery_stress_load_voltage_%s.png' % self.test.timestamp
        log, avg = self.scope_current(p, 60.0, title='Stress load voltage (V)', image_fn=image_fn,
                                      start_fn=self.start_stress, start_fn_ts=2.0,end_fn=self.kill_stress,end_fn_ts=55.0,num_points=300)
        data['voltage_stress_load'] = avg
        self.test.log_data('test_battery_loading', data)

        p.stop()


test_suite = TestSuite(test=test_POWER_battery_loading.test,failfast=False)
test_suite.addTest(test_POWER_battery_loading('test_battery_loading'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
