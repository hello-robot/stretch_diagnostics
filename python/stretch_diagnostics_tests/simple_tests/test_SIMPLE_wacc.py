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
        self.assertTrue(dp,msg='Device /dev/hello-wacc not present')
        ttyACMx=hdu.get_all_ttyACMx()
        self.test.log_data('ttyACMx_devices', ttyACMx)
        d=stretch_body.wacc.Wacc()
        su=d.startup()
        self.assertTrue(su,msg='Device /dev/hello-wacc found but not able to startup')
        d.stop()

    def test_wacc_sensors(self):
        """
        Check wacc sensors have reasonable values
        """
        d = stretch_body.wacc.Wacc()
        self.assertTrue(d.startup(),'Wacc startup failed.')
        d.pull_status()
        self.assertFalse(d.status['ax']==0,'AX of 0. Possible communication failure with accelerometer.')
        self.assertTrue(val_in_range('AX', d.status['ax'], vmin=9.0, vmax=10.5),msg='AX value of %f outside of bounds'%d.status['ax'])
        d.stop()

test_suite = TestSuite(test=Test_SIMPLE_wacc.test,failfast=True)
test_suite.addTest(Test_SIMPLE_wacc('test_wacc_present'))
test_suite.addTest(Test_SIMPLE_wacc('test_wacc_sensors'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
