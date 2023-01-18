import unittest
import time
import os
import stretch_body.hello_utils as hu
import yaml
from colorama import Fore, Style
import sys
import stretch_production_tools.fleet_definition as fd
from subprocess import Popen, PIPE
import subprocess
from stretch_production_tools.helpers import confirm, print_instruction, print_bright,print_bright_red
import git
import stretch_factory.hello_device_utils as hdu
import glob
import pyrealsense2 as rs

class Production_Test():
    def __init__(self, test_name, test_type=None, results_directory=None):
        self.user_info = get_user_metadata()
        print(Style.BRIGHT + '{}'.format(test_name))
        print('=' * len(test_name) + Style.RESET_ALL)

        self.timestamp = hu.create_time_string()
        self.test_name = test_name
        self.fleet_id = os.environ['HELLO_FLEET_ID']
        self.production_repo = os.path.expanduser('~/repos/stretch_production_data')

        # Set up Results Directory
        if test_type == 'rdk':
            results_directory = os.path.expanduser(self.production_repo + '/rdk/'+os.environ['HELLO_PRODUCTION_TOOLS_BATCH_NAME'])
        if test_type == 'eol':
            results_directory = os.path.expanduser(self.production_repo + '/robots/' + self.fleet_id)
        if results_directory is None:
            results_directory = os.path.expanduser(self.production_repo + '/robots/' + self.fleet_id) # Default test type is 'bringup' which stores results robot specific

        os.system('mkdir -p %s' % results_directory)
        self.results_directory = results_directory
        self.results_directory_test_specific = self.results_directory + '/' + test_name

        self.params_dict = {}
        self.data_dict = {}
        self.test_status = {}

        self.result_data_dict = {'params': None,
                                 'test_status': None,
                                 'data': None,
                                 'FAILS': None,
                                 'ERRORS': None}
        self.check_test_results_directories()

    def check_test_results_directories(self):
        # self.update_production_repo()
        if not os.path.isdir(self.results_directory):
            os.system('mkdir -p {}'.format(self.results_directory))
        self.test_result_dir = '{}/{}'.format(self.results_directory, self.test_name)

        if not os.path.isdir(self.results_directory):
            os.system('mkdir -p {}'.format(self.test_result_dir))

        self.test_file_dir = '{}/{}'.format(self.results_directory, self.test_name)
        if not os.path.isdir(self.test_file_dir):
            os.system('mkdir -p {}'.format(self.test_file_dir))

    def save_test_result(self, test_status=None):
        """
        This function forces the practice of unit tests to produce result dict with the three fields
        """
        self.result_data_dict['test_status'] = test_status
        self.result_data_dict['params'] = self.params_dict
        self.result_data_dict['data'] = self.data_dict
        self.result_data_dict['user_info'] = self.user_info
        print(yaml.dump(self.result_data_dict['test_status']))
        print('Checking stretch_production_data.....')
        self.check_test_results_directories()
        test_file_name = self.test_name + '_' + self.timestamp + '.yaml'
        filename = self.test_file_dir + '/' + test_file_name
        with open(filename, 'w') as file:
            documents = yaml.dump(self.result_data_dict, file)
        print('Test data saved to : {}'.format(filename))

    def log_params(self, key, value):
        self.params_dict[key] = value

    def log_data(self, key, value):
        self.data_dict[key] = value

    def log_fails(self, failures):
        self.result_data_dict['FAILS'] = self.parse_TestErrors(failures)

    def log_errors(self, errors):
        self.result_data_dict['ERRORS'] = self.parse_TestErrors(errors)

    def parse_TestErrors(self, failures):
        fails = []
        for f in failures:
            test_id = str(f[0].id())
            out = str(f[1])
            out_lines = out.split('\n')
            fails.append({test_id: out_lines})
        return fails

    def save_TestResult(self, result):
        ok = result.wasSuccessful()
        errors = result.errors
        failures = result.failures
        if ok:
            print(Fore.GREEN)
            print('All Test Cases passed')
            self.save_test_result(test_status={'status': 'SUCCESS',
                                               'errors': len(errors),
                                               'failures': len(failures)})
            print(Style.RESET_ALL)
        else:
            print(Fore.RED)
            print('{} errors and {} failures so far'.format(len(errors), len(failures)))
            self.log_errors(errors)
            self.log_fails(failures)
            self.save_test_result(test_status={'status': 'FAIL',
                                               'errors': len(errors),
                                               'failures': len(failures)})
            print(Style.RESET_ALL)

    def move_misc_file(self, file_key, filename):
        ff = filename.split('.')

        filename_ts = ff[0] + '_' + self.timestamp + '.' + ff[-1]
        os.system('mv {} {}/{}/{}'.format(filename, self.results_directory, self.test_name, filename_ts))
        self.log_data(file_key, filename_ts)


