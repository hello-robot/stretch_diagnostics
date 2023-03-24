from colorama import Fore, Style
import os
import glob
import pkg_resources
import click
import pyrealsense2 as rs
import stretch_factory.hello_device_utils as hdu
import stretch_body.scope as scope
import time
import socket
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Lock
import zipfile
import matplotlib.pyplot as plt
from drawnow import drawnow


class Dmesg_monitor:
    """
    Run live dmesg fetching in the backgorund using threading. Query the collected dmesg message
    outputs or clear them in between sessions. Save the collected dmesg output at the end.

    TODO: add methods for filtered capturing of Dmesg

    Params
    ------
    print_new_msg =  Prints Dmesg live if True
    log_fn = Optional file path to save the log at stop of dmesg monitor

    """

    def __init__(self, print_new_msg=False, log_fn=None):
        self.prev_out = None
        self.thread = None
        self.output_list = []
        self.is_live = False
        self.lock = Lock()
        self.print_new_msg = print_new_msg
        self.log_fn = log_fn
        os.system("sudo echo ''")

    def dmesg_fetch_clear(self):
        out = Popen("sudo dmesg -c", shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True,
                    stderr=PIPE).stdout.read().decode("utf-8")
        out = str(out).split('\n')
        with self.lock:
            try:
                # Filter ghost lines
                if out[0] != self.prev_out[-1]:
                    for o in out:
                        if len(o) > 0:
                            self.output_list.append(o)
                            if self.print_new_msg:
                                print("[DMESG]...{}".format(o))
            except:
                pass
        self.prev_out = out

    def write_lines_to_file(self, lines, file_path):
        with open(os.path.expanduser(file_path), 'w') as file:
            for line in lines:
                file.write(line + '\n')
        print("DMESG Log saved to: {}".format(self.log_fn))

    def start(self):
        print("Starting DMESG capture....")
        self.is_live = True
        self.thread = Thread(target=self.live)
        self.thread.start()

    def stop(self):
        self.is_live = False
        self.thread.join()
        print("Ending DMESG capture....")
        if self.log_fn is not None:
            self.write_lines_to_file(self.output_list, self.log_fn)

    def live(self):
        while self.is_live:
            self.dmesg_fetch_clear()

    def clear(self):
        with self.lock:
            self.output_list = []

    def get_latest_msg(self):
        return self.prev_out

    def get_output_list(self):
        return self.output_list


class Scope_Sensor_vs_Sensor:
    """
    Scope two sensor values against eachother
    """

    def __init__(self, yrange, title='Scope'):
        plt.ion()  # enable interactivity
        self.fig = plt.figure()
        self.fig.canvas.set_window_title(title)
        plt.ylim(yrange[0], yrange[1])
        self.data_x = []
        self.data_y = []

    def step(self, sensor_value_x, sensor_value_y):
        self.data_x.append(sensor_value_x)
        self.data_y.append(sensor_value_y)
        drawnow(self.make_fig)

    def make_fig(self):
        plt.plot(self.data_x, self.data_y, 'b')

    def savefig(self, filename):
        plt.savefig(filename)


class Scope_Log_Sensor:
    """
    Scope a sensor value and save the figure to a PNG file.
    Optionally provide when callbacks to be called at some time after launch and before exiting
    Return if complete or not
    """

    def __init__(self, duration, y_range=[0, 100.0], title='Sensor', num_points=100, image_fn=None, start_fn=None,
                 start_fn_ts=None, end_fn=None, end_fn_ts=None, delay=0.1):

        self.ts_start = time.time()
        self.duration = duration
        self.data = []
        self.avg = None
        self.delay = delay
        self.image_fn = image_fn
        self.start_fn = start_fn
        self.start_fn_ts = start_fn_ts
        self.end_fn = end_fn
        self.end_fn_ts = end_fn_ts
        self.scope = scope.Scope(num_points=num_points, yrange=y_range, title=title)

    def step(self, sensor_value):
        dt = time.time() - self.ts_start
        if dt < self.duration:
            if self.start_fn_ts is not None and dt > self.start_fn_ts and self.start_fn is not None:
                self.start_fn()
                self.start_fn = None
            if self.end_fn_ts is not None and dt > self.end_fn_ts and self.end_fn is not None:
                self.end_fn()
                self.end_fn = None
            self.data.append(sensor_value)
            self.scope.step_display(sensor_value)
            time.sleep(self.delay)
            return True
        else:
            if self.image_fn is not None:
                print('Saving file %s' % self.image_fn)
                self.scope.savefig(self.image_fn)
                self.image_fn = None
            self.avg = sum(self.data) / len(self.data)
            return False


def get_installed_package_info(find_specific=None):
    packages = {}
    for package in pkg_resources.working_set:
        packages[package.key] = {"version": package.version,
                                 "path": package.location}
    if find_specific:
        return packages[find_specific]
    return packages


def extract_zip(zip_file_path, extract_to_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_path)


def val_in_range(val_name, val, vmin, vmax, silent=False):
    p = val <= vmax and val >= vmin
    if silent:
        return p
    if p:
        print(Fore.GREEN + '[Pass] ' + val_name + ' = ' + str(val))
        print(Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + '[Fail] ' + val_name + ' = ' + str(val) + ' out of range ' + str(vmin) + ' to ' + str(vmax))
        print(Style.RESET_ALL)
        return False


def val_is_not(val_name, val, vnot):
    if val is not vnot:
        print(Fore.GREEN + '[Pass] ' + val_name + ' = ' + str(val))
        return True
    else:
        print(Fore.RED + '[Fail] ' + val_name + ' = ' + str(val))
        return False


