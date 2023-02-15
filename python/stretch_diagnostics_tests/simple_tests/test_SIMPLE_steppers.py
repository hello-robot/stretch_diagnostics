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
import  click

class Test_SIMPLE_steppers(unittest.TestCase):
    """
    Test Stepper basic configuration
    """
    test = TestBase('test_SIMPLE_steppers')
    steppers = ['hello-motor-right-wheel','hello-motor-left-wheel','hello-motor-arm','hello-motor-lift']

    def test_steppers_present(self):
        """
        Check that steppers are present
        """
        for s in self.steppers:
            self.assertTrue(hdu.is_device_present('/dev/'+s),msg='Stepper %s not found on USB bus'%s)
    
    def test_steppers_calibrated(self):
        """
        Check that steppers have encoder calibration
        """
        all_calibrated=True
        calibrated_log={}
        for s in self.steppers:
            m=stretch_body.stepper.Stepper(usb='/dev/'+s)
            self.assertTrue(m.startup(),msg='Not able to startup stepper %s'%s)
            m.pull_status()
            calibrated=m.status['calibration_rcvd']
            calibrated_log[s]=calibrated
            self.assertTrue(calibrated,'Encoder calibration not in flash for %s'%s)
            m.stop()
        self.test.log_data('encoder_calibrated',calibrated_log)


    def test_stepper_calibration_files(self):
        """
        Check that encoder calibration is present in stretch_user and etc (and they match)
        """
        calibration_data_log = {}
        for s in self.steppers:
            m = stretch_body.stepper.Stepper(usb='/dev/' + s)
            fn_encoder_calibration = m.name+'_'+m.params['serial_no']+'.yaml'
            fn_user=hu.get_fleet_directory()+'calibration_steppers/'+fn_encoder_calibration
            fn_etc ='/etc/hello-robot/'+hu.get_fleet_id()+'/calibration_steppers/'+fn_encoder_calibration
            etc_exists=os.path.exists(fn_etc)
            user_exists=os.path.exists(fn_user)
            data_match=False
            if etc_exists and user_exists:
                e=hu.enc_data=hu.read_fleet_yaml(fn_etc)
                u = hu.enc_data = hu.read_fleet_yaml(fn_user)
                data_match=(e==u)
            calibration_data_log[s]={'etc_file_exists':etc_exists,'user_file_exists':user_exists,'file_data_match':data_match}
            self.assertTrue(etc_exists,'Encoder calibration file missing: %s'%fn_etc)
            self.assertTrue(user_exists,'Encoder calibration file missing: %s'%fn_user)
            self.assertTrue(data_match,'Encoder calibration data files do not match: %s and %s' % (fn_etc,fn_user))

            #m.stop()
        self.test.log_data('encoder_calibration_files', calibration_data_log)


test_suite = TestSuite(test=Test_SIMPLE_steppers.test,failfast=False)
test_suite.addTest(Test_SIMPLE_steppers('test_steppers_present'))
test_suite.addTest(Test_SIMPLE_steppers('test_steppers_calibrated'))
test_suite.addTest(Test_SIMPLE_steppers('test_stepper_calibration_files'))


if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
