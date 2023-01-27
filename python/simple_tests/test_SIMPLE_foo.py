#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner

"""
This is a Template script for writing a SIMPLE type Test and generating a Test suite.
"""


class Test_SIMPLE_foo(unittest.TestCase):
    """
    Class level doc string describing this SIMPLE type TestCase class
    """

    # test object is always expected within a TestCase Class
    test = TestBase('test_SIMPLE_foo')
    test.add_hint("This test is foo failure.")

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

    def test_foo_1(self):
        """
        Short Description : Test foo 1

        """
        # a = 10 * (1 / 0)
        self.assertEqual(0, 0)
        self.test.log_params('param_key1', 'any value')
        self.test.log_data('data_key1', 100)
        if 1 > 0:
            self.test.add_hint("Foo 1 hint.")

    def test_foo_2(self):
        """
        Short Description : Test foo 2
        """
        self.assertEqual(0, 0)
        self.test.log_params('param_key2', {'val': 0})

    def test_foo_3(self):
        """
        Short Description : Test foo 3
        """
        self.assertTrue(96 > len('hello'))


# Initialize you test suite with TestSuite(test,failfast)
# Arguments:
#   test = Test Object inside TestCase Class
#   failfast = If "True" the test exits at the first failiure. Use it for tests-order sensitive tests.
test_suite = TestSuite(test=Test_SIMPLE_foo.test, failfast=False)

# Add tests from the Test Class to the test_suite in the same order it would be run.
test_suite.addTest(Test_SIMPLE_foo('test_foo_1'))
test_suite.addTest(Test_SIMPLE_foo('test_foo_2'))
test_suite.addTest(Test_SIMPLE_foo('test_foo_3'))

if __name__ == '__main__':
    # Create a TestRunner object with TestRunner(suite,doc_verify_fail)
    # Arguments:
    #   suite = test_suite built
    #   doc_verify_fail = If "True" , checks if Class level and Test level docstring descriptions available
    #                     If not available reports the missing description and exits the script.
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
