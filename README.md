# Deprecation Notice
This repo is has been replaced by CLIs in [Stretch Body](https://github.com/hello-robot/stretch_body) (the low level interface for the Stretch robots). In particular, the `stretch_system_check.py` CLI is the recommended starting point for confirming that all subsystems are healthy. The original README is preserved below:

## Overview 
#### The Stretch Diagnostics package provides tools to run different suites of tests on the stretch robot to debug issues.

> **Note**
> This tool is to be used only with Hello Robot's guidance.

## Installation
Standard python package install
```commandline
pip3 install hello-robot-stretch-diagnostics
```
For local python package installation
```commandline
cd ~/repos
git clone https://github.com/hello-robot/stretch_diagnostics
cd stretch_diagnostics/python
pip3 install -e .
```

## Using the `stretch_diagnostic_check.py` tool
The `stretch_diagnostic_check.py` tool can be executed anywhere from the terminal 
to run different tests, see test status reports, manage test data and zip the generated diagnostics data.   
```commandline
$ stretch_diagnostics_tool.py -h
For use with S T R E T C H (R) RESEARCH EDITION from Hello Robot Inc.
---------------------------------------------------------------------

usage: stretch_diagnostic_check.py [-h] [--report] [--zip] [--archive] [--menu] [--unzip [zip file]] [--list [verbosity]]
                                   [--simple | --power | --realsense | --stepper | --firmware | --dynamixel | --gripper | --ros | --cpu | --arm | --all]

Script to run Diagnostic Test Suite and generate reports.

optional arguments:
  -h, --help          show this help message and exit
  --report            Report the latest diagnostic check
  --zip               Generate zip file of latest diagnostic check
  --archive           Archive old diagnostic test data
  --menu              Run tests from command line menu
  --unzip [zip file]  Unzip the given stretch diagnostics zipped data and view report.
  --list [verbosity]  Lists all the available TestSuites and its included TestCases Ordered (Default verbosity=1)
  --simple            Run simple diagnostics across entire robot
  --power             Run diagnostics on the power subsystem
  --realsense         Run diagnostics on the Intel RealSense D435 camera
  --stepper           Run diagnostics on stepper drivers
  --firmware          Run diagnostics on robot firmware versions
  --dynamixel         Run diagnostics on all robot Dynamixel servos
  --gripper           Run diagnostics on the gripper subsystem
  --ros               Run diagnostics on the ROS packages
  --cpu               Run diagnostics on the CPU
  --arm               Run diagnostics on the Arm
  --all               Run all diagnostics
```
The diagnostics data are stored under the directory `~/stretch_user/log/diagnostic_check`.



