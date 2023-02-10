
"""
This Library consists of all the test_* test suite names listed and ordered.
The dictionary "test_order" should have all the robot batch specific test lists.
"""

test_order= {
    'simple':[
        'test_SIMPLE_wifi',
        'test_SIMPLE_params',
        'test_SIMPLE_stretch_body_background',
        'test_SIMPLE_usb_devices_on_bus',
        'test_SIMPLE_udev',
        'test_SIMPLE_realsense_status',
        'test_SIMPLE_pimu',
        'test_SIMPLE_wacc',
        'test_SIMPLE_rplidar',
        'test_SIMPLE_steppers',
        'test_SIMPLE_firmware',
        'test_SIMPLE_dynamixel_configure',
        'test_SIMPLE_accessories',
        'test_SIMPLE_software_packages',
        'test_SIMPLE_filesystem',
        'test_SIMPLE_capture_system'
        ],
    'power':[
        'test_POWER_charger',
        'test_POWER_battery_loading'
        ],
    'cpu':['test_CPU_usage_temp'],
    'ros':[
        'test_ROS_sourced_distro',
        'test_ROS_calibration',
        'test_ROS_urdf'
        ],
    'dynamixel':[
        'test_DYNAMIXEL_measure_efforts',
        'test_DYNAMIXEL_measure_range_of_motion',
        'test_DYNAMIXEL_check_zero_position'
        ],
    'gripper':[
        'test_GRIPPER_broken_string',
        ],
     'stepper':[
         'test_STEPPER_calibration_data_match',
         'test_STEPPER_runstop',
         'test_STEPPER_sync'
         ],
    'arm':['test_ARM_effort_through_range_of_motion'],
    'lift': ['test_LIFT_effort_through_range_of_motion'],
    'realsense':[
        'test_REALSENSE_cable',
        'test_REALSENSE_frame_rate'
    ],
}
