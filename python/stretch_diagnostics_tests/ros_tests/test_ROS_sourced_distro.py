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

    test = TestBase('test_ROS_sourced_distro')

    def test_ros_install(self):
        """
        Check whether ROS is installed
        """
        
        try:
            distro = subprocess.check_output(["ls", "/opt/ros"])
            distro = str(distro, 'UTF-8')
            distros = distro.split()
            if not distros: # if /opt/ros directory exists but is empty
                self.test.add_hint('No ROS installation detected. Install ROS.')
        except subprocess.CalledProcessError: # if /opt/ros directory does not exist
            distros = []
            self.assertTrue(0,'No ROS installation detected. Install ROS.')

        self.test.log_data('ros_distro_installed', distros)
        self.assertTrue(distros,'No ROS distro installed')

    def test_distro_sourced(self):
        """
        Check whether a ROS distro is sourced
        """

        distro = os.getenv('ROS_DISTRO')

        self.assertTrue(distro,'No ROS distro sourced. Source ROS in the ~/.bashrc file.')

        self.test.log_data('ros_distro_sourced', distro)
        self.assertTrue(distro, 'No ROS distro sourced')
        
    def test_workspace_sourced(self):
        """
        Check whether correct workspace is sourced in .bashrc file
        """

        sourced = False
        ros_ws_sourced = None
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
                        line_list.append(line)

        if not line_list:
            self.assertTrue(0,'There is no ros workspace sourced. Source {} workspace in .bashrc file.'.format(distro))
        else:
            for line in line_list:
                if distro in ['melodic', 'noetic'] and catkin_ws_path in line:
                    sourced = True
                    ros_ws_sourced = catkin_ws_path
                elif distro in ['galactic', 'humble'] and ament_ws_path in line:
                    sourced = True
                    ros_ws_sourced = ament_ws_path
                elif distro in ['galactic', 'humble'] and catkin_ws_path in line: # Conflicting workspace
                    sourced = False
                    ros_ws_sourced = catkin_ws_path
                    break
                elif distro in ['melodic', 'noetic'] and ament_ws_path in line: # Conflicting workspace
                    sourced = False
                    ros_ws_sourced = ament_ws_path
                    break

        self.assertTrue(sourced,'Either no or conflicting ros workspace sourced. Source correct ros workspace in .bashrc file.')
        self.test.log_data('ros_ws_sourced', ros_ws_sourced)



# failsafe set to True - if a test fails, subsequent tests will be assumed to fail and won't be run
test_suite = TestSuite(test=Test_ROS_sourced_distro.test, failfast=True)

# Add tests from the Test Class to the test_suite in the same order it would be run.
test_suite.addTest(Test_ROS_sourced_distro('test_ros_install'))
test_suite.addTest(Test_ROS_sourced_distro('test_distro_sourced'))
test_suite.addTest(Test_ROS_sourced_distro('test_workspace_sourced'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
