#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import unittest
import stretch_factory.hello_device_utils as hdu
import stretch_body.dynamixel_hello_XL430
import stretch_body.dynamixel_XL430
class Test_SIMPLE_dynamixel_configure(unittest.TestCase):
    """
    Test Dynamixel device basic functionality
    """
    test = TestBase('test_SIMPLE_dynamixel_configure')
    devices=['hello-dynamixel-head','hello-dynamixel-wrist']
    joints=['head_tilt','head_pan','wrist_yaw','stretch_gripper']
    def test_device_present(self):
        """
        Check that Dynamixel devices are present
        """
        for d in self.devices:
            dh=hdu.is_device_present('/dev/'+d)
            self.assertTrue(dh,msg='Device %s not on bus. May be UDEV or hardware issue.'%d)

    def test_identify_baud(self):
        "Check that baud rates are set correctly"
        baud_id={'head_pan':{},'head_tilt':{},'wrist_yaw':{},'stretch_gripper':{}}
        baud_id['head_pan']['identified']=stretch_body.dynamixel_XL430.DynamixelXL430.identify_baud_rate(11,'/dev/hello-dynamixel-head')
        baud_id['head_tilt']['identified'] = stretch_body.dynamixel_XL430.DynamixelXL430.identify_baud_rate(12,'/dev/hello-dynamixel-head')
        baud_id['wrist_yaw']['identified'] = stretch_body.dynamixel_XL430.DynamixelXL430.identify_baud_rate(13,'/dev/hello-dynamixel-wrist')
        baud_id['stretch_gripper']['identified'] = stretch_body.dynamixel_XL430.DynamixelXL430.identify_baud_rate(14,'/dev/hello-dynamixel-wrist')

        for j in self.joints:
            servo=stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name=j, chain=None)
            baud_id[j]['params']=servo.params['baud']
            msg='Baud mismmatch for %s. YAML param is %d and servo is set to %d'%(j,baud_id[j]['params'],baud_id[j]['identified'])
            self.assertTrue(baud_id[j]['params'] == baud_id[j]['identified'],msg=msg)
        self.test.log_data('baud_identification', baud_id)

    def test_servo_ping(self):
        "Ping the primary Dynamixel servos"
        ping={}
        for j in self.joints:
            servo = stretch_body.dynamixel_hello_XL430.DynamixelHelloXL430(name=j, chain=None)
            st=servo.startup()
            self.assertTrue(st,'Unable to startup %s'%j)
            ping[j]=servo.do_ping()
            self.assertTrue(ping[j], msg='Failed to ping servo %s'%j)
        self.test.log_data('servo_pinged', ping)


test_suite = TestSuite(test=Test_SIMPLE_dynamixel_configure.test,failfast=False)
test_suite.addTest(Test_SIMPLE_dynamixel_configure('test_device_present'))
test_suite.addTest(Test_SIMPLE_dynamixel_configure('test_servo_ping'))
test_suite.addTest(Test_SIMPLE_dynamixel_configure('test_identify_baud'))
if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
