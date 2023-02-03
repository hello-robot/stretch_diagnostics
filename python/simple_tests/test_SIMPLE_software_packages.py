#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_helpers import check_internet
import pkg_resources
import unittest
import distro
import requests
import click
import apt


# The tests were adapted from:
# https://github.com/hello-robot/stretch_body/blob/feature/system_check_improvements/tools/test/test_system.py

class Test_SIMPLE_software_packages(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_software_packages')
    test.add_hint('Possible issues with software packages installed.')

    def test_check_internet(self):
        """
        Check if the robot is connected to the internet
        """
        while not check_internet():
            input(click.style("Robot not connected to the Internet. Connect to the Internet and press Enter.",
                              fg='yellow', bold=True))
        self.assertTrue(check_internet(), " Robot not connected to the Internet. Connect the robot")

    def test_latest_hello_pip_packages(self):
        """
        Stretch Python libraries up-to-date
        """
        ubuntu_to_pip_mapping = {'18.04': 'pip2', '20.04': 'pip3'}
        pip_str = ubuntu_to_pip_mapping[distro.version()]

        self.test.log_data("ubuntu_version", distro.version())

        def get_installed_package_versions(find_specific=None):
            packages = {}
            for package in pkg_resources.working_set:
                packages[package.key] = package.version
            if find_specific:
                return packages[find_specific]
            return packages

        def get_latest_package_version(package_name):
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                return data["info"]["version"]
            else:
                return None

        # Stretch Body
        installed_stretch_body_version = get_installed_package_versions("hello-robot-stretch-body")
        latest_stretch_body_version = get_latest_package_version("hello-robot-stretch-body")

        print("Found Stretch Body : current_version={} | latest_version={}".format(installed_stretch_body_version,
                                                                                   latest_stretch_body_version))
        self.test.log_params("latest_stretch_body_version", latest_stretch_body_version)
        self.test.log_data("installed_stretch_body_version", installed_stretch_body_version)

        self.assertEqual(installed_stretch_body_version, latest_stretch_body_version,
                         msg="run {} install -U hello-robot-stretch-body".format(pip_str))

        # Stretch Body Tools
        installed_stretch_body_tools_version = get_installed_package_versions("hello-robot-stretch-body-tools")
        latest_stretch_body_tools_version = get_latest_package_version("hello-robot-stretch-body-tools")

        print("Found Stretch Body Tools : current_version={} | latest_version={}".format(installed_stretch_body_tools_version,
                                                                                   latest_stretch_body_tools_version))
        self.test.log_params("latest_stretch_body_tools_version", latest_stretch_body_tools_version)
        self.test.log_data("installed_stretch_body_tools_version", installed_stretch_body_tools_version)

        self.assertEqual(installed_stretch_body_tools_version, latest_stretch_body_tools_version,
                         msg="run {} install -U hello-robot-stretch-body-tools".format(pip_str))

        # Stretch Factory
        installed_stretch_factory_version = get_installed_package_versions("hello-robot-stretch-factory")
        latest_stretch_factory_version = get_latest_package_version("hello-robot-stretch-factory")

        print("Found Stretch Factory : current_version={} | latest_version={}".format(installed_stretch_factory_version,
                                                                                   latest_stretch_factory_version))
        self.test.log_params("latest_stretch_factory_version", latest_stretch_factory_version)
        self.test.log_data("installed_stretch_factory_version", installed_stretch_factory_version)

        self.assertEqual(installed_stretch_factory_version, latest_stretch_factory_version,
                         msg="run {} install -U hello-robot-stretch-factory".format(pip_str))

        # Stretch Tool Share
        installed_stretch_tool_share_version = get_installed_package_versions("hello-robot-stretch-tool-share")
        latest_stretch_tool_share_version = get_latest_package_version("hello-robot-stretch-tool-share")

        print("Found Stretch Tool Share : current_version={} | latest_version={}".format(installed_stretch_tool_share_version,
                                                                                   latest_stretch_tool_share_version))
        self.test.log_params("latest_stretch_tool_share_version", latest_stretch_tool_share_version)
        self.test.log_data("installed_stretch_tool_share_version", installed_stretch_tool_share_version)

        self.assertEqual(installed_stretch_tool_share_version, latest_stretch_tool_share_version,
                         msg="run {} install -U hello-robot-stretch-tool-share".format(pip_str))

    def test_realsense_sw_configuration(self):
        """
        Realsense setup correctly
        """
        apt_list = apt.Cache()
        if distro.version() == '18.04':
            self.test.log_data('ros-melodic-librealsense2', 'ros-melodic-librealsense2' in apt_list)
            self.assertTrue('ros-melodic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-melodic-librealsense2'].is_installed)

        if distro.version() == '20.04':
            self.test.log_data('ros-noetic-librealsense2', 'ros-noetic-librealsense2' in apt_list)
            self.assertTrue('ros-noetic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-noetic-librealsense2'].is_installed)

            self.test.log_data('ros-galactic-librealsense2', 'ros-galactic-librealsense2' in apt_list)
            self.assertTrue('ros-galactic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-galactic-librealsense2'].is_installed)


test_suite = TestSuite(test=Test_SIMPLE_software_packages.test, failfast=False)
test_suite.addTest(Test_SIMPLE_software_packages('test_check_internet'))
test_suite.addTest(Test_SIMPLE_software_packages('test_latest_hello_pip_packages'))
test_suite.addTest(Test_SIMPLE_software_packages('test_realsense_sw_configuration'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
