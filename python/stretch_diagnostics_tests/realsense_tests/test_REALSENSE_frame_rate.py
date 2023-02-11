#!/usr/bin/env python3
import unittest
from stretch_diagnostics.test_base import TestBase
from stretch_diagnostics.test_suite import TestSuite
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_helpers import Dmesg_monitor, get_rs_details
from colorama import Fore, Style
from subprocess import Popen, PIPE, STDOUT
import time
import numpy as np
import click
import stretch_body.robot
import subprocess
from tabulate import tabulate

# Enter each stream's pass fps rate
streams_assert = {'Depth': 29, 'Color': 29, 'Gyro': 199, 'Accel': 62}  # Refer create_config_target_*


def create_config_target_hi_res():
    f = open('/tmp/d435i_confg.cfg', "w+")
    config_script = ["DEPTH,1280,720,30,Z16,0",
                     "COLOR,1920,1080,30,RGB8,0",
                     "ACCEL,1,1,63,MOTION_XYZ32F",
                     "GYRO,1,1,200,MOTION_XYZ32F"]

    header = ["STREAM", "WIDTH", "HEIGHT", "FPS", "FORMAT", "STREAM_INDEX"]
    config_data = []
    for ll in config_script:
        f.write(ll + "\n")
        config_data.append(ll.split(','))
    config_table = str(tabulate(config_data, headers=header, tablefmt='github')).split('\n')

    f.close()
    target = {'duration': 31,
              'nframe': 900,
              'margin': 16,
              'streams': {
                  'Color': {'target': 900, 'sampled': 0},
                  'Depth': {'target': 900, 'sampled': 0},
                  'Accel': {'target': 900, 'sampled': 0},
                  'Gyro': {'target': 900, 'sampled': 0}}}
    return target


def create_config_target_low_res():
    f = open('/tmp/d435i_confg.cfg', "w+")
    config_script = ["DEPTH,424,240,30,Z16,0",
                     "COLOR,424,240,30,RGB8,0",
                     "ACCEL,1,1,63,MOTION_XYZ32F",
                     "GYRO,1,1,200,MOTION_XYZ32F"]

    header = ["STREAM", "WIDTH", "HEIGHT", "FPS", "FORMAT", "STREAM_INDEX"]
    config_data = []
    for ll in config_script:
        f.write(ll + "\n")
        config_data.append(ll.split(','))
    config_table = str(tabulate(config_data, headers=header, tablefmt='github')).split('\n')

    f.close()
    target = {'duration': 31,
              'nframe': 900,
              'margin': 16,
              'streams': {
                  'Color': {'target': 900, 'sampled': 0},
                  'Depth': {'target': 900, 'sampled': 0},
                  'Accel': {'target': 900, 'sampled': 0},
                  'Gyro': {'target': 900, 'sampled': 0}}}
    return target


known_msgs = [[0, 30, 'uvcvideo: Failed to query (GET_CUR) UVC control'],
              [0, 15, 'Non-zero status (-71) in video completion handler'],
              [0, 15, 'No report with id 0xffffffff found'],
              [0, 10, 'uvcvideo: Found UVC 1.50 device Intel(R) RealSense(TM) Depth Camera 435'],
              [0, 5, 'uvcvideo: Unable to create debugfs'],
              [0, 4, 'hid-sensor-hub'],
              [0, 6, 'input: Intel(R) RealSense(TM) Depth Ca'],
              [0, 1, 'uvcvideo: Failed to resubmit video URB (-1).'],
              [0, 1, 'Netfilter messages via NETLINK v0.30.'],
              [0, 1, 'USB disconnect']]


def get_frame_id_from_log_line(stream_type, line):
    if line.find(stream_type) != 0:
        return None
    return int(line.split(',')[2])


