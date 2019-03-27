# Copy from websecmap, changed websecmap to dashboard.
# Todo: as soon as you import anything from dashboard.celery.worker, the internet_nl_dashboard app disappears from
# the known django apps list. Which is weird.
import logging
import os
import platform
import shutil
import sys
import tempfile

from celery.signals import celeryd_init, worker_shutdown
from django.conf import settings

from dashboard.celery.worker import (tls_client_certificate, worker_configuration,
                                     worker_verify_role_capabilities)

"""This module is imported by failmap.__init__ to register Signal hooks."""


log = logging.getLogger(__name__)

# as soon as this gets imported the internet_nl_dashboard app is gone.


@celeryd_init.connect
def configure_workers(sender=None, conf=None, instance=None, **kwargs):
    """Configure workers when Celery is initialized."""

    # set hostname based on context
    container_host_name = os.environ.get('HOST_HOSTNAME', None)
    if container_host_name:
        hostname = '.'.join([platform.node(), container_host_name])
    else:
        hostname = platform.node()
    role = os.environ.get('WORKER_ROLE', 'default')
    instance.hostname = "%s@%s" % (role, hostname)

    if not worker_verify_role_capabilities(role):
        log.error('Host does not seem to have capabilities to run chosen role!')
        sys.exit(1)
    log.info('Worker is capable for chosen role.')

    try:
        # create a universal temporary directory to be removed when the application quits
        settings.WORKER_TMPDIR = tempfile.mkdtemp()
        # configure worker queues
        conf.update(worker_configuration())

        # for remote workers configure TLS key and certificate from PKCS12 file
        conf.update(tls_client_certificate())
    except BaseException:
        log.exception('Failed to setup worker configuration!')
        sys.exit(1)


@worker_shutdown.connect
def cleanup_certificates(sender=None, conf=None, **kwargs):
    """Remove worker temporary directory."""

    shutil.rmtree(settings.WORKER_TMPDIR)
