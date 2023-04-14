# SPDX-License-Identifier: Apache-2.0
# example: dashboard dashboard_celery worker -Q storage -l debug
from __future__ import absolute_import, unicode_literals

import logging
import os

from django.core.management.base import BaseCommand

log = logging.getLogger(__package__)


def reusable_run_from_argv(argv):
    """Replace python with celery process with given arguments."""
    appname = __name__.split('.', 1)[0] + '.celery:app'
    appname_arguments = ['-A', appname]

    log.info(argv[1])
    log.info(argv[1:2] + appname_arguments + argv[2:])

    # todo: fix Starting a process without a shell.
    # todo: fix Starting a process with a partial executable path
    # Not fixed because if the binary can be replaced, this is the least of our problems
    os.execvp("celery", argv[1:2] + appname_arguments + argv[2:])  # nosec


class Command(BaseCommand):  # pylint: disable=abstract-method
    """Celery command wrapper."""
    help = __doc__

    # disable (MySQL) check on startup
    requires_system_checks = []

    def run_from_argv(self, argv):
        reusable_run_from_argv(argv)
