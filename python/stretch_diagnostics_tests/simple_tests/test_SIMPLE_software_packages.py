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


class Test_SIMPLE_software_packages(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_software_packages')

    def test_check_internet(self):
        """
        Check if the robot is connected to the internet
        """
        while not check_internet():
            input(click.style("Robot not connected to the Internet. Connect to the Internet and press Enter.",
                              fg='yellow', bold=True))
        self.assertTrue(check_internet(), " Robot not connected to the Internet. Connect the robot")

    def check_if_latest(self, pkg_name):
        ubuntu_to_pip_mapping = {'18.04': 'pip2', '20.04': 'pip3'}
        pip_str = ubuntu_to_pip_mapping[distro.version()]

        installed_version = get_installed_package_versions(pkg_name)
        latest_version = get_latest_package_version(pkg_name)

        print("Found {} : current_version={} | latest_version={}".format(pkg_name, installed_version,
                                                                         latest_version))
        self.test.log_params("latest_{}_version".format(pkg_name), latest_version)
        self.test.log_data("installed_{}_version".format(pkg_name), installed_version)

        self.assertEqual(installed_version, latest_version,
                         msg=f"Newer version v{latest_version} available | run `{pip_str} install -U {pkg_name}`")

    def test_stretch_body(self):
        """
        Test stretch body package version
        """
        self.check_if_latest('hello-robot-stretch-body')

    def test_stretch_body_tools(self):
        """
        Test stretch body tools package version
        """
        self.check_if_latest('hello-robot-stretch-body-tools')

    def test_stretch_factory(self):
        """
        Test stretch factory package version
        """
        self.check_if_latest('hello-robot-stretch-factory')

    def test_stretch_tool_share(self):
        """
        Test stretch tool share package version
        """
        self.check_if_latest('hello-robot-stretch-tool-share')

    def test_realsense_sw_configuration(self):
        """
        Realsense setup correctly
        """
        apt_list = apt.Cache()
        if distro.version() == '18.04':
            self.test.log_data('ros-melodic-librealsense2', 'ros-melodic-librealsense2' in apt_list)
            self.assertTrue('ros-melodic-librealsense2' in apt_list,'ros-melodic-librealsense2 not found in apt')
            self.assertFalse(apt_list['ros-melodic-librealsense2'].is_installed,'Library ros-melodic-librealsense2 is installed')


        if distro.version() == '20.04':
            self.test.log_data('ros-noetic-librealsense2', 'ros-noetic-librealsense2' in apt_list)
            self.assertTrue('ros-noetic-librealsense2' in apt_list,'ros-noetic-librealsense2 not found in apt')

            self.assertFalse(apt_list['ros-noetic-librealsense2'].is_installed,'Library ros-noetic-librealsense2 is installed')

            self.test.log_data('ros-galactic-librealsense2', 'ros-galactic-librealsense2' in apt_list)
            self.assertTrue('ros-galactic-librealsense2' in apt_list,'ros-galactic-librealsense2 not found in apt')

            self.assertFalse(apt_list['ros-galactic-librealsense2'].is_installed,'Library ros-galactic-librealsense2 is installed')


test_suite = TestSuite(test=Test_SIMPLE_software_packages.test, failfast=False)
test_suite.addTest(Test_SIMPLE_software_packages('test_check_internet'))
test_suite.addTest(Test_SIMPLE_software_packages('test_stretch_body'))
test_suite.addTest(Test_SIMPLE_software_packages('test_stretch_body_tools'))
test_suite.addTest(Test_SIMPLE_software_packages('test_stretch_factory'))
test_suite.addTest(Test_SIMPLE_software_packages('test_stretch_tool_share'))
test_suite.addTest(Test_SIMPLE_software_packages('test_realsense_sw_configuration'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
