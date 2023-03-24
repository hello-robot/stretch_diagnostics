import setuptools
from os import listdir
from os.path import isfile, join

with open("../README.md", "r") as fh:
    long_description = fh.read()

scripts = set()
script_paths = ['./tools']
for script_path in script_paths:
    scripts = scripts.union({script_path + '/' + f for f in listdir(script_path) if isfile(join(script_path, f))})

stretch_diagnostics_tests_dir_list = ['./{}/*'.format(f) for f in listdir('./stretch_diagnostics_tests')]
package_data = {'stretch_diagnostics_tests': stretch_diagnostics_tests_dir_list}

setuptools.setup(
    name="hello_robot_stretch_diagnostics",
    version="0.0.9",
    author="Hello Robot Inc.",
    author_email="support@hello-robot.com",
    description="Stretch Diagnostics",
    long_description=long_description[30:],
    long_description_content_type="text/markdown",
    url="https://github.com/hello-robot/stretch_diagnostics",
    scripts=scripts,
    packages=['stretch_diagnostics', 'stretch_diagnostics_tests'],
    package_data=package_data,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    install_requires=['hello-robot-stretch-factory>=0.3.12','hello-robot-stretch-body>=0.4.15','stress','xmltodict']
)
