#!/usr/bin/env python3
import unittest
import subprocess
import os
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_ROS_sourced_distro(unittest.TestCase):
    """
    Test to check if correct ROS distro and workspace are sourced in the .bashrc file.
    """

    # test object is always expected within a TestCase Class
    test = TestBase('test_ROS_sourced_distro')

    def test_ros_install(self):
        """
        Check whether ROS is installed
        """
        
        try:
            distro = subprocess.check_output(["ls", "/opt/ros"])
            distro = str(distro, 'UTF-8')
            distros = distro.split()
        except subprocess.CalledProcessError:
            distros = None
            self.test.add_hint('No ROS installation detected. Install ROS.')

        self.test.log_data('ros_installed', distros)
        self.assertIsNotNone(distros)

    def test_distro_sourced(self):
        """
        Check whether a ROS distro is sourced
        """

        distro = os.getenv('ROS_DISTRO')
        self.test.log_data('ros_sourced', distro)

        if distro == None:
            self.test.add_hint('No ROS distro sourced. Source ROS in the ~/.bashrc file')

        self.assertIsNotNone(distro)
        
    def test_workspace_sourced(self):
        """
        Check whether correct workspace is sourced in .bashrc file
        """

        sourced = False
        distro = os.getenv('ROS_DISTRO')

        home_path = os.getenv('HOME')
        bashrc_path = '{}/.bashrc'.format(home_path)
        ament_ws_path = '{}/ament_ws/install/setup.bash'.format(home_path)
        catkin_ws_path = '{}/catkin_ws/devel/setup.bash'.format(home_path)

        with open(bashrc_path, 'r') as file:
            line_list = []
            for line in file:
                if 'source' in line:
                    if '#' not in line:
                        line_list.append(line.split())

        if not line_list:
            self.test.add_hint('There is no ROS workspace sourced. Source workspace in .bashrc file')
        else:
            if distro == 'melodic' or 'noetic':
                for line in line_list:
                    if catkin_ws_path in line:
                        sourced = True
            elif distro == 'galactic':
                for line in line_list:
                    if ament_ws_path in line:
                        sourced = True

        for line in line_list:
            if ament_ws_path or catkin_ws_path in line:
                self.test.log_data

        if sourced == False:
            self.test.add_hint('Check .bashrc file to ensure correct ROS workspace has been sourced')

        self.assertTrue(sourced)


# failsafe set to True - if a test fails, subsequent tests will be assumed to fail and won't be run
test_suite = TestSuite(test=Test_ROS_sourced_distro.test, failfast=True)

# Add tests from the Test Class to the test_suite in the same order it would be run.
test_suite.addTest(Test_ROS_sourced_distro('test_ros_install'))
test_suite.addTest(Test_ROS_sourced_distro('test_distro_sourced'))
test_suite.addTest(Test_ROS_sourced_distro('test_workspace_sourced'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
