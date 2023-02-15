#!/usr/bin/env python3
import unittest
import os
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_ROS_calibration(unittest.TestCase):
    """
    Test to check if calibrated urdf and head calibration file exist in workspace.
    """

    test = TestBase('test_ROS_calibration')

    @classmethod
    def setUpClass(self):
        # Write Test Class optional startup Scripts
        # E.g:
        # r = stretch_body.robot.Robot()
        # r.startup()
        pass

    @classmethod
    def tearDownClass(self):
        # Write Test Class optional ending Scripts
        # E.g:
        # r.stop()
        pass

    def test_head_calib_file(self):
        """
        Check if head calibration file exists in workspace
        """
        
        ros_distro = os.getenv('ROS_DISTRO')
        home_path = os.getenv('HOME')
        yaml_catkin_ws = 'catkin_ws/src/stretch_ros/stretch_core/config/controller_calibration_head.yaml'
        yaml_ament_ws = 'ament_ws/src/stretch_ros2/stretch_description/urdf/controller_calibration_head.yaml'

        head_calibration_path='./'
        if ros_distro in ['melodic', 'noetic']:
            head_calibration_path = '{0}/{1}'.format(home_path, yaml_catkin_ws)
        elif ros_distro in ['galactic', 'humble']:
            head_calibration_path = '{0}/{1}'.format(home_path, yaml_ament_ws)
        else:
            self.assertTrue(0,"No ROS distro sourced. Source ROS in the ~/.bashrc file.")
        
        head_calibration_exists = os.path.exists(head_calibration_path)

        if not head_calibration_exists:
            self.assertTrue(0,"Could not find head calibration file {}.".format(head_calibration_path))
        
        self.test.log_data('head_calibration_exists', head_calibration_exists)
        self.assertTrue(head_calibration_exists,'Head calibration file does not exist')

    def test_calib_urdf_file(self):
        """
        Check if calibrated urdf file exists in workspace
        """

        ros_distro = os.getenv('ROS_DISTRO')
        home_path = os.getenv('HOME')
        urdf_catkin_ws = 'catkin_ws/src/stretch_ros/stretch_description/urdf/stretch.urdf'
        urdf_ament_ws = 'ament_ws/src/stretch_ros2/stretch_description/urdf/stretch.urdf'

        calibrated_urdf_path='./'
        if ros_distro in ['melodic', 'noetic']:
            calibrated_urdf_path = '{0}/{1}'.format(home_path, urdf_catkin_ws)
        elif ros_distro in ['galactic', 'humble']:
            calibrated_urdf_path = '{0}/{1}'.format(home_path, urdf_ament_ws)
        else:
            self.assertTrue(0,"No ROS distro sourced. Source ROS in the ~/.bashrc file.")
        
        calibrated_urdf_exists = os.path.exists(calibrated_urdf_path)

        if not calibrated_urdf_exists:
            self.assertTrue(0,"Could not find calibrated URDF file {}.".format(calibrated_urdf_path))
        
        self.test.log_data('calibrated_urdf_exists', calibrated_urdf_exists)
        self.assertTrue(calibrated_urdf_exists, 'Calibrated URDF does not exist')

test_suite = TestSuite(test=Test_ROS_calibration.test, failfast=False)

test_suite.addTest(Test_ROS_calibration('test_head_calib_file'))
test_suite.addTest(Test_ROS_calibration('test_calib_urdf_file'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
