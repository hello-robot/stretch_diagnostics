#!/usr/bin/env python3

import sys
import argparse
import stretch_body.hello_utils as hu
from stretch_wellness.test_manager import TestManager

hu.print_stretch_re_use()

parser = argparse.ArgumentParser(description='Script to run Wellness Test Suite and generate reports.', )
parser.add_argument("--latest", help="Print the latest wellness check", action="store_true")
parser.add_argument("--simple", help="Run test suite: SIMPLE", action="store_true")


args = parser.parse_args()

if args.latest:
    system_check = TestManager()
    system_check.print_status_report()

if args.simple:
    mgmt = TestManager(test_type='simple')
    mgmt.run_suite()

if not len(sys.argv) > 1:
    parser.error('No action requested. Please use one of the arguments listed above.')
