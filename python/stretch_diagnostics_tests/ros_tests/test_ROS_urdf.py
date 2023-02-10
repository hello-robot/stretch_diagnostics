#!/usr/bin/env python3
import unittest
import os
import shutil
import xacro
import xml.etree.ElementTree as ET
from stretch_body import robot as rb
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_ROS_urdf(unittest.TestCase):
    """
    Test to check if URDF file conforms with attached end-of-arm tool
    """

    test = TestBase('test_ROS_urdf')

    def get_param_distro_path(self):
        r = rb.Robot()
        r.startup()
        tool = r.params['tool']
        r.stop()

        ros_distro = ['melodic', 'noetic']
        ros2_distro = ['galactic', 'humble']

        distro = os.getenv('ROS_DISTRO')
        home_path = os.getenv('HOME')
        catkin_urdf_path = 'catkin_ws/src/stretch_ros/stretch_description/urdf'
        ament_urdf_path = 'ament_ws/src/stretch_ros2/stretch_description/urdf'

        if distro in ros_distro:
            urdf_path = '{0}/{1}'.format(home_path, catkin_urdf_path)
        elif distro in ros2_distro:
            urdf_path = '{0}/{1}'.format(home_path, ament_urdf_path)
        else:
            self.test.add_hint('Source ROS distro before running test.')

        return tool, distro, urdf_path

    def test_gripper_type(self):
        """
        Test the kind of gripper attached
        """
        
        tool, distro, urdf_path = self.get_param_distro_path()
        tool_type = ['tool_stretch_gripper', 'tool_stretch_dex_wrist', 'tool_dry_erase_holder_v1', 'tool_reactor_wrist', 'tool_usbcam_wrist']
        
        tool_valid = tool in tool_type
        
        if not tool_valid:
            self.test.add_hint('Unidentified gripper type. Add a valid gripper tool to stretch_configuration_params.yaml')

        self.test.log_data('tool_type', tool)
        self.assertTrue(tool_valid)

    def test_endofarm_xacro(self):
        """
        Test if XACRO file corresponds to the end-of-arm tool in params YAML
        """
        
        xacro_tool_sourced = None

        tool, distro, urdf_path = self.get_param_distro_path()
        xacro_path = '{}/stretch_description.xacro'.format(urdf_path)

        xacro_exists = os.path.exists(xacro_path)
        self.assertTrue(xacro_exists)
        if not xacro_exists:
            self.test.add_hint('{} does not exist.'.format(xacro_path))
            return
        
        shutil.copy(xacro_path, '{}/stretch_description.xacro'.format(self.test.results_directory))

        doc = xacro.parse(open(xacro_path))
        robot_description_config = doc.toxml()
        root = ET.fromstring(robot_description_config)

        attrib_list = []
        for child in root:
            try:
                attrib_list.append(child.attrib['filename'])
            except KeyError:
                continue

        tool_dict = {'tool_stretch_gripper': ['stretch_gripper.xacro', 'stretch_gripper_with_puller.xacro'],
                     'tool_stretch_dex_wrist': ['stretch_dex_wrist.xacro'],
                     'tool_dry_erase_holder_v1': ['stretch_dry_erase_marker.xacro'],
                     'tool_reactor_wrist': [],
                     'tool_usbcam_wrist': ['stretch_wrist_USB_board_camera.xacro'],
                     }

        tool_xacro = tool_dict[tool]

        for x in tool_xacro:
            if x in attrib_list:
                xacro_tool_sourced = x

        if not xacro_tool_sourced:
            self.test.add_hint('Add the correct end of arm tool to {}'.format(xacro_path))

        self.test.log_data('xacro_tool_sourced', xacro_tool_sourced)
        self.assertTrue(xacro_tool_sourced)

    def test_endofarm_urdf(self):
        """
        Test if URDF file corresponds to the end-of-arm tool in params YAML
        """

        urdf_configured = False

        tool, distro, urdf_path = self.get_param_distro_path()
        calibrated_urdf_path = '{}/stretch.urdf'.format(urdf_path)

        calibrated_urdf_exists = os.path.exists(calibrated_urdf_path)
        self.assertTrue(calibrated_urdf_exists)
        if not calibrated_urdf_exists:
            self.test.add_hint('{} does not exist.'.format(calibrated_urdf_path))
            return

        shutil.copy(calibrated_urdf_path, '{}/stretch.urdf'.format(self.test.results_directory))

        link_list = [] # Stores list of links in URDF
        tree = ET.parse(calibrated_urdf_path)
        root = tree.getroot()
        for child in root:
            if child.tag == 'link':
                link_list.append(child.attrib['name'])

        # Dictionary of identifying links for tools that confirm the URDF is configured correctly
        id_link = {'tool_stretch_gripper': 'link_gripper',
                   'tool_stretch_dex_wrist': 'link_wrist_pitch',
                   'tool_dry_erase_holder_v1': 'link_dry_erase_holder',
                   'tool_reactor_wrist': '',
                   'tool_usbcam_wrist': 'link_wrist_USB_board_camera',
                   }

        tool_link = id_link[tool]

        if tool_link in link_list:
            urdf_configured = True
        else:
            self.test.add_hint('URDF file stretch.urdf is not configured correctly. Generate URDF using appropriate XACRO file for tool.')
        
        self.test.log_data('urdf_configured', urdf_configured)
        self.assertTrue(urdf_configured)
        

test_suite = TestSuite(test=Test_ROS_urdf.test, failfast=True)

test_suite.addTest(Test_ROS_urdf('test_gripper_type'))
test_suite.addTest(Test_ROS_urdf('test_endofarm_xacro'))
test_suite.addTest(Test_ROS_urdf('test_endofarm_urdf'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
