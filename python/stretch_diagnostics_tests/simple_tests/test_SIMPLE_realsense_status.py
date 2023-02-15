#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_helpers import get_rs_details
import unittest
import subprocess

import sys
from subprocess import Popen, PIPE, STDOUT
from colorama import Fore, Back, Style


class Test_SIMPLE_realsense_status(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_realsense_status')

    def test_get_usb_busID(self):
        """
        Gets the USB Bus number and device ID for monitoring
        """
        out = Popen("usb-devices | grep -B 5 -i 'RealSense' | grep -i 'Bus'", shell=True, bufsize=64, stdin=PIPE,stdout=PIPE, close_fds=True).stdout.read().decode()
        self.assertNotEqual(len(out),0,msg='Realsense D435i not found at USB Bus')
        out_list = out.split(' ')
        bus_no = None
        dev_id = None
        for i in range(len(out_list)):
            if out_list[i].find('Bus') != -1:
                bus_no = out_list[i].split('=')[1]
                bus_no = int(bus_no)
            if out_list[i] == 'Dev#=':
                dev_id = int(out_list[i + 2])
        bus_info = {'bus_no': bus_no, 'device_id': dev_id}
        self.test.log_data('usb_bus_info', bus_info)
        print('Realsense D435i found at USB Bus_No : %d | Device ID : %d' % (bus_no, dev_id))

    def test_get_system_info(self):
        """
        Collect realsense driver information
        """
        driver_info = {}

        fw_details = Popen("rs-fw-update -l | grep -i 'firmware'", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,close_fds=True).stdout.read().decode()
        fw_details = fw_details.split(',')[3]
        fw_version = fw_details.split(' ')[-1]
        driver_info['fw_version'] = fw_version

        nuc_bios_version = Popen("sudo dmidecode -s bios-version", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                                 close_fds=True).stdout.read().decode().rstrip()
        system_version = Popen("sudo dmidecode -s system-version", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                               close_fds=True).stdout.read().decode().rstrip()
        baseboard_version = Popen("sudo dmidecode -s baseboard-version", shell=True, bufsize=64, stdin=PIPE,
                                  stdout=PIPE, close_fds=True).stdout.read().decode().rstrip()
        processor_version = Popen("sudo dmidecode -s processor-version", shell=True, bufsize=64, stdin=PIPE,
                                  stdout=PIPE, close_fds=True).stdout.read().decode().rstrip()
        kernel_version = Popen("uname -r", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                               close_fds=True).stdout.read().decode().rstrip()

        driver_info['nuc_bios_version'] = nuc_bios_version
        driver_info['system_version'] = system_version
        driver_info['baseboard_version'] = baseboard_version
        driver_info['processor_version'] = processor_version
        driver_info['firmware_vekernel_versionrsion'] = kernel_version

        # check_install_v4l2()
        print('\nD435i Firmware version: %s\n' % (fw_version))
        print("Linux Kernel Version : %s" % (kernel_version))
        print("NUC Bios Version : %s" % (nuc_bios_version))
        print("NUC System Version : %s" % (system_version))
        print("NUC Baseboard Version : %s" % (baseboard_version))
        print("Processor Version : %s" % (processor_version))
        self.test.log_data('system_info', driver_info)

    def test_USB3_2_connection(self):
        """
        Check that Realsense camera is on USB3.2 connection
        """
        out = Popen("rs-enumerate-devices| grep Usb | grep 3.2", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,close_fds=True).stdout.read()

        if len(out):
            print('Confirmed USB 3.2 connection to realsense device')
        self.assertIsNot(len(out), 0,msg='Did not find USB 3.2 connection to realsense device')

    def test_realsense_on_usb_bus(self):
        """
        Check that Realsense camera is on USB bus.
        """
        print('---- Checking for Intel D435i ----')
        cmd = "lsusb -d 8086:0b3a"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        self.assertEqual(returned_value,0,'Realsense D435i not found at USB Bus')

    def test_realsense_details(self):
        """
        Capture realsense details and log
        """
        d=get_rs_details()
        self.assertIsNotNone(d,'Not able to launch Realsense driver. It may be conflicting with ROS')
        self.test.log_data('realsense_details',d)

test_suite = TestSuite(test=Test_SIMPLE_realsense_status.test,failfast=False)
test_suite.addTest(Test_SIMPLE_realsense_status('test_realsense_on_usb_bus'))
test_suite.addTest(Test_SIMPLE_realsense_status('test_realsense_details'))
test_suite.addTest(Test_SIMPLE_realsense_status('test_USB3_2_connection'))
test_suite.addTest(Test_SIMPLE_realsense_status('test_get_system_info'))
test_suite.addTest(Test_SIMPLE_realsense_status('test_get_usb_busID'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