class Production_TestResult(unittest.runner.TextTestResult):
    def startTest(self, test):
        super(Production_TestResult, self).startTest(test)
        print('\n')
        test_id = test.id().split('.')[-1]
        print(test_id)
        print('-' * len(test_id))
        if test.shortDescription():
            print('Description:\n' + test.shortDescription() + '\n')
        else:
            print(Fore.YELLOW + "[WARNING]: Description Missing for test: {}".format(test_id) + Style.RESET_ALL)

    def stopTest(self, test):
        super(Production_TestResult, self).stopTest(test)
        result = test.defaultTestResult()
        test._feedErrorsToResult(result, test._outcome.errors)
        ok = result.wasSuccessful()
        errors = result.errors
        failures = result.failures

        if ok:
            print(Fore.GREEN)
            print('Test Case passed')
            print(Style.RESET_ALL)
        else:
            print(Fore.RED)
            print('Test Case Failed')
            print('{} errors and {} failures'.format(len(errors), len(failures)))
            print(Style.RESET_ALL)


class Production_TestSuite(unittest.TestSuite):
    def __init__(self, production_test=None, failfast=False):
        super().__init__(self)
        self.include_production_test(production_test)
        self.failfast = failfast

    def include_production_test(self, prd_test):
        self.production_test = prd_test
        if not self.production_test:
            print(Fore.YELLOW + 'Creating Test Suite Without Production Test' + Style.RESET_ALL)


class Production_TestRunner(unittest.TextTestRunner):
    resultclass = Production_TestResult

    def __init__(self, suite, doc_verify_fail=False):
        super(Production_TestRunner, self).__init__()
        self.failfast = suite.failfast
        self.suite = suite
        self.doc_verify_fail = doc_verify_fail

    def _suite_verify_doc_fail(self):
        doc_check_fail = False
        if len(self.suite._tests) == 0:
            print(Fore.YELLOW + '[SYSTEM CHECK ERROR]: A test suite must have at least one test\n' + Style.RESET_ALL)
            doc_check_fail = True

        if len(self.suite._tests):
            class_doc = self.suite._tests[0].__doc__
            if class_doc is None:
                print(
                    Fore.YELLOW + '[SYSTEM CHECK ERROR]: A test case must have a class-level docstring' + Style.RESET_ALL)
                doc_check_fail = True

            for t in self.suite._tests:
                if not t.shortDescription():
                    print(Fore.YELLOW + '[SYSTEM CHECK ERROR]: Short Description not provided for test : {}'.format(
                        t.id()) + Style.RESET_ALL)
                    doc_check_fail = True

        return doc_check_fail

    def run(self):
        if self.doc_verify_fail:
            if self._suite_verify_doc_fail():
                print(Fore.RED + 'Stopping Test Run' + Style.RESET_ALL)
                return
        result = super(Production_TestRunner, self).run(self.suite)
        # result = super().run(self.suite)
        if self.suite.production_test:
            self.suite.production_test.save_TestResult(result)
        else:
            print(
                Fore.YELLOW + '[WARNING]: Result Data not saved because Production Object was not included with Test Suite.')
            print(
                'Add production_test object while initializing  "test_suite = Production_TestSuite(Test_XXX_foo.proudction_test)" ' + Style.RESET_ALL)
        return result


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


def push_production_data():
    update_production_repo()
    print('Pushing Production Data at stretch_production_data repo')
    cmd_list = [
        'cd {}'.format(os.path.expanduser('~/repos/stretch_production_data')),
        'git pull',
        'git add .',
        'git commit -m "Pushing {} Production data"'.format(os.environ['HELLO_FLEET_ID']),
        'git push'
    ]
    command_list_exec(cmd_list)


