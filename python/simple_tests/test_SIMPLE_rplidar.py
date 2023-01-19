#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
from rplidar import *
import glob

class Test_SIMPLE_rplidar(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_rplidar')
    test.add_hint('Possible issue with rplidar at hardware level. Check cables.')

    def test_rplidar_present(self):
        """
        Check that device is present
        """
        nd=len(glob.glob('/dev/ttyUSB*'))>=3
        if not nd:
            self.test.add_hint('Not enough ttyUSB devices found. Check RPLidar cables.')
        dp = hdu.is_device_present('/dev/hello-lrf')
        if not dp:
            self.test.add_hint('/dev/hello-lrf device not found. Check UDEV rules.')
        self.assertTrue(nd)
        self.assertTrue(dp)

    def test_rplidar_scan(self):
        """
        Check that rplidar can generate a complete scan
        """
        rplidar = RPLidar('/dev/hello-lrf')
        for i, scan in enumerate(rplidar.iter_scans()):
            if i > 0:
                break
        print('%d: Got %d RPLidar scan measurments' % (i, len(scan)))
        self.assertTrue(len(scan)>100) #Should be 125+
        self.test.log_data('rplidar_scan', str(scan))

    def test_rplidar_info(self):
        """
        Check rplidar can report health and info
        """
        rplidar = RPLidar('/dev/hello-lrf')
        info = rplidar.get_info()
        self.assertTrue(len(info)>0)
        info['firmware']=list(info['firmware']) #Tuple makes YAML choke
        info['health']=list(rplidar.get_health())
        self.test.log_data('rplidar_info', info)

test_suite = TestSuite(test=Test_SIMPLE_rplidar.test,failfast=False)
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_present'))
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_info'))
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_scan'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
