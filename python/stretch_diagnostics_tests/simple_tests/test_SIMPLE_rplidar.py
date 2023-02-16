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

    def test_rplidar_present(self):
        """
        Check that hello-lrf device is present
        """
        try:
            nd=len(glob.glob('/dev/ttyUSB*'))>=3
            dp = hdu.is_device_present('/dev/hello-lrf')
            self. assertTrue(nd,'Not enough ttyUSB devices found. Check RPLidar cables.')
            self.assertTrue(dp,'/dev/hello-lrf device not found. Check UDEV rules.')
            #Start and stop device to reset connection (see https://github.com/SkoltechRobotics/rplidar/issues/34)
            rplidar = RPLidar('/dev/hello-lrf')
            rplidar.stop_motor()
            rplidar.stop()
            rplidar.disconnect()
        except RPLidarException:
            self.assertTrue(0,msg='RPLidar exception. Check all cables to device.')

    def test_rplidar_speed(self):
        """
        Measure the scan rate (points-per-sec) for 10s
        """
        ts=time.time()
        try:
            rplidar = RPLidar('/dev/hello-lrf')
            old_t = None
            points_per_sec = []
            for i, scan in enumerate(rplidar.iter_scans(scan_type='express')):
                now = time.time()
                if old_t is None:
                    old_t = now
                    continue
                delta = now - old_t
                print('%.2f points-per-sec' % (len(scan)/delta))
                points_per_sec.append(len(scan)/delta)
                old_t = now
                if now-ts>10.0:
                    break

            ah = sum(points_per_sec) / len(points_per_sec)
            print('Mean points-per-sec: %.2f Hz' % (ah))
            self.test.log_data('rplidar_points_per_sec', points_per_sec)
            self.assertTrue(ah>2500.0,'RPLidar scan rate of %f points-per-sec below threshold of 2500. Check USB cables.'%ah)
        except RPLidarException:
            self.assertTrue(0, msg='RPLidar exception. Check all cables to device.')

    def test_rplidar_scan(self):
        """
        Check that rplidar can generate a complete scan
        """
        try:
            rplidar = RPLidar('/dev/hello-lrf')
            for i, scan in enumerate(rplidar.iter_scans()):
                if i > 0:
                    break
            print('%d: Got %d RPLidar scan measurments' % (i, len(scan)))
            rplidar.stop_motor()
            rplidar.stop()
            rplidar.disconnect()
            self.assertTrue(len(scan)>90,'Scan length %d is too short'%len(scan)) #Should be 125+
            self.test.log_data('rplidar_scan', str(scan))
        except RPLidarException:
            self.assertTrue(0,msg='RPLidar exception. Check all cables to device.')
    def test_rplidar_info(self):
        """
        Check rplidar can report health and info
        """
        try:
            rplidar = RPLidar('/dev/hello-lrf')
            info = rplidar.get_info()
            self.assertTrue(len(info)>0,'Invalid info returned')
            info['firmware']=list(info['firmware']) #Tuple makes YAML choke
            info['health']=list(rplidar.get_health())
            rplidar.stop_motor()
            rplidar.stop()
            rplidar.disconnect()
            self.test.log_data('rplidar_info', info)
        except RPLidarException:
            self.assertTrue(0,msg='RPLidar exception. Check all cables to device.')

test_suite = TestSuite(test=Test_SIMPLE_rplidar.test,failfast=True)
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_present'))
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_info'))
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_scan'))
test_suite.addTest(Test_SIMPLE_rplidar('test_rplidar_speed'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
