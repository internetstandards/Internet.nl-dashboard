# SPDX-License-Identifier: Apache-2.0
import logging
import os
import subprocess  # nosec
import sys

from django.core.management import call_command
# django_uwsgi is only in the deployement depencies as it has issues on M1 macs.
from django_uwsgi.management.commands.runuwsgi import \
    Command as RunserverCommand  # pylint: disable=import-error

from dashboard.security import confirm_keys_are_changed

log = logging.getLogger(__name__)

UWSGI_INFO = """Production server started without UWSGI installed.

Please refer to deployment instructions for more information.

http://failmap.readthedocs.io/en/latest/topics/deployment.html
"""


class Command(RunserverCommand):
    """Run a Failmap production server."""

    command = 'runuwsgi'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--migrate', action='store_true',
                            help='Before starting server run Django migrations.')
        parser.add_argument('-l', '--loaddata', default=None, type=str,
                            help='Comma separated list of data fixtures to load.')

        super().add_arguments(parser)

    def handle(self, *args, **options):
        """Optionally run migrations and load data."""

        confirm_keys_are_changed()

        try:
            # todo: fix Starting a process with a partial executable path
            # todo: fix subprocess call with shell=True seems safe, but may be changed in the future, consider rewriting
            #  without shell
            subprocess.check_call('command -v uwsgi', shell=True, stdout=subprocess.DEVNULL)  # nosec
        except subprocess.CalledProcessError:
            print(UWSGI_INFO)
            sys.exit(1)

        if set(options).intersection(['migrate', 'loaddata']):
            # detect if we run inside the autoreloader's second thread
            inner_run = os.environ.get('RUN_MAIN', False)

            if inner_run:
                log.info('Inner run: skipping --migrate/--loaddata.')
            else:
                if options['migrate']:
                    call_command('migrate')
                if options['loaddata']:
                    call_command('load_dataset', *options['loaddata'].split(','))

        sys.stdout.flush()
        super().handle(*args, **options)
