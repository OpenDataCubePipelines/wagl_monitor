#!/usr/bin/env python3
import versioneer
from setuptools import setup, find_packages

install_requires = [
    "click",
    "flask",
    "pathlib",
    "python-dateutil",
    "sqlalchemy",
    "pathlib",
    "py-dateutil",
#    "sqlite3",
]

tests_require = [
    "mock",
    "pytest",
    "pytest-runner"
]

setup(
    name='wagl_monitor',
    version="0.0.1",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points='''\
    [console_scripts]
    wagl_monitor=wagl_monitor.scripts.wagl_monitor:cli
    ''',
)
