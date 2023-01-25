#!/usr/bin/env python3
from stretch_diagnostics.test_helpers import val_in_range
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_suite import TestSuite
import stretch_factory.hello_device_utils as hdu
from stretch_body.dynamixel_XL430 import DynamixelXL430, DynamixelCommError
import unittest
from stretch_body.robot_params import RobotParams
import glob


class Test_SIMPLE_accessories(unittest.TestCase):
    """
    Test to verify if the Stretch Accessories param configuration match the found HW devices
    """
    test = TestBase('test_SIMPLE_accessories')

    def test_check_tool_config(self):
        """
        Pull Stretch robot configuration details from params
        """
        robot_tool = RobotParams.get_params()[1]['robot']['tool']
        robot_model = RobotParams.get_params()[1]['robot']['model_name']
        robot_batch = RobotParams.get_params()[1]['robot']['batch_name']
        self.test.log_data('robot_tool', robot_tool)
        self.test.log_data('robot_model', robot_model)
        self.test.log_data('robot_batch', robot_batch)

        print("Found robot tool config: {}".format(robot_tool))
        print("Found robot model config: {}".format(robot_model))
        print("Found robot batch config: {}".format(robot_batch))

    def test_verify_params(self):
        """
        Verify if the stretch robot tool configuration matches the recommended stretch params
        """
        ref_params = None
        standard_gripper_yaml_RE2V0 = {
            'params': [],
            'lift': {'i_feedforward': 1.2},
            'hello-motor-lift': {'gains': {'i_safety_feedforward': 1.2}}}
        standard_gripper_yaml_RE1V0 = {
            'params': [],
            'lift': {'i_feedforward': 0.54},
            'hello-motor-lift': {'gains': {'i_safety_feedforward': 0.4}}}
        dex_wrist_yaml_RE1V0 = {
            'params': ['stretch_tool_share.stretch_dex_wrist.params'],
            'lift': {'i_feedforward': 0.75},
            'hello-motor-lift': {'gains': {'i_safety_feedforward': 0.75}}}
        dex_wrist_yaml_RE2V0 = {
            'params': ['stretch_tool_share.stretch_dex_wrist.params'],
            'lift': {'i_feedforward': 1.8},
            'hello-motor-lift': {'gains': {'i_safety_feedforward': 1.8}}}

        if self.test.data_dict['robot_tool'] == 'tool_stretch_gripper' and self.test.data_dict[
            'robot_model'] == 'RE1V0':
            ref_params = standard_gripper_yaml_RE1V0
            self.test.add_hint(
                "Checkout Stretch wrist tool guide https://docs.hello-robot.com/0.2/stretch-hardware-guides/docs/dex_wrist_guide_re1/")
        elif self.test.data_dict['robot_tool'] == 'tool_stretch_dex_wrist' and self.test.data_dict[
            'robot_model'] == 'RE1V0':
            ref_params = dex_wrist_yaml_RE1V0
            self.test.add_hint(
                "Checkout stretch wrist tool guide https://docs.hello-robot.com/0.2/stretch-hardware-guides/docs/dex_wrist_guide_re1/")
        elif self.test.data_dict['robot_tool'] == 'tool_stretch_gripper' and self.test.data_dict[
            'robot_model'] == 'RE2V0':
            ref_params = standard_gripper_yaml_RE2V0
            self.test.add_hint(
                "Checkout stretch wrist tool guide https://docs.hello-robot.com/0.2/stretch-hardware-guides/docs/dex_wrist_guide_re2/")
        elif self.test.data_dict['robot_tool'] == 'tool_stretch_dex_wrist' and self.test.data_dict[
            'robot_model'] == 'RE2V0':
            ref_params = dex_wrist_yaml_RE1V0
            self.test.add_hint(
                "Checkout stretch wrist tool guide https://docs.hello-robot.com/0.2/stretch-hardware-guides/docs/dex_wrist_guide_re2/")
        self.assertIsNotNone(ref_params, "Unable to identify the right stretch tool configuration")
        self.test.log_params('correct_params', ref_params)

        _params = []
        try:
            _params = RobotParams.get_params()[1]['params']
        except KeyError:
            _params = []
        self.assertEqual(ref_params['params'], _params, "'params' dont match")

        _lift_i_feedforward = RobotParams.get_params()[1]['lift']['i_feedforward']
        self.assertEqual(ref_params['lift']['i_feedforward'], _lift_i_feedforward,
                         "Lift i_feedforward value does not match.")

        _hello_motor_lift_i_safety_feedforward = RobotParams.get_params()[1]['hello-motor-lift']['gains'][
            'i_safety_feedforward']
        self.assertEqual(ref_params['hello-motor-lift']['gains']['i_safety_feedforward'],
                         _hello_motor_lift_i_safety_feedforward,
                         "hello-motor-lift safety i_feedforward value does not match.")

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

    def test_check_wrist_dynamixels(self):
        dev_list = glob.glob('/dev/hello-dynamixel-*')
        print("Found Servo IDs: {}".format(dev_list))
        self.assertEqual(len(dev_list), 2, "Unable to find all hello-dynamixel-* devices")
        self.assertTrue('/dev/hello-dynamixel-wrist' in dev_list, "Unable to find device: /dev/hello-dynamixel-wrist")
        found_ids = self.get_servo_ids(port='/dev/hello-dynamixel-wrist')
        self.test.log_data('found_servo_ids', found_ids)
        if self.test.data_dict['robot_tool'] == 'tool_stretch_dex_wrist':
            self.assertEqual(len(found_ids), 4, "Unable to find the all the servos")
        if self.test.data_dict['robot_tool'] == 'tool_stretch_gripper':
            self.assertEqual(len(found_ids), 2, "Unable to find the all the servos")


test_suite = TestSuite(test=Test_SIMPLE_accessories.test, failfast=False)
test_suite.addTest(Test_SIMPLE_accessories('test_check_tool_config'))
test_suite.addTest(Test_SIMPLE_accessories('test_verify_params'))
test_suite.addTest(Test_SIMPLE_accessories('test_check_wrist_dynamixels'))

if __name__ == '__main__':
    runner = TestRunner(test_suite)
    runner.run()
