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

class test_POWER_charger(unittest.TestCase):
    """
    Test if charger is working
    """
    test = TestBase('test_POWER_charger')


    def get_average_voltage(self,pimu,duration=3.0):
        ts=time.time()
        v=[]
        while time.time()-ts<duration:
            pimu.pull_status()
            v.append(pimu.status['voltage'])
            time.sleep(0.1)
        return v,sum(v)/len(v)


    def test_supply_mode_voltage(self):
        """
        Check if supply mode voltage is OK
        """
        data={}
        p=stretch_body.pimu.Pimu()
        self.assertTrue(p.startup())

        print()
        click.secho('Unplug charger from robot.', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        print('This will take 10s...')
        time.sleep(5.0)
        log,avg=self.get_average_voltage(p)
        data['voltage_no_charger']=avg
        data['log_voltage_no_charger']=log
        print('No charger voltage of: %f'%data['voltage_no_charger'])
        print()

        click.secho('Plug charger into robot and place charger in SUPPLY mode', fg="yellow")
        click.secho('Hit enter when ready', fg="yellow")
        input()
        print('This will take 5-15s...')
        time.sleep(5.0)
        supply_mode_voltage_min=13.0
        for i in range(10):
            log, avg = self.get_average_voltage(p,1.0)
            data['voltage_supply_mode']=avg
            data['log_voltage_supply_mode'] = log
            print('Tested supply mode voltage of: %f'%data['voltage_supply_mode'])
            if data['voltage_supply_mode']>supply_mode_voltage_min:
                break
        if not data['voltage_supply_mode']>supply_mode_voltage_min:
            self.test.add_hint('Charger SUPPLY mode has low voltage. May be broken charger or cable.')
        self.assertTrue(data['voltage_supply_mode']>supply_mode_voltage_min)
        p.stop()
        self.test.log_data('test_supply_mode_voltage', data)

test_suite = TestSuite(test=test_POWER_charger.test,failfast=False)
test_suite.addTest(test_POWER_charger('test_supply_mode_voltage'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
