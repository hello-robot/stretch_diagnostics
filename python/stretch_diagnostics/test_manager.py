#!/usr/bin/env python3

import os
import sys

import yaml
from stretch_diagnostics.test_order import test_order
from colorama import Fore, Style
import importlib
from stretch_diagnostics.test_helpers import confirm
import stretch_body.hello_utils as hu
from stretch_diagnostics.test_runner import TestRunner
from stretch_diagnostics.test_helpers import command_list_exec, get_installed_package_info, center_string
import click
import glob
from zipfile import ZipFile


class TestManager():
    def __init__(self, test_type):
        self.next_test_ready = False
        self.test_type = test_type

        self.pkg_tests_path = '{}/stretch_diagnostics_tests/{}_tests'.format(
            get_installed_package_info('hello-robot-stretch-diagnostics')['path'], test_type)
        sys.path.append(self.pkg_tests_path)

        # Get Fleet ID
        self.fleet_id = os.environ['HELLO_FLEET_ID']

        results_directory = os.environ['HELLO_FLEET_PATH'] + '/log/diagnostic_check'
        self.test_timestamp = hu.create_time_string()
        self.tests_order = test_order[test_type]
        self.DiagnosticCheck_filename = 'diagnostic_check_%s_%s_%s.yaml' % (
            self.test_type, self.fleet_id, self.test_timestamp)
        self.results_directory = results_directory
        self.system_health_dict = {'total_tests': 0,
                                   'total_tests_failed': 0,
                                   'all_success': False,
                                   'check_timestamp': self.test_timestamp,
                                   'robot_name': self.fleet_id,
                                   'tests': None
                                   }
        self.disable_print_warning = False
        self.disable_print_error = False

    def get_TestModule(self, test_name):
        try:
            TestCase = importlib.import_module(test_name)
            return TestCase
        except ModuleNotFoundError:
            self.print_error('Unable to Load Test : {}'.format(test_name))
            return None

    def get_TestSuite(self, test_name):
        try:
            test_module = importlib.import_module(test_name)
            return test_module.test_suite
        except Exception as e:
            self.print_error('Unable to Load Test Suite: {}\n ERROR: {}'.format(test_name, e))
            return None

    def run_test(self, test_name):
        try:
            test_suite = self.get_TestSuite(test_name)
            runner = TestRunner(test_suite, False)
            runner.run()
            result = self.read_latest_test_result(test_name)
            del sys.modules[test_name]
            return result
        except Exception as e:
            self.print_error('Unable to Run Test: {} \n Error: {}'.format(test_name, e))
            return None

    def get_latest_files_with_extension(self, test_name, ext):
        # Retrieve the latest files of type test_name with extension ext
        # Not all tests will also generate a file of type ext
        try:
            list_of_files = []
            all_files = glob.glob(self.results_directory + '/' + test_name + '/' + '*.' + ext)
            unique_files = []
            for a in all_files:
                base = a[:a.rfind('_')]
                if not base in unique_files:
                    unique_files.append(base)
            for u in unique_files:
                all_files = glob.glob(u + '*.' + ext)
                all_files.sort()
                list_of_files.append(all_files[-1])
            return list_of_files
        except:
            return []

    def get_latest_test_result_filename(self, test_name):
        try:
            listOfFiles = glob.glob(self.results_directory + '/' + test_name + '/' + test_name + '*.yaml')
            listOfFiles.sort()
            return listOfFiles[-1]
        except Exception as e:
            # self.print_warning('{} result file not found'.format(test_name))
            return None

    def read_latest_test_result(self, test_name):
        try:
            listOfFiles = glob.glob(self.results_directory + '/' + test_name + '/' + test_name + '*.yaml')
            listOfFiles.sort()
            with open(listOfFiles[-1]) as f:
                result = yaml.safe_load(f)
            return result
        except Exception as e:
            self.print_warning('{} result not found or not performed'.format(test_name))
            return None

    def run_all_test(self):
        end = False
        i = 0
        while not end:
            choice, i = self.print_run_all_choices(i)
            if confirm('Run the Test {}'.format(Fore.CYAN + choice + Style.RESET_ALL)):
                print('\n')
                self.run_test(choice)
                print('\n\n')
            i = i + 1
            if i == len(self.tests_order) or i > len(self.tests_order):
                end = True
            print('---------------------------------------------------------\n')
        self.generate_last_system_health_report()

    def archive_all_tests_status(self):
        for test_name in self.tests_order:
            self.archive_test_status(test_name)

    def archive_test_status(self, test_name):
        wd = self.results_directory + '/' + test_name
        if not os.path.isdir(wd):
            return
        if not os.path.isdir(wd + '/archive'):
            os.system('mkdir {}/archive'.format(wd))
        command_list_exec(["cd {}".format(wd),
                           "find './' -maxdepth 1 -not -type d -exec mv -t 'archive/' -- '{}' +"])

    def run_suite(self):
        for t in self.tests_order:
            self.run_test(t)

    def run_menu(self, show_subtests=False):
        while True:
            self.print_status_report(show_subtests)
            print(Style.BRIGHT + '############### MENU ################' + Style.RESET_ALL)
            print('Enter test # to run (q to quit)')
            print('A: archive tests')
            print('-------------------------------------')
            try:
                r = input()
                if r == 'q' or r == 'Q':
                    return
                elif r == 'A':
                    self.archive_all_tests_status()
                    print('Resetting All Tests')
                    print('-------------------------------------')
                else:
                    n = int(r)
                    if 0 <= n < len(self.tests_order):
                        test_name = self.tests_order[n]
                        print('Running test: %s' % test_name)
                        print('')
                        self.run_test(test_name)
                        print('########### TEST COMPLETE ##########\n')
                    else:
                        print('Invalid entry')
            except(TypeError, ValueError):
                print('Invalid entry')

    def print_run_all_choices(self, test_i):
        print('---------------------------------------------------------\n')
        print(Style.BRIGHT + 'Choose an action from the list:')
        print(
            '[0]  RUN TEST = [{}. {}]'.format(test_i + 1, Fore.CYAN + self.tests_order[test_i] + Fore.RESET))
        if not test_i == 0:
            print('[1]  RE-RUN PREVIOUS TEST = [{}. {}]'.format(test_i, self.tests_order[test_i - 1]))
        print('[2]  ABORT HEALTH TEST' + Style.RESET_ALL)
        choice = input('Enter the Choice:\n')
        if choice == '0':
            return self.tests_order[test_i], test_i
        elif choice == '1':
            if not test_i == 0:
                return self.tests_order[test_i - 1], test_i - 1
            else:
                return self.print_run_all_choices(test_i)
        elif choice == '2':
            print('ABORTING HEALTH TEST.....')
            sys.exit()
        else:
            return self.print_run_all_choices(test_i)

    def print_subtests_status(self,result):
        for stest in result['test_status']['subtests_status'].keys():
            description = result['test_status']['subtests_status'][stest]['description']
            status = result['test_status']['subtests_status'][stest]['status']
            if status == 'PASS':
                description = self.set_subtests_descripton(result, stest, status)
                click.secho(f"\t\t[{status}] {stest}: {description}", fg="green")
            else:
                description = self.set_subtests_descripton(result,stest,status)
                click.secho(f"\t\t[{status}] {stest}: {description}", fg="red")

    def set_subtests_descripton(self, result, stest, status):
        description = result['test_status']['subtests_status'][stest]['description']

        if status == 'FAIL':
            def parse_traceback(tb):
                assertion_line = tb[-2]
                tbl = assertion_line.split(':')
                if len(tbl) > 3:
                    return f"{tbl[-2]}:{tbl[-1]}"
                return tbl[-1]

            for item in result['FAILS']:
                k = list(item.keys())[0]
                if k == stest:
                    description = description + f"\n\t\t\tfailure: {parse_traceback(item[k])}"
            for item in result['ERRORS']:
                k = list(item.keys())[0]
                if k == stest:
                    description = description + f"\n\t\t\terror: {parse_traceback(item[k])}"
        elif status == 'PASS':
            pass
        return description

    def print_status_report(self,show_subtests=False):
        self.disable_print_warning = True
        self.disable_print_error = True
        i = 0
        for test_name in self.tests_order:
            result = self.read_latest_test_result(test_name)
            if not result:
                print(click.style('[%d] %s: Test result: N/A' % (i, test_name), fg="yellow", bold=True))
            elif result['test_status']['status'] != 'SUCCESS':
                print(click.style('[%d] %s: Test result: FAIL' % (i, test_name,), fg="red", bold=True))
                if show_subtests:
                    self.print_subtests_status(result)
            else:
                print(click.style('[%d] %s: Test result: PASS' % (i, test_name), fg="green", bold=True))
                if show_subtests:
                    self.print_subtests_status(result)
            i = i + 1
        self.disable_print_warning = False
        self.disable_print_error = False

    def generate_latest_zip_file(self, zip_file=None):

        if zip_file is None:
            zip_file = self.results_directory + '/diagnostic_check_%s_%s.zip' % (self.fleet_id, self.test_timestamp)

        # Pass in a zip file to append new tests

        files_to_zip = [self.results_directory + '/' + self.DiagnosticCheck_filename]
        rel_path_directory = 'diagnostic_'
        files_rel_path = [self.DiagnosticCheck_filename]

        for test_name in self.tests_order:
            fn = self.get_latest_test_result_filename(test_name)
            lfn = self.get_latest_files_with_extension(test_name, 'log')
            ifn = self.get_latest_files_with_extension(test_name, 'png')
            if (fn):
                files_to_zip.append(fn)
                files_rel_path.append(fn.split('/')[-2] + '/' + fn.split('/')[-1])
            for l in lfn:
                files_to_zip.append(l)
                files_rel_path.append(l.split('/')[-2] + '/' + l.split('/')[-1])
            for i in ifn:
                files_to_zip.append(i)
                files_rel_path.append(i.split('/')[-2] + '/' + i.split('/')[-1])
        try:
            with ZipFile(zip_file, 'a') as z:
                for file, fn_path in zip(files_to_zip, files_rel_path):
                    print('Adding: %s' % file)
                    z.write(file, fn_path)
        except FileNotFoundError:
            self.print_error("Unable zip the file {}".format(zip_file))
        return zip_file

    def generate_last_diagnostic_report(self, silent=False):
        tests_results_collection = []
        total_fail = 0
        total_tests = len(self.tests_order)
        total_tests_ran = 0
        all_success = True
        for test_name in self.tests_order:
            result = self.read_latest_test_result(test_name)
            if (result):
                result_status = result['test_status']
                tests_results_collection.append({test_name: result_status})
                if result_status['status'] != 'SUCCESS':
                    total_fail = total_fail + 1
                total_tests_ran = total_tests_ran + 1
        self.system_health_dict['tests'] = tests_results_collection
        self.system_health_dict['total_tests'] = total_tests
        self.system_health_dict['total_tests_ran'] = total_tests_ran
        self.system_health_dict['total_tests_failed'] = total_fail
        if total_tests_ran == 0:
            if not silent:
                self.print_error('Zero Tests were Ran.')
                print(Fore.RED)
            self.system_health_dict['all_success'] = False
        elif total_fail == 0:
            if not silent:
                print(Fore.GREEN)
            self.system_health_dict['all_success'] = True
        else:
            if not silent:
                print(Fore.YELLOW)
        try:
            with open(self.results_directory + '/' + self.DiagnosticCheck_filename, 'w') as file:
                documents = yaml.dump(self.system_health_dict, file)
        except FileNotFoundError:
            self.print_error(
                "Unable to find file {}".format(self.results_directory + '/' + self.DiagnosticCheck_filename))
        if not silent:
            print('\n\n')
            print('Last Diagnostic Report:')
            print('================================')
            print(yaml.dump(self.system_health_dict))
            print('\nReported {} Fails.'.format(total_fail))
            print(Style.RESET_ALL)
            print('Diagnostic Check Saved to : {}'.format(self.results_directory + '/' + self.DiagnosticCheck_filename))

        return self.system_health_dict

    def list_ordered_tests(self, verbosity=1):
        all_tests_dict = {}
        txt = "Printing Orderded TestSuites  for %s and it's included Sub-TestCases" % self.test_type.upper()
        print(Style.BRIGHT + txt)
        print('-' * len(txt) + '\n' + Style.RESET_ALL)
        for i in range(len(self.tests_order)):
            test_name = self.tests_order[i]
            all_tests_dict[test_name] = {}
            test_suite = self.get_TestSuite(test_name)
            if test_suite:
                sub_tests = test_suite._tests
                if not len(sub_tests):
                    self.print_warning('Unable Discover tests added to {}.test_suite'.format(test_name))
                else:
                    cls_doc = sub_tests[0].__doc__
                    if cls_doc:
                        cls_doc = cls_doc.strip()
                        if verbosity == 2:
                            print('  ' + cls_doc)
                        all_tests_dict[test_name]['Description'] = cls_doc
                    else:
                        if verbosity == 2:
                            self.print_warning('Test Class level Doc missing.')
                    for j in range(len(sub_tests)):
                        sub_test_name = sub_tests[j].id().split('.')[-1]
                        all_tests_dict[test_name][sub_test_name] = {'Description': None}
                        if verbosity == 1 or verbosity == 2:
                            print('  {} {}'.format('-', sub_test_name))
                        sub_test_description = sub_tests[j].shortDescription()
                        if sub_test_description:
                            all_tests_dict[test_name][sub_test_name] = {'Description': sub_test_description}
                            if verbosity == 2:
                                print('       {}'.format(sub_test_description))
                        else:
                            if verbosity == 2:
                                self.print_warning('Short Description not provided.', 7)

        all_test_list_ordereded = []
        for test_name in self.tests_order:
            all_test_list_ordereded.append({test_name: all_tests_dict[test_name]})

        return all_test_list_ordereded

    def print_warning(self, text, indent=0):
        if not self.disable_print_warning:
            e = '[WARNING]:'
            print(' ' * indent + Fore.YELLOW + e + text + Style.RESET_ALL)

    def print_error(self, text, indent=0):
        if not self.disable_print_error:
            e = '[ERROR]:'
            print(' ' * indent + Fore.RED + e + text + Style.RESET_ALL)
