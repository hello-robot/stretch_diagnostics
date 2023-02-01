#!/usr/bin/env python3

import sys
import argparse
import stretch_body.hello_utils as hu
from stretch_diagnostics.test_manager import TestManager
from stretch_diagnostics.test_order import test_order
from colorama import Style

hu.print_stretch_re_use()

parser = argparse.ArgumentParser(description='Script to run Diagnostic Test Suite and generate reports.', )
parser.add_argument("--report", help="Report the latest diagnostic check", action="store_true")
parser.add_argument("--zip", help="Generate zip file of latest diagnostic check", action="store_true")
parser.add_argument("--archive", help="Archive old diagnostic test data", action="store_true")
parser.add_argument("--menu", help="Run tests from command line menu", action="store_true")
parser.add_argument("--list", type=int, metavar='verbosity', choices=[1, 2], nargs='?',
                    help="Lists all the available TestSuites and its included TestCases Ordered (Default verbosity=1)",
                    const=1)

group = parser.add_mutually_exclusive_group()
group.add_argument("--simple", help="Run simple diagnostics across entire robot", action="store_true")
group.add_argument("--power", help="Run diagnostics on the power subsystem", action="store_true")
group.add_argument("--realsense", help="Run diagnostics on the Intel RealSense D435 camera", action="store_true")
group.add_argument("--stepper", help="Run diagnostics on stepper drivers", action="store_true")
group.add_argument("--firmware", help="Run diagnostics on robot firmware versions", action="store_true")
group.add_argument("--dynamixel", help="Run diagnostics on all robot Dynamixel servos", action="store_true")
group.add_argument("--gripper", help="Run diagnostics on the gripper subsystem", action="store_true")
group.add_argument("--all", help="Run all diagnostics", action="store_true")

args = parser.parse_args()


def print_report(suite_names=None):
    if suite_names is None:
        suite_names = test_order.keys()
    for t in suite_names:
        print(Style.BRIGHT + '####################### %s TESTS #######################' % t.upper() + Style.RESET_ALL)
        system_check = TestManager(test_type=t)
        system_check.print_status_report()
        print('')


def run_test_type(test_type):
    mgmt = TestManager(test_type=test_type)
    if args.menu:
        mgmt.run_menu()
    else:
        mgmt.run_suite()


if args.menu and len(sys.argv) < 3:
    print("The '--menu' tag must be provided with a test type. E.g. stretch_diagnostics_check.py --menu --simple")
    exit()

if args.menu and args.all:
    print("The `--menu` tag cannot be used with `--all` test type.")
    exit()

if (args.list and len(sys.argv) < 3) or (args.list and sys.argv[-1] == 'list'):
    print("The '--list' tag must be prefixed by a test type (E.g. stretch_diagnostics_check.py --simple --list)")
    exit()


if args.archive:
    for t in test_order.keys():
        mgmt = TestManager(test_type=t)
        mgmt.archive_all_tests_status()
    print('Archvied all diagnostic data under: %s' % mgmt.results_directory)

if args.zip:
    print(
        Style.BRIGHT + '############################## Zipping Latest Results ###############################' + Style.RESET_ALL)
    zip_file = None
    for t in test_order.keys():
        mgmt = TestManager(test_type=t)
        mgmt.generate_last_diagnostic_report(silent=True)
        zip_file = mgmt.generate_latest_zip_file(zip_file=zip_file)
    print('\n----------- Complete -------------')
    print('Zip file available at: %s' % zip_file)

if args.report:
    print(Style.BRIGHT + '############################## SUMMARY ###############################\n')
    # mgmt = TestManager(test_type='simple')
    # mgmt.generate_last_diagnostic_report()
    print_report()

if args.all:
    for t in test_order.keys():
        if args.list:
            print("\n")
            mgmt = TestManager(test_type=t)
            mgmt.list_ordered_tests(verbosity=int(args.list))
        else:
            run_test_type(t)

if args.simple:
    if args.list:
        mgmt = TestManager(test_type='simple')
        mgmt.list_ordered_tests(verbosity=int(args.list))
    else:
        run_test_type('simple')

if args.power:
    if args.list:
        mgmt = TestManager(test_type='power')
        mgmt.list_ordered_tests(verbosity=int(args.list))
    else:
        run_test_type('power')

if args.dynamixel:
    if args.list:
        mgmt = TestManager(test_type='dynamixel')
        mgmt.list_ordered_tests(verbosity=int(args.list))
    else:
        run_test_type('dynamixel')

if args.gripper:
    if args.list:
        mgmt = TestManager(test_type='gripper')
        mgmt.list_ordered_tests(verbosity=int(args.list))
    else:
        run_test_type('gripper')

if args.stepper:
    if args.list:
        mgmt = TestManager(test_type='stepper')
        mgmt.list_ordered_tests(verbosity=int(args.list))
    else:
        run_test_type('stepper')

if not len(sys.argv) > 1:
    parser.error('No action requested. Please use one of the arguments listed above.')
