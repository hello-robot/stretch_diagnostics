#!/usr/bin/env python3

import sys
import argparse
import stretch_body.hello_utils as hu
from stretch_wellness.test_manager import TestManager
from stretch_wellness.test_order import test_order
from colorama import Style

hu.print_stretch_re_use()

parser = argparse.ArgumentParser(description='Script to run Wellness Test Suite and generate reports.', )
parser.add_argument("--report", help="Report the latest wellness check", action="store_true")
parser.add_argument("--simple", help="Run test suite: SIMPLE", action="store_true")

args = parser.parse_args()

def print_report(suite_names=None):
    if suite_names is None:
        suite_names=test_order.keys()
    for t in suite_names:
        print(Style.BRIGHT + '############################## %s ###############################'%t.upper() + Style.RESET_ALL)
        system_check = TestManager(test_type=t)
        system_check.print_status_report()
        print('')
if args.report:
    print_report()

if args.simple:
    mgmt = TestManager(test_type='simple')
    mgmt.run_suite()

if not len(sys.argv) > 1:
    parser.error('No action requested. Please use one of the arguments listed above.')
