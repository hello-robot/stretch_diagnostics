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
from stretch_diagnostics.test_helpers import Scope_Log_Sensor
class test_POWER_charger(unittest.TestCase):
    """
    Test if charger is working
    """
    test = TestBase('test_POWER_charger')

    def test_supply_mode_voltage(self):
        """
        Check if supply mode voltage is OK
        """
        data = {}
        p = stretch_body.pimu.Pimu()
        self.assertTrue(p.startup(),'Failed to startup Pimu')
        p.pull_status()

        click.secho('Plug charger into robot and place charger in SUPPLY mode', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        print('This will take 20s...')
        time.sleep(5.0)

        # Measure no load voltage
        image_fn = self.test.test_result_dir + '/battery_supply_mode_voltage_%s.png' % self.test.timestamp
        sls = Scope_Log_Sensor(duration=15.0, y_range=[9, 14.0], title='Charger supply mode, no load voltage (V)', num_points=100,
                               image_fn=image_fn, start_fn=None, start_fn_ts=None, end_fn=None, end_fn_ts=None)
        while sls.step(p.status['voltage']):
            p.pull_status()

        data['voltage_supply_load'] = sls.avg
        data['voltage_supply_load_data']=sls.data

        supply_mode_voltage_min=13.0

        low_voltage = sls.avg < supply_mode_voltage_min
        msg = 'Average supply mode voltage of %f below expected of %f. May be broken charger or cable.' % (
        sls.avg, supply_mode_voltage_min)
        self.assertFalse(low_voltage, msg=msg)

        self.test.log_data('test_supply_mode_voltage', data)

test_suite = TestSuite(test=test_POWER_charger.test,failfast=False)
test_suite.addTest(test_POWER_charger('test_supply_mode_voltage'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