def get_rs_data(target):
    cmd = 'rs-data-collect -c /tmp/d435i_confg.cfg -f /tmp/d435i_log.csv -t %d -m %d' % (
        target['duration'], target['nframe'])
    out = Popen(cmd, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().decode("utf-8")
    ff = open('/tmp/d435i_log.csv')
    data = ff.readlines()
    data = data[10:]  # drop preamble
    return data


def get_fps(data, stream, t):
    timestamps = []
    for ll in data:
        tag = stream + ',' + t
        if tag in ll:
            l = ll.split(',')[-1].split('\n')[0]
            if stream == 'Accel' or stream == 'Gyro':
                l = ll.split(',')[-4].split('\n')[0]
            timestamp = float(l) / 1000
            timestamps.append(timestamp)
    if len(timestamps) > 1:
        duration = timestamps[-1] - timestamps[0]
        avg_fps = len(timestamps) / duration
        return avg_fps
    else:
        return 000.0


def check_FPS(data):
    fps_dict = {}
    for s in streams_assert.keys():
        fps = get_fps(data, s, '0')
        fps_dict[s] = fps
        if fps > streams_assert[s]:
            print(Fore.GREEN + '[Pass] %s Rate : %f FPS' % (s, fps) + Style.RESET_ALL)
        else:
            print(Fore.RED + '[Fail] %s Rate : %f FPS < %d FPS' % (s, fps, streams_assert[s]) + Style.RESET_ALL)
    return fps_dict


def check_frames_collected(data, target):
    frames_n_dict = {}
    for ll in data:
        for kk in target['streams'].keys():
            id = get_frame_id_from_log_line(kk, ll)
            if id is not None:
                target['streams'][kk]['sampled'] = max(id, target['streams'][kk]['sampled'])
    for kk in target['streams'].keys():
        sampled_frames = target['streams'][kk]['sampled']
        min_frames = target['streams'][kk]['target'] - target['margin']
        frames_n_dict[kk] = {'sampled_frames': sampled_frames, 'min_frames': min_frames}
        if sampled_frames >= min_frames:
            print(Fore.GREEN + '[Pass] Stream: %s with %d frames collected' % (kk, sampled_frames))
        else:
            print(Fore.RED + '[Fail] Stream: %s with %d frames of %d collected' % (kk, sampled_frames, min_frames))
    print(Style.RESET_ALL)
    return frames_n_dict


class Test_REALSENSE_frame_rate(unittest.TestCase):
    """
    Testing the frame rate capture performance of realsense
    """

    # test object is always expected within a TestCase Class
    test = TestBase('test_REALSENSE_frame_rate')
    test.add_hint("Realsense frame rate issues can sometimes be solved by relasense drivers reinstall or firmware "
                  "update.")

    @classmethod
    def setUpClass(self):
        dmesg_log_fn = "{}/{}_{}.log".format(self.test.results_directory_test_specific,
                                             "dmesg",
                                             self.test.timestamp)
        self.dmesg = Dmesg_monitor(print_new_msg=True, log_fn=dmesg_log_fn)
        self.dmesg.start()

    @classmethod
    def tearDownClass(self):
        self.dmesg.stop()
        print("\nCollected DMESG")
        print("---------------")
        for l in self.dmesg.output_list:
            print(l)

    def test_USB3_2_connection(self):
        """
        Check that Realsense camera is on USB3.2 connection
        """
        out = Popen("rs-enumerate-devices| grep Usb | grep 3.2", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                    close_fds=True).stdout.read()

        if len(out):
            print('Confirmed USB 3.2 connection to realsense device')
        else:
            self.add_hint('Did not find USB 3.2 connection to realsense device')
        self.assertIsNot(len(out), 0, msg='Did not find USB 3.2 connection to realsense device')

    def test_realsense_on_usb_bus(self):
        """
        Check that Realsense camera is on USB bus.
        """
        print('---- Checking for Intel D435i ----')
        cmd = "lsusb -d 8086:0b3a"
        returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
        if returned_value != 0:
            self.test.add_hint('Realsense D435i not found at USB Bus')
        self.assertEqual(returned_value, 0)

    def test_realsense_details(self):
        """
        Capture realsense details and log
        """
        d = get_rs_details()
        if d is None:
            self.test.add_hint('Not able to launch Realsense driver. It may be conflicting with ROS')
        self.assertIsNotNone(d)
        self.test.log_data('realsense_details', d)

    def test_get_realsense_drivers_info(self):
        """
        Collect realsense driver information
        """
        driver_info = {}

        fw_details = Popen("rs-fw-update -l | grep -i 'firmware'", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                           close_fds=True).stdout.read().decode()
        fw_details = fw_details.split(',')[3]
        fw_version = fw_details.split(' ')[-1]
        driver_info['fw_version'] = fw_version

        nuc_bios_version = Popen("sudo dmidecode -s bios-version", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                                 close_fds=True).stdout.read().decode().rstrip()
        system_version = Popen("sudo dmidecode -s system-version", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                               close_fds=True).stdout.read().decode().rstrip()
        baseboard_version = Popen("sudo dmidecode -s baseboard-version", shell=True, bufsize=64, stdin=PIPE,
                                  stdout=PIPE, close_fds=True).stdout.read().decode().rstrip()
        processor_version = Popen("sudo dmidecode -s processor-version", shell=True, bufsize=64, stdin=PIPE,
                                  stdout=PIPE, close_fds=True).stdout.read().decode().rstrip()
        kernel_version = Popen("uname -r", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE,
                               close_fds=True).stdout.read().decode().rstrip()

        driver_info['nuc_bios_version'] = nuc_bios_version
        driver_info['system_version'] = system_version
        driver_info['baseboard_version'] = baseboard_version
        driver_info['processor_version'] = processor_version
        driver_info['firmware_vekernel_versionrsion'] = kernel_version

        # check_install_v4l2()
        print('\nD435i Firmware version: %s\n' % (fw_version))
        print("Linux Kernel Version : %s" % (kernel_version))
        print("NUC Bios Version : %s" % (nuc_bios_version))
        print("NUC System Version : %s" % (system_version))
        print("NUC Baseboard Version : %s" % (baseboard_version))
        print("Processor Version : %s" % (processor_version))
        self.test.log_data('system_info', driver_info)

    def test_frame_rate_high_res(self):
        """
        Check the frames collected and frame rate achieved while collecting high res rs data
        """
        target = create_config_target_hi_res()
        self.test.log_params("high_res_config", target)

        print("Collecting High res data from realsense......")
        data = get_rs_data(target)
        frames_collected = check_frames_collected(data, target)
        fps_dict = check_FPS(data)
        self.test.log_data("high_res_frames_collected", frames_collected)
        self.test.log_data("high_res_frame_rates", fps_dict)

        for kk in frames_collected.keys():
            self.assertGreaterEqual(frames_collected[kk]['sampled_frames'], frames_collected[kk]['min_frames'])
        for s in streams_assert.keys():
            self.assertGreater(fps_dict[s], streams_assert[s])

    def test_frame_rate_low_res(self):
        """
        Check the frames collected and frame rate achieved while collecting low res rs data
        """
        target = create_config_target_low_res()
        self.test.log_params("high_res_config", target)

        print("Collecting Low res data from realsense......")
        data = get_rs_data(target)
        frames_collected = check_frames_collected(data, target)
        fps_dict = check_FPS(data)
        self.test.log_data("low_res_frames_collected", frames_collected)
        self.test.log_data("low_res_frame_rates", fps_dict)

        for kk in frames_collected.keys():
            self.assertGreaterEqual(frames_collected[kk]['sampled_frames'], frames_collected[kk]['min_frames'])
        for s in streams_assert.keys():
            self.assertGreater(fps_dict[s], streams_assert[s])

    def check_dmesg(self, msgs):
        unknown_msgs = []
        excessive_msgs = []
        unexpected_msgs = []
        no_error = True
        for m in msgs:
            if len(m):
                found = False
                for i in range(len(known_msgs)):
                    if m.find(known_msgs[i][2]) != -1:
                        found = True
                        known_msgs[i][0] = known_msgs[i][0] + 1
                if not found:
                    unknown_msgs.append(m)
        for i in range(len(known_msgs)):
            if known_msgs[i][0] >= known_msgs[i][1]:
                print(Fore.YELLOW + '[Warning] Excessive dmesg warnings (%d) of: %s' % (
                    known_msgs[i][0], known_msgs[i][2]))
                excessive_msgs.append(known_msgs[i][2])
                no_error = False
        if len(unknown_msgs):
            print('[Warning] Unexpected dmesg warnings (%d)' % len(unknown_msgs))
            unexpected_msgs = unknown_msgs
            no_error = False
            for i in unknown_msgs:
                print(i)
        if no_error:
            print(Fore.GREEN + '[Pass] No unexpected dmesg warnings')
        print(Style.RESET_ALL)
        self.test.log_data("excessive_dmesgs", excessive_msgs)
        self.test.log_data("unexpected_dmesgs", unexpected_msgs)
        self.assertTrue(no_error, "Errors captured in DMESGs.")

    def test_check_dmesgs(self):
        """
        Check Dmesg output errors
        """
        self.check_dmesg(self.dmesg.get_output_list())


test_suite = TestSuite(test=Test_REALSENSE_frame_rate.test, failfast=False)
test_suite.addTest(Test_REALSENSE_frame_rate('test_USB3_2_connection'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_realsense_on_usb_bus'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_get_realsense_drivers_info'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_realsense_details'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_frame_rate_high_res'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_frame_rate_low_res'))
test_suite.addTest(Test_REALSENSE_frame_rate('test_check_dmesgs'))

if __name__ == '__main__':
    runner = TestRunner(suite=test_suite, doc_verify_fail=False)
    runner.run()
