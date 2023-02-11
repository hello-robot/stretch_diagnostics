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

    def check_dir_paths(self, file_dir_list):
        for f in file_dir_list:
            check = os.path.isdir(os.path.expanduser(f))
            self.assertTrue(check, "Directory not found : {}".format(f))

    def check_file_paths(self, file_path_list):
        for f in file_path_list:
            check = os.path.isfile(os.path.expanduser(f))
            self.assertTrue(check, "File not found : {}".format(f))

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
                "~/stretch_user/{}/calibration_D435i".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_guarded_contact".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_ros".format(self.test.fleet_id),
                "~/stretch_user/{}/calibration_guarded_contact".format(self.test.fleet_id),
                "~/stretch_user/{}/exported_urdf".format(self.test.fleet_id),
                "~/stretch_user/{}/udev".format(self.test.fleet_id)]

        self.test.log_params("stretch_user_dir_checks", dirs)
        self.test.log_params("stretch_user_files_checks", files)
        self.check_dir_paths(dirs)
        self.check_file_paths(files)

    def test_udev_files(self):
        """
        verify if all the udev files copied during stretch install is present
        """
        files = ["~/stretch_user/{}/udev/60-openocd.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/90-hello-respeaker.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/91-hello-lrf.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/94-hello-usb.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/95-hello-arduino.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/97-intel-ncs2.rules".format(self.test.fleet_id),
                 "~/stretch_user/{}/udev/99-hello-dynamixel.rules".format(self.test.fleet_id)]
        self.check_file_paths(files)

    def test_autostart_files(self):
        """
        Verify if all autostart scripts present
        """
        files = ["/bin/hello_robot_audio.sh",
                 "/bin/hello_robot_lrf_off.py",
                 "/bin/hello_robot_pimu_ping.py",
                 "/bin/hello_robot_pimu_ping.sh",
                 "/bin/hello_robot_xbox_teleop.sh"]
        self.check_file_paths(files)

    def test_etc_files(self):
        """
        Check if /etc directory has stretch user files and udev
        """
        dirs = ["/etc/hello-robot/{}".format(self.test.fleet_id)]
        files = ["/etc/udev/rules.d/60-openocd.rules",
                 "/etc/udev/rules.d/90-hello-respeaker.rules",
                 "/etc/udev/rules.d/91-hello-lrf.rules",
                 "/etc/udev/rules.d/94-hello-usb.rules",
                 "/etc/udev/rules.d/95-hello-arduino.rules",
                 "/etc/udev/rules.d/97-intel-ncs2.rules",
                 "/etc/udev/rules.d/99-hello-dynamixel.rules"]
        self.check_dir_paths(dirs)
        self.check_file_paths(files)

    def test_storage_space(self):
        """
        TODO
        """
        pass


test_suite = TestSuite(test=Test_SIMPLE_filesystem.test, failfast=False)
test_suite.addTest(Test_SIMPLE_filesystem('test_check_stretch_user_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_udev_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_autostart_files'))
test_suite.addTest(Test_SIMPLE_filesystem('test_etc_files'))
# test_suite.addTest(Test_SIMPLE_filesystem('test_storage_space'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
