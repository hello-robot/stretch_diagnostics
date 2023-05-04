#!/usr/bin/env python3

import time
import click
import os
from stretch_body.pimu import Pimu
import numpy
import subprocess
import unittest
import apt
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner
import signal


class Test_POWER_battery_health(unittest.TestCase):
    """
    Test to check battery health
    """
    test = TestBase('test_POWER_battery_health')

    def confirm(self, statement, color):
        click.secho(statement, fg=color)
        x = input()
        if x == 'y':
            return True
        if x == 'n':
            return False

    def apt_check_if_installed(self, pkg):
        apt_list = apt.Cache()
        if apt_list[pkg].is_installed is False:
            if self.confirm("Would you like to install stress y or n", "yellow"):
                os.system("sudo apt-get install stress")
                apt_list = apt.Cache()
        self.assertTrue(apt_list[pkg].is_installed, msg='Stress package not installed')

    def test_stress_package(self):
        """
        Check if stress package is installed
        """
        apt_list = apt.Cache()
        self.apt_check_if_installed('stress')

    def test_battery_charged(self):
        """
        Check if batteries have been charged and settled
        """
        x1 = self.confirm("Have you fully charged the robot y or n", "yellow")
        self.assertTrue(x1, msg='Not fully charged')
        
    def test_charger_unplugged(self):
        """
        Check if charger is unplugged and battery voltage has settled
        """
        x1 = self.confirm("Is the charger unplugged and the battery voltage has settled for 10 minutes y or n", "yellow")
        self.assertTrue(x1, msg='Battery voltage not settled')

    def test_applications_closed(self):
        """
        Check if no other applications are running in the background
        """
        x1 = self.confirm("Have you closed all other applications y or n", "yellow")
        self.assertTrue(x1, msg='Other applications are still running')
    def start_stress(self):
        print('Starting stress')
        subprocess.Popen("stress -c 4", shell=True)
        time.sleep(5)

    def kill_stress(self):
        print('Killing stress')
        for line in os.popen("ps ax | grep stress | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid), signal.SIGKILL)

    def test_battery_health_test(self):
        """
        This tool gathers a baseline voltage reading and a voltage reading under a high load to estimate current state of battery health
        """
        global baseline_voltage, load_voltage, baseline_current
        baseline_reading = {'voltage': [], 'current': []}
        load_reading = {'voltage': [], 'current': []}
        sample = 10
        timeout_cnt = 0
        timeout = 65
        p = Pimu()
        p.startup()
        self.assertTrue(p.startup(), 'Failed to startup Pimu')

        print('Running Battery Health Tool, will take about 1 minute')
        try:
            while True:
                try:
                    p.pull_status()
                    msg = 'Voltage: %f  Current: %f' % (p.status['voltage'], p.status['current'])
                    # print(msg)

                    if timeout_cnt > 65:
                        timeoutmsg = ('TIMEOUT ERROR: Could not grab accurate voltage readings\n'
                                      'Please try running the script again')
                        self.kill_stress()
                        self.assertTrue(timeout < 65, timeoutmsg)
                        break

                    #Only collect votlage readings when current draw is below 1.6A
                    if p.status['current'] < 1.6 and len(baseline_reading) <= sample:
                        baseline_reading['voltage'].append(p.status['voltage'])
                        baseline_reading['current'].append(p.status['current'])
                        if p.status['voltage'] < 12.2:
                            print('Battery was not fully charged')
                            break
                        if len(baseline_reading['voltage']) == sample:
                            timeout = 0
                            print('Baseline reading done')
                            baseline_voltage = numpy.mean(baseline_reading['voltage'])
                            baseline_current = numpy.mean(baseline_reading['current'])
                            time.sleep(0.1)
                            self.start_stress()

                    # Only collect votlage readings when current draw is above 3.9A but less than 5A
                    if 3.9 < p.status['current'] < 5 and len(baseline_reading['voltage']) >= sample:
                        load_reading['voltage'].append(p.status['voltage'])
                        load_reading['current'].append(p.status['current'])

                        if len(load_reading["voltage"]) == sample:
                            load_voltage = numpy.mean(load_reading['voltage'])
                            load_current = numpy.mean(load_reading['current'])
                            self.kill_stress()

                            voltage_drop = float(round((baseline_voltage - load_voltage), 3))
                            esr = float(
                                round(((baseline_voltage - load_voltage) / (load_current - baseline_current)), 3))
                            battery_sts = ('Voltage Drop: %f ESR: %f' % (voltage_drop, esr))

                            self.test.log_data('baseline_voltage', float(baseline_voltage))
                            self.test.log_data('baseline_current', float(baseline_current))

                            self.test.log_data('load_voltage', float(load_voltage))
                            self.test.log_data('load_current', float(load_current))

                            self.test.log_data("voltage_drop", voltage_drop)
                            self.test.log_data("esr", esr)

                            print('\n########################################################')

                            if voltage_drop <= 0.5:
                                health = ("Batteries are in Great Health")
                            elif 0.5 < voltage_drop <= 0.75:
                                health = ('Batteries are in ok health..they are not as good as brand new\n'
                                          'but, they should meet expected run times.'
                                          'You can run a repair cycle to improve battery perfomance')
                            else:
                                health = ('Batteries are not in good health!!\n'
                                          'Recommended to run repair cycle on batteries')
                            if health is not None:
                                print(health)
                                self.test.log_data("battery_health", health)
                                print('########################################################')
                                self.assertTrue(voltage_drop <= 0.75, health)
                                break
                    timeout += 1
                    time.sleep(1)
                except (ValueError):
                    print('Bad input...')
        except (KeyboardInterrupt, SystemExit):
            p.stop()


test_suite = TestSuite(test=Test_POWER_battery_health.test, failfast=True)
test_suite.addTest(Test_POWER_battery_health('test_stress_package'))
test_suite.addTest(Test_POWER_battery_health('test_battery_charged'))
test_suite.addTest(Test_POWER_battery_health('test_charger_unplugged'))
test_suite.addTest(Test_POWER_battery_health('test_applications_closed'))
test_suite.addTest(Test_POWER_battery_health('test_battery_health_test'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
