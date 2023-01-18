
"""
This Librabry consists of all the test_BRI_* test suite names listed and ordered.
The dictionary "test_order" should have all the robot batch specific test lists.
"""

test_order = {}

test_order['mitski'] = {'bringup':[
    #Subs test tagged with a SN
    # 'SUBS_LIFT_CYCLE_INSERTION_FORCE',
    # 'SUBS_LIFT_MEASURE_INSERTION_FORCE',
    'test_BRI_discover_hello_devices',
    #Do simple tests first, no motion
    'test_BRI_usb_devices_on_bus',
    'test_BRI_realsense',
    'test_BRI_steppers_pull_calibration',
    'test_BRI_firmware_update',
    'test_BRI_audio',
    'test_BRI_light_bar',
    'test_BRI_rp_lidar_jog',
    'test_BRI_monitor_test',
    #
    #  Do calibrations, no motion
    'test_BRI_pimu_calibrate',
    'test_BRI_wacc_calibrate',
    #
    # #Do simple motions
    'test_BRI_head_jog',
    'test_BRI_wrist_yaw_home',
    'test_BRI_gripper_home',
    'test_BRI_arm_home',
    'test_BRI_lift_home',
    'test_BRI_base_jog',
    #
    # #Multi joint tests
    'test_BRI_robot_home_stow',
    'test_BRI_runstop_test',
    #
    # #Joint calibrations, simple
    'test_BRI_head_pan_phase',
    'test_BRI_dynamixel_calibrate_range',
    'test_BRI_arm_calibrate_range',
    'test_BRI_lift_calibrate_range',
    'test_BRI_base_imu_calibrate',
    'test_BRI_gripper_zero_calibration',
    #
    # #Joint calibrations, complex
    'test_BRI_base_wheel_separation',
    'test_BRI_arm_break_in',
    'test_BRI_arm_calibrate_guarded_contact',
    'test_BRI_lift_break_in',
    'test_BRI_lift_calibrate_guarded_contact',
    #
    # #Full system checks
    'test_BRI_robot_hardware_echo',
    'test_BRI_robot_system_check'
],
'eol':[
    'test_EOL_arm_wrist_yaw',
    'test_EOL_arm_home',
    'test_EOL_arm_break_in',
    'test_EOL_arm_calibrate_guarded_contact',
    'test_EOL_arm_calibrate_range',
    'test_EOL_arm_sticker',
    'test_EOL_head_pan',
    'test_EOL_head_runstop',
    'test_EOL_head_audio',
    'test_EOL_head_sticker',
    'test_EOL_lift_present',
    'test_EOL_lift_home',
    'test_EOL_lift_break_in',
    'test_EOL_lift_calibrate_guarded_contact',
    'test_EOL_lift_sticker',
],
'rdk':[
    'test_RDK_servo_id',
    'test_RDK_pimu_flash',
    'test_RDK_pimu_jog'
]}

test_order['nina'] = {'bringup':[
    #Subs test tagged with a SN
    # 'SUBS_LIFT_CYCLE_INSERTION_FORCE',
    # 'SUBS_LIFT_MEASURE_INSERTION_FORCE',
    'test_BRI_discover_hello_devices',
    #Do simple tests first, no motion
    'test_BRI_usb_devices_on_bus',
    'test_BRI_realsense',
    'test_BRI_steppers_pull_calibration',
    'test_BRI_firmware_update',
    'test_BRI_audio',
    'test_BRI_light_bar',
    'test_BRI_rp_lidar_jog',
    'test_BRI_monitor_test',
    #
    #  Do calibrations, no motion
    'test_BRI_pimu_calibrate',
    'test_BRI_wacc_calibrate',
    #
    # #Do simple motions
    'test_BRI_head_jog',
    'test_BRI_wrist_yaw_home',
    'test_BRI_gripper_home',
    'test_BRI_arm_home',
    'test_BRI_lift_home',
    'test_BRI_base_jog',
    #
    # #Multi joint tests
    'test_BRI_robot_home_stow',
    'test_BRI_runstop_test',
    #
    # #Joint calibrations, simple
    'test_BRI_head_pan_phase',
    'test_BRI_dynamixel_calibrate_range',
    'test_BRI_arm_calibrate_range',
    'test_BRI_lift_calibrate_range',
    'test_BRI_base_imu_calibrate',
    'test_BRI_gripper_zero_calibration',
    #
    # #Joint calibrations, complex
    'test_BRI_base_wheel_separation',
    'test_BRI_arm_break_in',
    'test_BRI_arm_calibrate_guarded_contact',
    'test_BRI_lift_break_in',
    'test_BRI_lift_calibrate_guarded_contact',
    #
    # #Full system checks
    'test_BRI_robot_hardware_echo',
    'test_BRI_robot_system_check'
],
'eol':[
    'test_EOL_arm_wrist_yaw',
    'test_EOL_arm_home',
    'test_EOL_arm_break_in',
    'test_EOL_arm_calibrate_guarded_contact',
    'test_EOL_arm_calibrate_range',
    'test_EOL_arm_sticker',
    'test_EOL_head_pan',
    'test_EOL_head_runstop',
    'test_EOL_head_audio',
    'test_EOL_head_sticker',
    'test_EOL_lift_present',
    'test_EOL_lift_home',
    'test_EOL_lift_break_in',
    'test_EOL_lift_calibrate_guarded_contact',
    'test_EOL_lift_sticker',
],
'rdk':[
    'test_RDK_servo_id',
    'test_RDK_pimu_flash',
    'test_RDK_pimu_jog'
]}

