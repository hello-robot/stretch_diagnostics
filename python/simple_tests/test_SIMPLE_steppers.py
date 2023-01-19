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
        Check that stepper is present
        """
        for s in self.steppers:
            self.assertTrue(hdu.is_device_present(s))

    def test_steppers_udev(self):
        for s in self.steppers:
            udev_sn=test_helpers.get_serial_nos_from_udev('/etc/udev/rules.d/95-hello-arduino.rules', s)
            uda_sn=test_helpers.extract_udevadm_info('/dev/hello-motor-arm',ID_NAME='ID_SERIAL_SHORT')
            uda_


    def test_wacc_sensors(self):
        """
        Check wacc sensors have reasonable values
        """
        d = stretch_body.wacc.Wacc()
        self.assertTrue(d.startup())
        d.pull_status()
        ax_in_range=val_in_range('AX', d.status['ax'], vmin=9.0, vmax=10.5)
        if d.status['ax']==0:
            self.test.add_hint('AX of 0. Possible communication failure with accelerometer.')
        self.assertTrue(ax_in_range)
        d.stop()

test_suite = TestSuite(test=Test_SIMPLE_steppers.test,failfast=False)
test_suite.addTest(Test_SIMPLE_steppers('test_wacc_present'))
test_suite.addTest(Test_SIMPLE_steppers('test_wacc_sensors'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
