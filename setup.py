# coding: utf-8
import re
from parver import Version, ParseError
import setuptools
import sys
import argparse
import shutil
from pathlib import Path
import os

# Use the following command from a terminal window to generate the whl with source code
# The arguments -condition-monitor -topic-distribution. Omitting the arguments will create all whl files
# `python setup.py -condition_monitor -topic_distribution`

CURRENT_DIR = Path(__file__).parent.resolve()
BUILD_DIR = CURRENT_DIR.joinpath('build')
EGG = '.egg-info'

with open("seeq/addons/email/condition_monitor/README.md", "r") as fh:
    long_description_condition_monitor = fh.read()

addons = dict(
    condition_monitor=dict(
        version_file="seeq/addons/email/condition_monitor/_version.py",
        installer_notebook="Email Condition Monitor Installer.ipynb",
        installer_target="seeq/addons/email/condition_monitor/deploy_notebooks",
        namespace=['seeq.addons.email.*'],
        exclude_packages=['seeq.addons.email.topic_distribution*'],
        name='seeq-email-condition-monitor',
        author="Alberto Rivas",
        author_email="alberto.rivas@seeq.com",
        description="Data Lab Notebook-based Email Condition Monitor Scheduling tool",
        long_description=long_description_condition_monitor,
        install_requires=[
            'jsonschema>=4.16.0',
            'beautifulsoup4>=4.9.3',
            'pytz>=2022.4',
        ]
    ),
    topic_distribution=dict(
        version_file="seeq/addons/email/topic_distribution/_version.py",
        namespace=['seeq.addons.email.*'],
        exclude_packages=['seeq.addons.email.condition_monitor*'],
        name='seeq-email-topic-distribution',
        author="Alberto Rivas",
        author_email="alberto.rivas@seeq.com",
        description="Data Lab Notebook-based Email Condition Monitor Scheduling tool",
        long_description="",
        install_requires=[
            'jsonschema>=4.16.0',
            'beautifulsoup4>=4.9.3',
            'pytz>=2022.4',
        ]
    )
)


def get_version(version_file):
    version_scope = {'__builtins__': None}
    with open(version_file, "r+") as f:
        version_file = f.read()
        version_line = re.search(r"__version__ = (.*)", version_file)
        if version_line is None:
            raise ValueError(f"Invalid version. Expected __version__ = 'xx.xx.xx', but got \n{version_file}")
        version = version_line.group(1).replace(" ", "").strip('\n').strip("'").strip('"')
        print(f"version: {version}")
        try:
            Version.parse(version)
            exec(version_line.group(0), version_scope)
        except ParseError as e:
            print(str(e))
            raise
    return version_scope['__version__']


def create_setup_args_dict(addon_key):
    return dict(
        name=addons.get(addon_key).get('name'),
        version=get_version(addons.get(addon_key).get('version_file')),
        author=addons.get(addon_key).get('author'),
        author_email=addons.get(addon_key).get('author_email'),
        description=addons.get(addon_key).get('description'),
        long_description=addons.get(addon_key).get('long_description'),
        long_description_content_type="text/markdown",
        license='Apache License 2.0',
        platforms=["Linux", "Windows"],
        url="",
        packages=setuptools.find_namespace_packages(
            include=addons.get(addon_key).get('namespace'),
            exclude=addons.get(addon_key).get('exclude_packages')),
        include_package_data=True,
        zip_safe=False,
        install_requires=addons.get(addon_key).get('install_requires'),
        classifiers=[
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.8',
    )


def cli_interface():
    """ Installs MyAddOnClassName as a Seeq Add-on Tool """
    parser = argparse.ArgumentParser(
        description=f'Create wheel files of the seeq.addons.email project. You need to supplu at least one of the '
                    f'following arguments')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('-topic_distribution', action='store_true',
                   help='Creates the topic_distribution wheel')
    g.add_argument('-condition_monitor', action='store_true',
                   help="Creates the condition_monitor wheel")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()


args = cli_interface()
sys.argv = [sys.argv[0], 'bdist_wheel']

for addon in addons:
    if getattr(args, addon):
        print(f"Moving installer notebook inside package (for user reference)")
        filename = addons.get(addon).get('installer_notebook')
        target = addons.get(addon).get('installer_target')
        shutil.copyfile(CURRENT_DIR.joinpath(filename),
                        CURRENT_DIR.joinpath(target).joinpath(filename))
        print(f'creating wheel for addon: {addon}')
        # need to delete the previous build and egg folders, otherwise it will package
        # what was in those folders plus the current addon
        if BUILD_DIR.exists() and BUILD_DIR.is_dir():
            shutil.rmtree('build')
        dirs = os.walk(CURRENT_DIR)
        for d in os.walk(CURRENT_DIR):
            if d[0].endswith(EGG):
                shutil.rmtree(d[0])
        setuptools.setup(**create_setup_args_dict(addon))
    else:
        print(f"addon: {addon}... SKIPPED")
