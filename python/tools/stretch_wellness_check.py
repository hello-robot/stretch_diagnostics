#!/usr/bin/env python3

import sys
import argparse
import stretch_body.hello_utils as hu
from stretch_system_health.test_manager import HealthTestManager

hu.print_stretch_re_use()

parser = argparse.ArgumentParser(description='Script to run Health Tests Suite and generate reports.', )
parser.add_argument("--latest", help="Print the latest wellness check", action="store_true")
parser.add_argument("--run", help="Run tests from command line menu", action="store_true")


args = parser.parse_args()

if args.latest:
    system_check = HealthTestManager()
    system_check.print_status_report()

if args.run:
    system_check = HealthTestManager()
    system_check.run_menu()

if not len(sys.argv) > 1:
    parser.error('No action requested. Please use one of the arguments listed above.')