def confirm(question: str) -> bool:
    reply = None
    while reply not in ("y", "n"):
        reply = input(Style.BRIGHT + f"{question} (y/n): " + Style.RESET_ALL).lower()
    return (reply == "y")


def print_instruction(text, ret=0):
    return_text = Fore.BLUE + Style.BRIGHT + 'INSTRUCTION:' + Style.RESET_ALL + Style.BRIGHT + text + Style.RESET_ALL
    if ret == 1:
        return return_text
    else:
        print(return_text)


def print_bright(text):
    print(Style.BRIGHT + Fore.BLUE + text + Style.RESET_ALL)


def print_bright_red(text):
    print(Style.BRIGHT + Fore.RED + text + Style.RESET_ALL)


def system_check_warn(warning=None):
    def decorator(test_item):
        test_item.__system_check_warn__ = True
        test_item.__system_check_warning__ = warning
        return test_item

    return decorator


def command_list_exec(cmd_list):
    cmd = ''
    for c in cmd_list:
        cmd = cmd + c + ';'
    os.system(cmd)


def find_tty_devices():
    devices_dict = {}
    ttyUSB_dev_list = glob.glob('/dev/ttyUSB*')
    ttyACM_dev_list = glob.glob('/dev/ttyACM*')
    for d in ttyACM_dev_list:
        devices_dict[d] = {"serial": extract_udevadm_info(d, 'ID_SERIAL_SHORT'),
                           "vendor": extract_udevadm_info(d, 'ID_VENDOR'),
                           "model": extract_udevadm_info(d, 'ID_MODEL'),
                           "path": extract_udevadm_info(d, 'DEVPATH')}
    for d in ttyUSB_dev_list:
        devices_dict[d] = {"serial": extract_udevadm_info(d, 'ID_SERIAL_SHORT'),
                           "vendor": extract_udevadm_info(d, 'ID_VENDOR'),
                           "model": extract_udevadm_info(d, 'ID_MODEL'),
                           "path": extract_udevadm_info(d, 'DEVPATH')}
    return devices_dict


def get_serial_nos_from_udev(udev_file_full_path, device_name):
    sns = []
    try:
        f = open(udev_file_full_path, 'r')
        x = f.readlines()
        f.close()
        lines = []
        for xx in x:
            if xx.find(device_name) > 0 and xx[0] != '#':
                lines.append(xx)
        for l in lines:
            ll = l.split(',')
            for q in ll:
                if q.find('serial') > -1:
                    s = q[q.find('"') + 1:q.rfind('"')]
                    if len(s) == 8 or len(s) == 32:  # FTDI or Arduino
                        sns.append(s)
    except:
        pass
    return sns


def find_ftdi_devices_sn():
    devices_dict = {}
    ttyUSB_dev_list = glob.glob('/dev/ttyUSB*')
    for d in ttyUSB_dev_list:
        devices_dict[d] = extract_udevadm_info(d, 'ID_SERIAL_SHORT')
    return devices_dict


def find_arduino_devices_sn():
    devices_dict = {}
    ttyACM_dev_list = glob.glob('/dev/ttyACM*')
    for d in ttyACM_dev_list:
        devices_dict[d] = extract_udevadm_info(d, 'ID_SERIAL_SHORT')
    return devices_dict


def extract_udevadm_info(usb_port, ID_NAME=None):
    """
    Extracts usb device attributes with the given attribute ID_NAME

    example ID_NAME:
    ID_SERIAL_SHORT
    ID_MODEL
    DEVPATH
    ID_VENDOR_FROM_DATABASE
    ID_VENDOR
    """
    value = None
    dname = bytes(usb_port[5:], 'utf-8')
    out = hdu.exec_process([b'udevadm', b'info', b'-n', dname], True)
    if ID_NAME is None:
        value = out.decode(encoding='UTF-8')
    else:
        for a in out.split(b'\n'):
            a = a.decode(encoding='UTF-8')
            if "{}=".format(ID_NAME) in a:
                value = a.split('=')[-1]
    return value


def get_rs_details():
    """
    Returns the details of the first found realsense devices in the bus
    """
    dev = None
    ctx = rs.context()
    devices = ctx.query_devices()
    found_dev = False
    for dev in devices:
        if dev.get_info(rs.camera_info.serial_number):
            found_dev = True
            break
    if not found_dev:
        print('No RealSense device found.')
        return None

    data = {}
    data["device_pid"] = dev.get_info(rs.camera_info.product_id)
    data["device_name"] = dev.get_info(rs.camera_info.name)
    data["serial"] = dev.get_info(rs.camera_info.serial_number)
    data["firmware_version"] = dev.get_info(rs.camera_info.firmware_version)

    return data


def check_internet():
    try:
        socket.create_connection(("www.github.com", 80))
        return True
    except OSError:
        pass
    return False


def center_string(text, length=75, ch=' '):
    prefix_n = ((length - len(text)) // 2) - 1
    suffix_n = (length - len(text) - prefix_n) - 1
    return f"{ch * prefix_n} {text} {ch * suffix_n}"


def run_gist(gist_id):
    cmd = f"wget https://gist.githubusercontent.com/{gist_id}/raw/ --no-check-certificate"
    os.system(cmd)
    os.system("mv index.html misc_test.py")
    os.system("python3 misc_test.py")
    time.sleep(1)
    os.system("rm misc_test.py")
