#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner
import os


class Test_SIMPLE_filesystem(unittest.TestCase):
    """
    Verify the filesystem integrity of the stretch robot
    """

    test = TestBase('test_SIMPLE_filesystem')

    def check_file_paths(self, file_path_list):
        for f in file_path_list:
            check = os.path.isfile(os.path.expanduser(f))
            self.assertTrue(check, "File not found : {}".format(f))
            self.test.add_hint("File not found : {}".format(f))

    def check_dir_paths(self, file_dir_list):
        for f in file_dir_list:
            check = os.path.isfile(os.path.expanduser(f))
            self.assertTrue(check, "Directory not found : {}".format(f))
            self.test.add_hint("Directory not found : {}".format(f))

    def test_check_stretch_user_files(self):
        """
        Verify existance of user files
        """
        files = ["~/stretch_user/{}/stretch_configuration_params.yaml".format(self.test.fleet_id),
                 "~/stretch_user/{}/stretch_user_params.yaml".format(self.test.fleet_id)]
                # ADD More

        dirs = ["~/stretch_user",
                "~/stretch_user/{}/calibration_base_imu".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_steppers".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_D43i".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_guarded_contact".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_ros".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_guarded_contact".format(self.test.fleet_id),
                "~/stretch_user/{}/exported_urdf".format(self.test.fleet_id),
                "~/stretch_user/{}/udev".format(self.test.fleet_id)]

        self.check_dir_paths(dirs)
        self.check_file_paths(files)

    def test_udev_files(self):
        pass

    def test_autostart_files(self):
        pass

    def test_etc_files(self):
        pass

    def test_stretch_ros_files(self):
        pass

    def test_storage_space(self):
        pass


test_suite = TestSuite(test=Test_SIMPLE_filesystem.test, failfast=False)
test_suite.addTest(Test_SIMPLE_filesystem('test_check_stretch_user_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_udev_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_autostart_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_etc_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_stretch_ros_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_storage_space'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
