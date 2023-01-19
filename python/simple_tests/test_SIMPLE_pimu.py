#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.pimu
import stretch_body.hello_utils as hu

class Test_SIMPLE_pimu(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_pimu')
    test.add_hint('Possible issue with PIMU at udev / hardware / driver level')

    def test_pimu_present(self):
        """
        Check that device is present
        """
        self.assertTrue(hdu.is_device_present('/dev/hello-pimu'))
        ttyACMx=hdu.get_all_ttyACMx()
        self.test.log_data('ttyACMx_devices', ttyACMx)
        p=stretch_body.pimu.Pimu()
        self.assertTrue(p.startup())
        p.stop()

    def test_pimu_sensors(self):
        """
        Check Pimu sensors have reasonable values
        """
        p = stretch_body.pimu.Pimu()
        self.assertTrue(p.startup())
        self.assertTrue(val_in_range('Voltage', p.status['voltage'], vmin=p.config['low_voltage_alert'], vmax=14.5))
        self.assertTrue(val_in_range('Current', p.status['current'], vmin=0.5, vmax=p.config['high_current_alert']))
        self.assertTrue(val_in_range('Temperature', p.status['temp'], vmin=10, vmax=40))
        self.assertTrue(val_in_range('Cliff-0', p.status['cliff_range'][0], vmin=p.config['cliff_thresh'], vmax=20))
        self.assertTrue(val_in_range('Cliff-1', p.status['cliff_range'][1], vmin=p.config['cliff_thresh'], vmax=20))
        self.assertTrue(val_in_range('Cliff-2', p.status['cliff_range'][2], vmin=p.config['cliff_thresh'], vmax=20))
        self.assertTrue(val_in_range('Cliff-3', p.status['cliff_range'][3], vmin=p.config['cliff_thresh'], vmax=20))
        self.assertTrue(val_in_range('IMU AZ', p.status['imu']['az'], vmin=-10.1, vmax=-9.5))
        self.assertTrue(val_in_range('IMU Pitch', hu.rad_to_deg(p.status['imu']['pitch']), vmin=-12, vmax=12))
        self.assertTrue(val_in_range('IMU Roll', hu.rad_to_deg(p.status['imu']['roll']), vmin=-12, vmax=12))
        p.stop()

test_suite = TestSuite(test=Test_SIMPLE_pimu.test,failfast=False)
test_suite.addTest(Test_SIMPLE_pimu('test_pimu_present'))
test_suite.addTest(Test_SIMPLE_pimu('test_pimu_sensors'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