def update_production_repo():
    production_repo = os.path.expanduser('~/repos/stretch_production_data')
    if os.path.isdir(production_repo):
        print(Fore.GREEN + 'Found stretch_production_data repo.' + Style.RESET_ALL)
        os.system('cd ~/repos/stretch_production_data;git pull')
    else:
        print(Fore.YELLOW + 'Unable to find stretch_production_data repo.' + Style.RESET_ALL)
        if (confirm('Pull stretch_production_data repository?')):
            print('Fetching stretch_production_repo...')
            os.system(
                'cd ~/repos;git clone https://github.com/hello-robot/stretch_production_data')


def get_user_metadata():
    repo = git.Repo.init(os.path.expanduser('~/repos/stretch_production_tools'))
    try:
        reader = repo.config_reader()
        user_name = reader.get_value("user", "name")
        user_email = reader.get_value("user", "email")

        return {'user_name': user_name,
                'user_email': user_email}

    except Exception as e:
        print(Fore.YELLOW + 'Unable to Find a GIT User info.' + Fore.RESET)
        user_name = input("Enter a user's name: ")
        user_email = input("Enter a user's email: ")
        repo.config_writer().set_value("user", "name", user_name).release()
        repo.config_writer().set_value("user", "email", user_email).release()
        return get_user_metadata()


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


def burn_bootloader(sketch):
    print_bright('------------------------ Burning bootlader ------------------------')
    cmdl = ['arduino-cli', 'burn-bootloader', '-b', 'hello-robot:samd:%s' % sketch, '-P', 'sam_ice']
    sub = subprocess.Popen(cmdl, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sub.communicate(input=None)
    returncode = sub.returncode
    if returncode==0:
        return True
    else:
        print_bright_red('Bootloader failed to burn')
        print_bright_red('Check that red and green LEDs are on')
        print_bright_red('Double-click reset button if bootloader already present')
        x=stderr.decode('utf-8').split('\n')
        print('------------------------------')
        for i in range(len(x)):
            print(x[i])
        print('------------------------------')
        return False


def compile_arduino_firmware(sketch_name, repo_path):
    """
    :param sketch_name: eg 'hello_stepper'
    :return T if success:
    """
    print_bright('------------------------ Compile Arduino Firmware {} ------------------------'.format(sketch_name))
    compile_command = 'arduino-cli compile --fqbn hello-robot:samd:%s %s/arduino/%s' % (sketch_name, repo_path, sketch_name)
    print(compile_command)
    c = Popen(compile_command, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip()
    return c.find(b'Sketch uses') > -1


def burn_arduino_firmware(port, sketch_name,repo_path):
    print_bright('------------------------ Flashing firmware %s | %s ------------------------' % (port, sketch_name))
    port_name = Popen("ls -l " + port, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().split()[-1]
    port_name=port_name.decode("utf-8")
    if port_name is not None:
        upload_command = 'arduino-cli upload -p %s --fqbn hello-robot:samd:%s %s/arduino/%s' % (port_name, sketch_name,repo_path, sketch_name)
        print('Running: %s'%upload_command)
        u = Popen(upload_command, shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip()
        uu = u.split(b'\n')
        #Pretty print the result
        for l in uu:
            k=l.split(b'\r')
            if len(k)==1:
                print(k[0].decode('utf-8'))
            else:
                for m in k:
                    print(m.decode('utf-8'))
        print('################')
        success=uu[-1]==b'CPU reset.'
        if not success:
            print('Firmware flash. Failed to upload to %s'% ( port))
            return False
        else:
            print('Success in firmware flash')
        return True
    else:
        print('Firmware flash. Failed to find device %s' % ( port))
        return False

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
    data["device_pid"] =  dev.get_info(rs.camera_info.product_id)
    data["device_name"] = dev.get_info(rs.camera_info.name)
    data["serial"] = dev.get_info(rs.camera_info.serial_number)
    data["firmware_version"] = dev.get_info(rs.camera_info.firmware_version)

    return data