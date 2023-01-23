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
    Test USB Devices on Bus
    """
    test = TestBase('test_SIMPLE_steppers')
    test.add_hint('Possible issue with stepper at udev / hardware / driver level')
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
            if not calibrated:
                self.test.add_hint(('Encoder calibration not in flash for %s'%s))
                all_calibrated=False
            m.stop()
        self.test.log_data('encoder_calibrated',calibrated_log)
        self.assertTrue(all_calibrated,msg='One more more steppers missing encoder calibration in flash')

    def test_stepper_calibration_data_match(self):
        """
        Check that encoder calibration YAML matches what's in flash
        """
        all_match = True
        calibration_data_match_log = {}
        for s in self.steppers:
            if s=='hello-motor-lift':
                print()
                click.secho('Lift may drop. Place clamp under lift. Hit enter when ready', fg="yellow")
                input()
            m = stretch_body.stepper.Stepper(usb='/dev/' + s)
            self.assertTrue(m.startup(), msg='Not able to startup stepper %s' % s)
            print('Comparing flash data and encoder data for %s. This will take a minute...' % s)
            yaml_data=m.read_encoder_calibration_from_YAML()
            flash_data=m.read_encoder_calibration_from_flash()
            calibration_data_match_log[s]=(yaml_data == flash_data)
            if not calibration_data_match_log[s]:
                all_match = False
                self.test.add_hint('Encoder calibration in flash for %s does not match that in YAML. See REx_stepper_calibration_flash_to_YAML.py' % s)
        self.assertTrue(all_match, msg='Stepper calibration data is not consistent. Repair needed.')
        self.test.log_data('encoder_calibration_files', calibration_data_match_log)

    def test_stepper_calibration_files(self):
        """
        Check that encoder calibration data files are present and identical
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
            if not etc_exists:
                self.test.add_hint('Encoder calibration file missing: %s'%fn_etc)
            if not user_exists:
                self.test.add_hint('Encoder calibration file missing: %s'%fn_user)
            if not data_match:
                self.test.add_hint('Encoder calibration data files do not match: %s and %s' % (fn_etc,fn_user))
            self.assertTrue(user_exists,msg='Encoder calibration file %s not found'%fn_user)
            self.assertTrue(etc_exists,msg='Encoder calibration file %s not found'%fn_etc)
            #m.stop()
        self.test.log_data('encoder_calibration_files', calibration_data_log)


test_suite = TestSuite(test=Test_SIMPLE_steppers.test,failfast=False)
test_suite.addTest(Test_SIMPLE_steppers('test_steppers_present'))
test_suite.addTest(Test_SIMPLE_steppers('test_steppers_calibrated'))
test_suite.addTest(Test_SIMPLE_steppers('test_stepper_calibration_files'))
test_suite.addTest(Test_SIMPLE_steppers('test_stepper_calibration_data_match'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
