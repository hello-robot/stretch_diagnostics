#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner
import os
from subprocess import Popen, PIPE


class Test_SIMPLE_capture_system(unittest.TestCase):
    """
    Capture and log stretch system infos
    """

    test = TestBase('test_SIMPLE_capture_system')

    def run_save_log(self, cmd, fn):
        file_path = "{}/{}_{}.log".format(self.test.results_directory_test_specific, fn, self.test.timestamp)
        os.system('{} >> {}'.format(cmd, file_path))

    def test_log_hardware_echo(self):
        """
        Log stretch_hardware_echo.py
        """
        self.run_save_log('stretch_hardware_echo.py', 'stretch_hardware_echo')

    def test_log_usb_topology(self):
        """
        Log lsusb -v -t
        """
        self.run_save_log('lsusb -v -t', 'usb_topology')

    def test_log_stretch_version_script(self):
        """
        log stretch_version.sh
        """
        self.run_save_log('stretch_version.sh', 'stretch_version')

    def test_log_system_info(self):
        """
        Collect system information
        """
        driver_info = {}

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
        print("Linux Kernel Version : %s" % (kernel_version))
        print("NUC Bios Version : %s" % (nuc_bios_version))
        print("NUC System Version : %s" % (system_version))
        print("NUC Baseboard Version : %s" % (baseboard_version))
        print("Processor Version : %s" % (processor_version))
        self.test.log_data('system_info', driver_info)


test_suite = TestSuite(test=Test_SIMPLE_capture_system.test, failfast=False)
test_suite.addTest(Test_SIMPLE_capture_system('test_log_hardware_echo'))
test_suite.addTest(Test_SIMPLE_capture_system('test_log_usb_topology'))
test_suite.addTest(Test_SIMPLE_capture_system('test_log_stretch_version_script'))
test_suite.addTest(Test_SIMPLE_capture_system('test_log_system_info'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
