#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner


class Test_SIMPLE_filesystem(unittest.TestCase):
    """
    Verify the filesystem integrity of the stretch robot
    """

    test = TestBase('test_SIMPLE_filesystem')

    def test_check_stretch_user_files(self):
        pass

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
