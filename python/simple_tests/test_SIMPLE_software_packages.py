#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_body.device
import stretch_body.pimu
import stretch_body.hello_utils
import stretch_body.head
import stretch_body.wacc
import stretch_body.base
import stretch_body.lift
import stretch_body.arm
import distro
import requests
import xmltodict
import apt


# The tests were adapted from:
# https://github.com/hello-robot/stretch_body/blob/feature/system_check_improvements/tools/test/test_system.py

# xmltodict is a depedency ?

class Test_SIMPLE_software_packages(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_software_packages')
    test.add_hint('Possible issues with software packages installed.')

    def test_latest_hello_pip_packages(self):
        """
        Stretch Python libraries up-to-date
        """
        dummy_device = stretch_body.device.Device('dummy', req_params=False)
        ubuntu_to_pip_mapping = {'18.04': 'pip2', '20.04': 'pip3'}
        pip_str = ubuntu_to_pip_mapping[distro.version()]

        def get_latest_version(url):
            resp = requests.get(url)
            if resp.status_code == 200:
                releases = xmltodict.parse(resp.text)['rss']['channel']['item']
                for i in range(len(releases)):
                    if 'dev' not in releases[i]['title']:
                        return releases[i]['title']
            return None

        # Stretch Body
        try:
            from stretch_body.version import __version__ as installed_stretch_body_version
        except:
            installed_stretch_body_version = None
        latest_stretch_body_version = get_latest_version(
            "https://pypi.org/rss/project/hello-robot-stretch-body/releases.xml")
        dummy_device.logger.debug(
            "hello-robot-stretch-body installed={0}, latest available={1}".format(installed_stretch_body_version,
                                                                                  latest_stretch_body_version))
        self.assertEqual(installed_stretch_body_version, latest_stretch_body_version,
                         msg="run {} install -U hello-robot-stretch-body".format(pip_str))

        # Stretch Body Tools
        try:
            from stretch_body_tools.version import __version__ as installed_stretch_body_tools_version
        except:
            installed_stretch_body_tools_version = None
        latest_stretch_body_tools_version = get_latest_version(
            "https://pypi.org/rss/project/hello-robot-stretch-body-tools/releases.xml")
        dummy_device.logger.debug("hello-robot-stretch-body-tools installed={0}, latest available={1}".format(
            installed_stretch_body_tools_version, latest_stretch_body_tools_version))
        self.assertEqual(installed_stretch_body_tools_version, latest_stretch_body_tools_version,
                         msg="run {} install -U hello-robot-stretch-body-tools".format(pip_str))

        # Stretch Factory
        try:
            from stretch_factory.version import __version__ as installed_stretch_factory_version
        except:
            installed_stretch_factory_version = None
        latest_stretch_factory_version = get_latest_version(
            "https://pypi.org/rss/project/hello-robot-stretch-factory/releases.xml")
        dummy_device.logger.debug("hello-robot-stretch-factory installed={0}, latest available={1}".format(
            installed_stretch_factory_version, latest_stretch_factory_version))
        self.assertEqual(installed_stretch_factory_version, latest_stretch_factory_version,
                         msg="run {} install -U hello-robot-stretch-factory".format(pip_str))

        # Stretch Tool Share
        try:
            from stretch_tool_share.version import __version__ as installed_stretch_tool_share_version
        except:
            installed_stretch_tool_share_version = None
        latest_stretch_tool_share_version = get_latest_version(
            "https://pypi.org/rss/project/hello-robot-stretch-tool-share/releases.xml")
        dummy_device.logger.debug("hello-robot-stretch-tool-share installed={0}, latest available={1}".format(
            installed_stretch_tool_share_version, latest_stretch_tool_share_version))
        self.assertEqual(installed_stretch_tool_share_version, latest_stretch_tool_share_version,
                         msg="run {} install -U hello-robot-stretch-tool-share".format(pip_str))

    def test_realsense_sw_configuration(self):
        """
        Realsense setup correctly
        """
        apt_list = apt.Cache()
        if distro.version() == '18.04':
            self.assertTrue('ros-melodic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-melodic-librealsense2'].is_installed)
        if distro.version() == '20.04':
            self.assertTrue('ros-noetic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-noetic-librealsense2'].is_installed)
            self.assertTrue('ros-galactic-librealsense2' in apt_list)
            self.assertFalse(apt_list['ros-galactic-librealsense2'].is_installed)


test_suite = TestSuite(test=Test_SIMPLE_software_packages.test, failfast=False)
test_suite.addTest(Test_SIMPLE_software_packages('test_latest_hello_pip_packages'))
test_suite.addTest(Test_SIMPLE_software_packages('test_realsense_sw_configuration'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
