#!/usr/bin/env python3

import os
import sys
import argparse
import time
import stretch_body.hello_utils as hu
from stretch_production_tools.production_test_manager import ProductionTestManager
from stretch_production_tools.production_test_utils import push_production_data, update_production_repo
from colorama import Fore,Style

hu.print_stretch_re_use()

parser = argparse.ArgumentParser(description='Script to run Bringup Tests Suite and generate system health reports.', )

parser.add_argument("--run", type=str, metavar='testname',
                    help='Run a Test with given name (E.g ./stretch_system_check.py --run test_BRI_audio)')

parser.add_argument("--status", help="Print the bringup status", action="store_true")
parser.add_argument("--run_menu", help="Run tests from command line menu", action="store_true")

parser.add_argument("--system_check", help="Get Last System Check Report", action="store_true")
parser.add_argument("--run_all", help="Run All BRI* Tests", action="store_true")

parser.add_argument("--push_data", help="Pushes stretch_production_data to git", action="store_true")
parser.add_argument("--list", type=int, metavar='verbosity', choices=[1, 2],nargs='?',
                    help="Lists all the available Bringup TestSuites and its included TestCases Ordered (Default verbosity=1)", const=1)

parser.add_argument("--update_data", help="Verify and Update Stretch Production Data repo", action="store_true")
parser.add_argument("--store_data", help="Push Stretch User data to stretch fleet", action="store_true")
parser.add_argument("--clean_up", help="Cleanup before ready to ship", action="store_true")

args = parser.parse_args()
test_name = None
production_repo = os.path.expanduser('~/repos/stretch_production_data')

if args.push_data:
    push_production_data()

if args.update_data:
    update_production_repo()

if not os.path.isdir(production_repo):
    print(Fore.YELLOW+'Unable to find stretch_production_data repo.'+Style.RESET_ALL)
    print("Please run './BRI_manager.py --update_data'")
    sys.exit()

if args.status:
    system_check = ProductionTestManager()
    system_check.print_status_report()

if args.run_menu:
    system_check = ProductionTestManager()
    system_check.run_menu()

if args.system_check:
    system_check = ProductionTestManager()
    system_check.generate_last_system_health_report()

if args.run_all:
    system_check = ProductionTestManager()
    system_check.run_all_test()

if args.store_data:
    os.system('~/repos/stretch_production_tools/python/bringup_tools/BRI_store_data.sh')

if args.clean_up:
    os.system('~/repos/stretch_production_tools/python/bringup_tools/BRI_cleanup_data.sh')

if args.run:
    test_name = args.run
    if test_name:
        system_check = ProductionTestManager()
        system_check.run_test(test_name)
    else:
        print('Provide a Test Name.')

if args.list:
    system_check = ProductionTestManager()
    all_tests_dict = system_check.list_ordered_production_tests(verbosity=int(args.list))

if not len(sys.argv) > 1:
    parser.error('No action requested. Please use one of the arguments listed above.')
