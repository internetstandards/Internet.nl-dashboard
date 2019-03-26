# Near-copy of websecmap. Changed the command to a hardcoded 'celery' as the command was already defined.
# Django is not consistent in what has precendence. Dashboard does override admin stuff, but not commands.
from __future__ import absolute_import, unicode_literals

import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Celery command wrapper."""

    help = __doc__

    # disable (MySQL) check on startup
    requires_system_checks = False

    def run_from_argv(self, argv):
        """Replace python with celery process with given arguments."""
        appname = __name__.split('.', 1)[0] + '.celery:app'
        appname_arguments = ['-A', appname]

        print(argv[1])
        print(argv[1:2] + appname_arguments + argv[2:])

        os.execvp("celery", argv[1:2] + appname_arguments + argv[2:])
