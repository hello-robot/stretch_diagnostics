import setuptools
from os import listdir
from os.path import isfile, join


scripts=set()
script_paths=[]#'./fleet','./bringup','./subs','./roadkill']
for script_path in script_paths:
    scripts=scripts.union({script_path+'/'+f for f in listdir(script_path) if isfile(join(script_path, f))})


setuptools.setup(
    name="hello_robot_stretch_production_tools",
    version="0.0.1",
    author="Hello Robot Inc.",
    author_email="support@hello-robot.com",
    description="Stretch Production Tools",
    long_description="Stretch Production Tools",
    long_description_content_type="text/markdown",
    url="https://github.com/hello-robot/stretch_production_tools",
    scripts = scripts,
    packages=['stretch_production_tools'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    install_requires=['rsa==3.4']#,'hello-robot-stretch-factory>=0.2.0','hello-robot-stretch-body>0.3.0','future']
)
