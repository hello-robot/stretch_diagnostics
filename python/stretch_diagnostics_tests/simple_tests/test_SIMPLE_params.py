#!/usr/bin/env python3

import unittest
import yaml
import os, fnmatch
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import stretch_body.hello_utils as hu
import stretch_body.version
import unittest
import serial
import fcntl
import glob
from os.path import exists

class Test_SIMPLE_params(unittest.TestCase):
    """
    Check system parameters and identify issues
    """
    test = TestBase('test_SIMPLE_params')


    def test_param_files_exist(self):
        """
        Check that the correct parameter files can be found.
        """
        v=stretch_body.version.__version__
        version_major=int(v.split('.')[0])
        version_minor=int(v.split('.')[1])
        if version_major==0 and version_minor<3:
            ue=exists(hu.get_fleet_directory() + 'stretch_re1_user_params.yaml')
            ce=exists(hu.get_fleet_directory() + 'stretch_re1_factory_params.yaml')
            self.assertTrue(ue,'Legacy parameter file stretch_re1_user_params.yaml missing on HELLO_FLEET_PATH')
            self.assertTrue(ce,'Legacy parameter files stretch_re1_factory_params.yaml missing on HELLO_FLEET_PATH')
        else:
            ue=exists(hu.get_fleet_directory() + 'stretch_user_params.yaml')
            ce=exists(hu.get_fleet_directory() + 'stretch_configuration_params.yaml')
            self.assertTrue(ue,'Parameter format upgrade may be required. For more details, see https://forum.hello-robot.com/t/425')
            self.assertTrue(ce,'Parameter format upgrade may be required. For more details, see https://forum.hello-robot.com/t/425')

    def test_params_log(self):
        """
        Log parameter data from stretch_params.
        """
        #Log stretch params
        fn = self.test.test_result_dir+'/stretch_params_%s.log'%self.test.timestamp
        os.system("stretch_params.py >> %s"%fn)
        print('Logged stretch_params.py to %s' % fn)
        #Copy over yaml files
        param_files_list= glob.glob(hu.get_fleet_directory()+'*.yaml')
        for p in param_files_list:
            fn_no_path=p[p.rfind('/'):]
            new_fn=fn_no_path+'_%s.log'%self.test.timestamp
            os.system("cp %s %s"%(p,self.test.test_result_dir+new_fn))
            print('Logged parameter settings to %s'%new_fn)


test_suite = TestSuite(test=Test_SIMPLE_params.test,failfast=False)
test_suite.addTest(Test_SIMPLE_params('test_param_files_exist'))
test_suite.addTest(Test_SIMPLE_params('test_params_log'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
