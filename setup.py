from __future__ import print_function

import os
import sys
from subprocess import check_output

from setuptools import find_packages, setup


def get_version():
    """Determine the most appropriate version number for this package."""

    # try to use git tag if building python package
    try:
        # append git sha to version
        return '0.0.' + check_output("git rev-list --count HEAD",shell=True).decode('utf8')
    except Exception as e:
        print("Failed to acquire version info from git: {e}".format(e=e), file=sys.stderr)
        return '0.0.0'


def requirements(extra=None):
    """Return list of required package names from requirements.txt."""
    # strip trailing comments, and extract package name from git urls.
    if extra:
        filename = 'requirements-' + extra + '.txt'
    else:
        filename = 'requirements.txt'
    requirements = [r.strip().split(';',1)[0].split(' ', 1)[0].split('egg=', 1)[-1]
                    for r in open(filename) if r.strip() and not r.strip().startswith('#')]
    return requirements

for x in requirements(extra='deploy'):
    print(x)

setup(
    name='dashboard',
    version=get_version(),
    packages=find_packages(),
    install_requires=requirements(),
    extras_require={
        'deploy': requirements(extra='deploy'),
    },
    entry_points={
        'console_scripts': [
            'dashboard = dashboard.manage:main',
        ],
    },
    include_package_data=True,
)