test_order['re1'] = {'bringup':[
    #Subs test tagged with a SN
    # 'SUBS_LIFT_CYCLE_INSERTION_FORCE',
    # 'SUBS_LIFT_MEASURE_INSERTION_FORCE',

    #Do simple tests first, no motion
    'test_BRI_usb_devices_on_bus',
    'test_BRI_realsense',
    'test_BRI_steppers_pull_calibration',
    'test_BRI_firmware_update',
    'test_BRI_audio',
    'test_BRI_rp_lidar_jog',
    'test_BRI_monitor_test',
    #
    #  Do calibrations, no motion
    'test_BRI_pimu_calibrate',
    'test_BRI_wacc_calibrate',
    #
    # #Do simple motions
    'test_BRI_head_jog',
    'test_BRI_wrist_yaw_home',
    'test_BRI_gripper_home',
    'test_BRI_arm_home',
    'test_BRI_lift_home',
    'test_BRI_base_jog',
    #
    # #Multi joint tests
    'test_BRI_robot_home_stow',
    'test_BRI_runstop_test',
    #
    # #Joint calibrations, simple
    'test_BRI_head_pan_phase',
    'test_BRI_dynamixel_calibrate_range',
    'test_BRI_arm_calibrate_range',
    'test_BRI_lift_calibrate_range',
    'test_BRI_base_imu_calibrate',
    'test_BRI_gripper_zero_calibration',
    #
    # #Joint calibrations, complex
    'test_BRI_base_wheel_separation',
    'test_BRI_arm_break_in',
    'test_BRI_arm_calibrate_guarded_contact',
    'test_BRI_lift_break_in',
    'test_BRI_lift_calibrate_guarded_contact',
    #
    # #Full system checks
    'test_BRI_robot_hardware_echo',
    'test_BRI_robot_system_check'
],
'eol':[
    'test_EOL_arm_wrist_yaw',
    'test_EOL_arm_home',
    'test_EOL_arm_break_in',
    'test_EOL_arm_calibrate_guarded_contact',
    'test_EOL_arm_calibrate_range',
    'test_EOL_arm_sticker',
    'test_EOL_head_pan',
    'test_EOL_head_runstop',
    'test_EOL_head_audio',
    'test_EOL_head_sticker',
    'test_EOL_lift_present',
    'test_EOL_lift_home',
    'test_EOL_lift_break_in',
    'test_EOL_lift_calibrate_guarded_contact',
    'test_EOL_lift_sticker',
],
'rdk':[
    'test_RDK_servo_id',
    'test_RDK_pimu_flash',
    'test_RDK_pimu_jog'
]}




















#################### Params List for Reference ###########################
bringup_params_mitski={
'BRI_REALSENSE_TEST':  {'firmware_version': '05.13.0.50'},
'BRI_PIMU_CALIBRATE':{
  'cliff_zero_min': 480,
  'cliff_zero_max': 570,
  'az_min': -12.0,
  'az_max': -8.0,
  'voltage_min': 10.5,
  'voltage_max': 14.5,
  'i_min': 0.5,
  'i_max': 3.5,
  'temp_min': 20.0,
  'temp_max': 38.0,
  'pitch_roll_min': -12.0,
  'pitch_roll_max': 12.0},
'BRI_WACC_CALIBRATE':{
  'accel_gravity_scale_max': 1.1,
  'accel_gravity_scale_min': 0.9},
'BRI_ARM_CALIBRATE_RANGE':{'range_max': 0.521, 'range_min': 0.515},
'BRI_LIFT_CALIBRATE_RANGE':{'range_max': 1.101, 'range_min': 1.097},
'BRI_BASE_IMU_CALIBRATE':{'foo': 0},
'BRI_STEPPERS_PULL_CALIBRATION':{'foo': 0},
'BRI_GRIPPER_ZERO_CALIBRATION':{'min_ticks': 7000},
'BRI_ARM_CALIBRATE_GUARDED_CONTACT':{
  'offset_out': -0.002,
  'offset_in': .002,
  'nominal_force_out_N': 70.0,
  'nominal_force_in_N': -70,
  'margin_N': 15.0,
  'within_nominal_N': 5.0},
'BRI_LIFT_BREAK_IN':{'ncycles': 50},
'BRI_ARM_BREAK_IN':{'ncycles': 50},
'BRI_LIFT_CALIBRATE_GUARDED_CONTACT':{
  'offset_top': -0.001,
  'offset_bottom': .001,
  'nominal_force_up_N': 80.0,
  'nominal_force_down_N': -80,
  'margin_N': 15.0,
  'within_nominal_N': 5.0},
'BRI_BASE_WHEEL_SEPARATION':{
  'max_wheel_separation_m': 0.325,
  'min_wheel_separation_m': 0.310},
'SUBS_LIFT_CYCLE_INSERTION_FORCE':{
  'offset_top': -0.001,
  'offset_bottom': .02,
  'nominal_force_up_N': 65.0,
  'nominal_force_down_N': -55,
  'within_nominal_N': 5.0,
  'arm_force_offset': 20.0,
  'ncycle': 100},
'SUBS_LIFT_MEASURE_INSERTION_FORCE':{
  'offset_top': -0.001,
  'offset_bottom': .001,
  'nominal_force_up_N': 80.0,
  'nominal_force_down_N': -80,
  'margin_N': 15.0,
  'within_nominal_N': 5.0},
}

