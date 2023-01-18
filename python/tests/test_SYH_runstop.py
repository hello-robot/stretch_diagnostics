#!/usr/bin/env python3
import unittest
from stretch_production_tools.bringup_test_utils import Bringup_Test
from stretch_production_tools.bringup_test_utils import BRI_TestRunner, BRI_TestSuite
from stretch_production_tools.helpers import *
import stretch_body.robot as robot


class Test_BRI_runstop_test(unittest.TestCase):
    """
    Series of tests to check the Run Stop Capability
    """

    bringup_test = Bringup_Test('test_BRI_runstop_test')

    @classmethod
    def setUpClass(self):
        self.robot = robot.Robot()
        self.robot.startup()

    @classmethod
    def tearDownClass(self):
        self.robot.stop()

    def test_check_robot_homed(self):
        """
        Check if the Robot is Homed before running this test
        """
        self.robot.pull_status()
        self.assertTrue(self.robot.is_calibrated(), msg='Run stretch_robot_home.py before running this')

    def test_small_motions(self):
        """
        Manually verify if the robot makes small motions successfully when runstop is not triggered.
        """
        self.robot.pimu.runstop_event_reset()
        self.robot.push_command()
        print('-------------------------------')
        self.assertTrue(confirm('Is the runstop light solid?'))

        print('About to make small motion. Ensure robot is free to move \n')

        print('Sending command to arm. Press enter when ready')
        input()
        print('-------------------------------')
        self.robot.arm.move_by(x_m=0.01)
        self.robot.push_command()
        self.assertTrue(confirm('Did the arm move?'))

        print('Sending command to lift. Press enter when ready')
        input()
        print('-------------------------------')
        self.robot.lift.move_by(x_m=0.01)
        self.robot.push_command()
        self.assertTrue(confirm('Did the lift move?'))

        print('Sending command to base. Press enter when ready')
        input()
        print('-------------------------------')
        self.robot.base.translate_by(x_m=0.01)
        self.robot.push_command()
        self.assertTrue(confirm('Did the base move straight ahead?'))

    def test_runstop_button(self):
        """
        Manually verify if the external runstop button works and registers triggers
        """
        print('-------------------------------')
        self.robot.pimu.runstop_event_trigger()
        self.robot.push_command()
        self.assertTrue(confirm('Is the runstop button light flashing?'))
        self.robot.pull_status()
        self.assertTrue(self.robot.status['pimu']['runstop_event'], msg='Runstop Event not registered in pimu status.')

        print('-------------------------------')
        print('Hold the runstop button for 2s until it beeps')
        self.assertTrue(confirm('Is the runstop button solid?'))
        self.robot.pull_status()
        self.assertFalse(self.robot.status['pimu']['runstop_event'], msg='Runstop Event not registered in pimu status.')

        print('-------------------------------')
        print('Hit the runstop')
        self.assertTrue(confirm('Is the runstop button flashing?'))
        if 're2' in self.bringup_test.fleet_id:
            self.assertTrue(confirm('Is the lightbar flashing?'))
        self.robot.pull_status()
        self.assertTrue(self.robot.status['pimu']['runstop_event'], msg='Runstop Event not registered in pimu status.')

    def test_small_motions_with_runstop(self):
        """
        Manually verify if the robot makes small motions successfully when runstop is triggered.
        """
        self.robot.pull_status()
        self.assertTrue(self.robot.status['pimu']['runstop_event'], msg='Runstop Event not registered in pimu status.')

        print('-------------------------------')
        print('About to attempt small motion.\n')
        print('Sending command to arm. Press enter when ready')
        input()

        self.robot.arm.move_by(x_m=-0.01)
        self.robot.push_command()
        self.assertFalse(confirm('Did the arm move?'))

        print('Sending command to lift. Press enter when ready')
        input()
        self.robot.lift.move_by(x_m=-0.01)
        self.robot.push_command()
        self.assertFalse(confirm('Did the lift move?'))

        print('Sending command to base. Press enter when ready')
        input()
        self.robot.base.translate_by(x_m=-0.01)
        self.robot.push_command()
        self.assertFalse(confirm('Did the base move straight back?'))

        self.robot.pimu.runstop_event_reset()
        self.robot.push_command()


test_suite = BRI_TestSuite(bringup_test=Test_BRI_runstop_test.bringup_test, failfast=True)
test_suite.addTest(Test_BRI_runstop_test('test_check_robot_homed'))
test_suite.addTest(Test_BRI_runstop_test('test_small_motions'))
test_suite.addTest(Test_BRI_runstop_test('test_runstop_button'))
test_suite.addTest(Test_BRI_runstop_test('test_small_motions_with_runstop'))

if __name__ == '__main__':
    runner = BRI_TestRunner(suite=test_suite)
    runner.run()
