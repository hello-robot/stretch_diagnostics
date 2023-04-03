#!/usr/bin/env python3

from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
from stretch_body.dynamixel_XL430 import DynamixelXL430, DynamixelCommError
from stretch_body.robot_params import RobotParams
import os


class Test_DYNAMIXEL_hardware(unittest.TestCase):
    """
    Test Dynamixel for Hardware issues
    """
    test = TestBase('test_DYNAMIXEL_hardware')
    
    def get_servo_ids(self, port, baud_to=115200):
        found_ids = []
        print('\nScanning for servo at port: {}'.format(port))
        print('----------------------------------------------------------')
        b = baud_to
        for id in range(20):
            print("Checking at ID %d and baud %d" % (id, b))
            m = DynamixelXL430(id, port, baud=b)
            m.logger.disabled = True
            try:
                if m.startup():
                    print('Found servo at ID %d and Baud %d' % (id, b))
                    found_ids.append(id)
            except DynamixelCommError:
                print("ping failed for ID: " + str(id))
                continue
        return found_ids
    
    def check_elements(self, list2, list1):
        not_found = []
        for element in list1:
            if element not in list2:
                not_found.append(element)
        if len(not_found)>0:
            return False, not_found
        return True, not_found

    def test_check_head_hw(self):
        """
        Check for issues in Head Dynamixels
        """
        self.assertTrue(os.path.exists('/dev/hello-dynamixel-head'), " FTDI Driver not found, try REx_discover_hello_devices.py or check Head Board")
        servo_ids = self.get_servo_ids('/dev/hello-dynamixel-head')
        self.test.log_data("head_dynamixel_ids_found", servo_ids)
        chk, not_present = self.check_elements(servo_ids, [11, 12]) 
        self.assertTrue(chk, f"Unable to find servos ids:{not_present} in head, check for damage in Dynamixel cables or Head Board")
    
    def test_check_wrist(self):
        """
        Check for issues in Wrist Dynamixels
        """
        self.assertTrue(os.path.exists('/dev/hello-wacc'), "Wacc Board not found, try REx_discover_hello_devices.py")
        self.assertTrue(os.path.exists('/dev/hello-dynamixel-wrist'), "FTDI Driver not found, try REx_discover_hello_devices.py or check wacc board")
        servo_ids = self.get_servo_ids('/dev/hello-dynamixel-wrist')
        self.test.log_data("wrist_dynamixel_ids_found", servo_ids)
        tool = RobotParams.get_params()[1]['robot']['tool']
        if tool == 'tool_stretch_dex_wrist':
            chk, not_present = self.check_elements(servo_ids, [13, 14, 15, 16]) 
        else:
            chk, not_present = self.check_elements(servo_ids, [13, 14]) 
        self.assertTrue(chk, f"Unable to find servos ids:{not_present} in wrist, check for damage in Dynamixel cables or Wacc Board")
        
        
test_suite = TestSuite(test=Test_DYNAMIXEL_hardware.test,failfast=False)
test_suite.addTest(Test_DYNAMIXEL_hardware('test_check_head_hw'))
test_suite.addTest(Test_DYNAMIXEL_hardware('test_check_wrist'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
