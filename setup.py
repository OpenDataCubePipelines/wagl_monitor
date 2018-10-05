#!/usr/bin/env python3
import versioneer
from setuptools import setup, find_packages

install_requires = [
    "click",
    "flask",
    "pathlib",
    "python-dateutil",
    "sqlalchemy [postgresql]",
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
    entry_points={
        'console_scripts': [
            'wagl-log-extract=wagl_monitor.scripts.wagl_log_extract:cli',
            'wagl-log-results=wagl_monitor.scripts.wagl_log_results:cli'
        ]
    },
    extras_require={
        'testing': tests_require
    },
)
