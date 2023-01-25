
"""
This Librabry consists of all the test_* test suite names listed and ordered.
The dictionary "test_order" should have all the robot batch specific test lists.
"""

test_order= {
    'simple':[
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
        'test_SIMPLE_dynamixel_configure'
        ],
    'power':[
        'test_POWER_charger',
        'test_POWER_battery_loading'
        ],

}

