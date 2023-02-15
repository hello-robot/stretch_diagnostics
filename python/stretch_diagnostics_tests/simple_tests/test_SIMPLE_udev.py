#!/usr/bin/env python3
import stretch_diagnostics.test_helpers as test_helpers
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.stepper
import stretch_body.hello_utils as hu
import os
import glob


class Test_SIMPLE_udev(unittest.TestCase):
    """
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_udev')

    arduino_devices = ['hello-wacc',
                     'hello-motor-left-wheel',
                     'hello-pimu',
                     'hello-motor-arm',
                     'hello-motor-right-wheel',
                     'hello-motor-lift']

    dynamixel_devices= ['hello-dynamixel-head','hello-dynamixel-wrist']


    def test_udev_log(self):
        """
        Log udev files for Stretch devices.
        """
        udev_files_list= glob.glob('/etc/udev/rules.d/*hello*.rules')
        for p in udev_files_list:
            fn_no_path=p[p.rfind('/'):]
            new_fn=fn_no_path+'_%s.log'%self.test.timestamp
            os.system("cp %s %s"%(p,self.test.test_result_dir+new_fn))

        ls_l_file = self.test.test_result_dir+'/hello_usb_symlinks_%s.log'%self.test.timestamp
        os.system('ls -l /dev/hello* >>%s'%ls_l_file)

    def test_dynamixel_udev(self):
        """
        Check that all Dynamixels devices have valid UDEV mappings.
       """
        for s in self.dynamixel_devices:
            port = '/dev/' + s
            print('Checking UDEV for %s' % port)
            dp = hdu.is_device_present(port)
            self.assertTrue(dp, msg='Device %s not on bus' % s)
            udev_sn = test_helpers.get_serial_nos_from_udev('/etc/udev/rules.d/99-hello-dynamixel.rules', s)
            self.assertFalse(len(udev_sn) == 0,'UDEV rule for %s not found in /etc/udev/rules.d/99-hello-dynamixel.rules' % s)
            self.assertFalse(len(udev_sn) > 1,'Multiple UDEV rules for %s found in /etc/udev/rules.d/99-hello-dynamixel.rules' % s)

    def test_ftdi_device_count(self):
        """
        Check that there are two FTDI devices on bus.
        """
        tty_dev=test_helpers.find_tty_devices()
        dxl_keys=[]
        for k in tty_dev.keys():
            if tty_dev[k]['model']=='FT232R_USB_UART':
                dxl_keys.append(k)
        self.assertTrue(len(dxl_keys)==2,msg='Did not find two FTDI devices for Dynamixels')

    def test_ttyACM_symlinks(self):
        """
        Check that all ttyACM devices have symlinks.
        """
        # First check that there are at least 6 TTYACM devices
        ttyACM_SN_map = test_helpers.find_arduino_devices_sn()  # dict of {'/dev/ttyACM6': 'E469692150555733352E3120FF0A0C22',...}
        self.assertTrue(len(ttyACM_SN_map) >= 6,'Found less than 6 ttyACM devices')
        self.test.log_data('arduino_devices_udevadm', ttyACM_SN_map)

        # Now check that all ttyACM have symlinks
        for ttyACM in ttyACM_SN_map.keys():
            # Returns something like if mapped
            # ['/dev/hello-wacc',
            #  '/dev/serial/by-id/usb-Arduino_LLC_Hello_Wacc_C9D6FD8750555733352E3120FF0C0D1A-if00',
            #  '/dev/serial/by-path/pci-0000:00:14.0-usb-0:4.2.3.3:1.0']
            devlinks = test_helpers.extract_udevadm_info(ttyACM, 'DEVLINKS').split(' ')
            sn = test_helpers.extract_udevadm_info(ttyACM, 'ID_SERIAL_SHORT')
            print('Checking symlinks for %s' % ttyACM)
            # print('DEVLINKS',devlinks)
            if len(devlinks) < 3:
                self.test.log_data('missing_symlink_%s' % ttyACM, test_helpers.extract_udevadm_info(ttyACM))
            self.assertTrue(len(devlinks) == 3,'Device %s with serial %s lacks UDEV symlink.' % (ttyACM, sn))

    def test_arduino_udev(self):
        """
        Check that all arduino devices have valid UDEV mappings.
       """
        for s in self.arduino_devices:
            port='/dev/'+s
            print('Checking UDEV for %s'%port)
            dp = hdu.is_device_present(port)
            self.assertTrue(dp, msg='Device %s not on bus' % s)
            udev_sn = test_helpers.get_serial_nos_from_udev('/etc/udev/rules.d/95-hello-arduino.rules', s)
            self.assertFalse(len(udev_sn) == 0,'UDEV rule for %s not found in /etc/udev/rules.d/95-hello-arduino.rules' % s)
            self.assertFalse(len(udev_sn) > 1,'Multiple UDEV rules for %s found in /etc/udev/rules.d/95-hello-arduino.rules' % s)


test_suite = TestSuite(test=Test_SIMPLE_udev.test,failfast=False)
test_suite.addTest(Test_SIMPLE_udev('test_udev_log'))
test_suite.addTest(Test_SIMPLE_udev('test_ttyACM_symlinks'))
test_suite.addTest(Test_SIMPLE_udev('test_arduino_udev'))
test_suite.addTest(Test_SIMPLE_udev('test_ftdi_device_count'))
test_suite.addTest(Test_SIMPLE_udev('test_dynamixel_udev'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
