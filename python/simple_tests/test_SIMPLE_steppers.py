#!/usr/bin/env python3
import stretch_diagnostics.test_helpers as test_helpers
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.stepper
import stretch_body.hello_utils as hu

class Test_SIMPLE_steppers(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_steppers')
    test.add_hint('Possible issue with stepper at udev / hardware / driver level')
    steppers = ['hello-motor-right-wheel','hello-motor-left-wheel','hello-motor-arm','hello-motor-lift']

    def test_steppers_present(self):
        """
        Check that steppers are present
        """
        for s in self.steppers:
            self.assertTrue(hdu.is_device_present('/dev/'+s),msg='Stepper %s not found on USB bus'%s)

test_suite = TestSuite(test=Test_SIMPLE_steppers.test,failfast=False)
test_suite.addTest(Test_SIMPLE_steppers('test_steppers_present'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
