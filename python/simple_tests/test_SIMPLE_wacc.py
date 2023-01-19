#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.wacc
import stretch_body.hello_utils as hu

class Test_SIMPLE_wacc(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_wacc')

    def test_wacc_present(self):
        """
        Check that device is present
        """
        dp=hdu.is_device_present('/dev/hello-wacc')
        if not dp:
            self.test.add_hint('Wacc not on bus. May be UDEV or hardware issue.')
        self.assertTrue(dp,msg='Device /dev/hello-wacc not present')
        ttyACMx=hdu.get_all_ttyACMx()
        self.test.log_data('ttyACMx_devices', ttyACMx)
        d=stretch_body.wacc.Wacc()
        su=d.startup()
        if not su:
            self.test.add_hint('Not able to startup Wacc. Possible issue with firmware version')
        self.assertTrue(su,msg='Not able to startup Wacc')
        d.stop()

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

test_suite = TestSuite(test=Test_SIMPLE_wacc.test,failfast=True)
test_suite.addTest(Test_SIMPLE_wacc('test_wacc_present'))
test_suite.addTest(Test_SIMPLE_wacc('test_wacc_sensors'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
