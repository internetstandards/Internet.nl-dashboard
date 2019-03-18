from __future__ import print_function

import os
import sys
from subprocess import check_output

from setuptools import find_packages, setup


def get_version():
    """Determine the most appropriate version number for this package."""

    # prefer explicit version provided by (docker) build environment
    if os.path.exists('version'):
        version = open('version').read().strip()
        # ignore empty version file
        if version:
            print('Found version in file', file=sys.stderr)
            return version

    # try to use git tag if building python package
    try:
        # get closest tag version
        tag_version = check_output(["git", "describe", "--tags", "--abbrev=0"]).rstrip().decode()
        # determine if there has been development beyond the latest tagged commit
        dirty = bool(check_output(["git", "status", "--porcelain"]).strip())
        unreleased = bool(check_output(["git", "rev-list", tag_version + ".."]).strip())

        # there are unsaved changes
        if dirty:
            print('Repo has unsaved changes, versioning as development', file=sys.stderr)
            return tag_version + '.dev0'

        # the verion is commits ahead of latest tagged release
        if unreleased:
            print('Found commits after last release, versioning with latest sha', file=sys.stderr)

            # append git sha to version
            return tag_version + '+' + check_output("git rev-parse HEAD".split()).strip().decode()[:8]

        return tag_version
    except Exception as e:
        print("Failed to acquire version info from git: {e}".format(e=e), file=sys.stderr)
        return '0.0.0'


def requirements(extra=None):
    """Return list of required package names from requirements.txt."""
    # strip trailing comments, and extract package name from git urls.
    if extra:
        filename = 'requirements.' + extra + '.txt'
    else:
        filename = 'requirements.txt'
    requirements = [r.strip().split(' ', 1)[0].split('egg=', 1)[-1]
                    for r in open(filename) if not r.startswith('#')]
    return requirements


setup(
    name='dashboard',
    version=get_version(),
    packages=find_packages(),
    install_requires=requirements(),
    # allow extra packages to be installed, eg: `pip install -e .[deploy]`
    extras_require={
        'development': requirements(extra='dev'),
        'deploy': requirements(extra='deploy'),
    },
    entry_points={
        'console_scripts': [
            'dashboard = dashboard.manage:main',
        ],
    },
    include_package_data=True,
)
