# Copy from websecmap, changed websecmap to dashboard.
# Todo: as soon as you import anything from dashboard.celery.worker, the internet_nl_dashboard app disappears from
# the known django apps list. Which is weird.
"""This module is imported by failmap.__init__ to register Signal hooks."""
import getpass
import logging
import os
import platform
import shutil
import socket
import ssl
import sys
import tempfile

import certifi
import OpenSSL
from celery.signals import celeryd_init, worker_shutdown
from constance import config
from django.conf import settings
from kombu import Queue
from retry import retry

log = logging.getLogger(__package__)


TLS_CLIENT_FILE = '/client.p12'

# list of all roles that require internet connectivity
ROLES_REQUIRING_ANY_NETWORK = [
    'internet',  # the queue scanner accepts 4and6, 4 or 6 - so ANY network scan :)
]

ROLES_REQUIRING_IPV4_AND_IPV6 = [
    'default',
    'all_internet'
]

# list of all roles that require IPv6 networking
ROLES_REQUIRING_IPV6 = [
    'v6_internet',
    'default_ipv6',
]

ROLES_REQUIRING_IPV4 = [
    'v4_internet',
    'default_ipv4',
    'qualys',  # only supports ipv4(!)
]

ROLES_REQUIRING_NO_NETWORK = [
    'storage',
    'calculator',
    'claim_proxy'
]

ROLES_REQUIRING_GUI_AND_NETWORK = [
    'desktop'
]

# define roles for workers
QUEUES_MATCHING_ROLES = {
    # Select between roles.

    # universal worker that has access to database and internet on both v4 and v6
    # will work in one-worker configuration - and slowly -  it's untested and it likely will not be a great experience
    'default': [
        # doesn't care about network family, any network is fine
        Queue('internet'),
        # only ipv4 tasks
        Queue('ipv4'),
        # only ipv4 tasks
        Queue('ipv6'),
        # needs both network families to be present
        Queue('4and6'),
        # for tasks that require a database connection
        Queue('storage'),
        # tasks that require no network, no database. Such as calculations, parsing of datasets etc.
        Queue('isolated'),
        # run qualys scans
        Queue('qualys'),
        # scaling things
        Queue('hyper'),
    ],

    # queuemonitor shows the currently running queues on the dashboard. It will not do anything else. It subscribes
    # to all queues. This does not have a worker (and doesn't need one).
    'queuemonitor': [
        Queue('storage'),
        Queue('hyper'),
        Queue('4and6'),
        Queue('ipv4'),
        Queue('ipv6'),
        Queue('internet'),
        Queue('qualys'),
        Queue('isolated'),
        Queue('claim_proxy')
    ],

    'default_ipv4': [
        Queue('internet'),
        Queue('ipv4'),
        Queue('storage'),
        Queue('isolated'),
    ],
    'default_ipv6': [
        Queue('internet'),
        Queue('ipv6'),
        Queue('storage'),
        Queue('isolated'),
    ],
    'v4_internet': [
        Queue('internet'),
        Queue('ipv4'),
        Queue('isolated'),
    ],
    'v6_internet': [
        Queue('internet'),
        Queue('ipv6'),
        Queue('isolated'),
    ],
    'storage': [
        Queue('storage'),
        # Queue('isolated'),  # Do NOT perform isolated (slow) tasks, which might block the worker.
        # Given there is only one storage worker, blocking it doesn't help it's work.
    ],
    'claim_proxy': [
        Queue('claim_proxy'),
        # Queue('isolated'),  # Do NOT perform isolated (slow) tasks, which might block the worker.
        # Given there is only one storage worker, blocking it doesn't help it's work.
    ],
    'hyper': [
        # where hyper scaling tasks take place. Is not waiting or dealing with load elsewhere.
        Queue('hyper'),
    ],
    'calculator': [
        Queue('isolated')
    ],
    'desktop': [
        Queue('desktop')
    ],
    # universal scanner worker that has internet access for either IPv4 and IPv6 or both (you don't know)
    'any_internet': [
        Queue('internet'),  # tasks that requires ANY network
        Queue('isolated'),  # no network, no database
    ],
    # all internet access, with ipv4 and 6 configured
    'all_internet': [
        Queue('internet'),
        Queue('ipv4'),
        Queue('ipv6'),
        Queue('4and6'),
        Queue('isolated'),
    ],
    # special scanner worker for qualys rate limited tasks to not block queue for other tasks
    # and it needs a dedicated IP address, which is coded in hyper workers.
    'qualys': [
        Queue('qualys'),
    ]
}


def worker_configuration():
    """Apply specific configuration for worker depending on environment."""

    role = os.environ.get('WORKER_ROLE', 'default')

    log.info('Configuring worker for role: %s', role)

    # configure which queues should be consumed depending on assigned role for this worker
    return {'task_queues': QUEUES_MATCHING_ROLES[role]}


@retry(tries=3, delay=5)
def worker_verify_role_capabilities(role):
    """Determine if chosen role can be performed on this host (eg: ipv6 connectivity.)"""

    failed = False

    if role in ROLES_REQUIRING_NO_NETWORK:
        return not failed

    if role in ROLES_REQUIRING_IPV6 or role in ROLES_REQUIRING_IPV4_AND_IPV6:
        # verify if a https connection to a IPv6 website can be made
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        try:
            s.connect((config.IPV6_TEST_DOMAIN, 443))
        except socket.gaierror:
            # docker container DNS might not be ready, retry
            raise
        except BaseException:
            log.warning('Failed to connect to ipv6 test domain %s via IPv6', config.IPV6_TEST_DOMAIN, exc_info=True)
            failed = True

    if role in ROLES_REQUIRING_IPV4 or role in ROLES_REQUIRING_IPV4_AND_IPV6:
        # verify if a https connection to a website can be made
        # we assume non-ipv4 internet doesn't exist
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        try:
            s.connect((config.CONNECTIVITY_TEST_DOMAIN, 443))
        except socket.gaierror:
            # docker container DNS might not be ready, retry
            raise
        except BaseException:
            log.warning('Failed to connect to test domain %s via IPv4', config.CONNECTIVITY_TEST_DOMAIN, exc_info=True)
            failed = True

    if role in ROLES_REQUIRING_ANY_NETWORK:
        # one may fail.

        # try v4 first
        s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        try:
            s4.connect((config.IPV6_TEST_DOMAIN, 443))
        except socket.gaierror:
            # docker container DNS might not be ready, retry
            raise
        except BaseException:
            s6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
            try:
                s6.connect((config.IPV6_TEST_DOMAIN, 443))
            except socket.gaierror:
                # docker container DNS might not be ready, retry
                raise
            except BaseException:
                log.warning('Failed to connect to test domain %s via both v6 and v6', config.CONNECTIVITY_TEST_DOMAIN,
                            exc_info=True)
                failed = True

    return not failed


def tls_client_certificate():
    """Configure certificates from PKCS12 file.

    If client file is provided will extract key and certificate pem to files and
    configure these with Celery. """

    tls_client_file = os.path.abspath(os.path.expanduser(
        os.environ.get('TLS_CLIENT_FILE', TLS_CLIENT_FILE)))

    if os.path.exists(tls_client_file):
        log.info('PKCS12 file found, configuring TLS for worker.')

        # try to open PKCS12 file without passphrase, if it fails ask for passphrase and try again
        try:
            p12 = OpenSSL.crypto.load_pkcs12(open(tls_client_file, 'rb').read())
        except OpenSSL.crypto.Error:
            log.warning('Failed to decrypt without passphrase.')

            passphrase = os.environ.get('PASSPHRASE')
            if passphrase:
                log.info('Got passphrase from environment')
            else:
                passphrase = getpass.getpass('Please provide passphrase for %s: ' % tls_client_file)
            p12 = OpenSSL.crypto.load_pkcs12(open(tls_client_file, 'rb').read(), passphrase)

        # store extracted key and cert in temporary files that are deleted on exit of the worker
        tls_client_cert_file = tempfile.NamedTemporaryFile(dir=settings.WORKER_TMPDIR, delete=False)
        tls_client_key_file = tempfile.NamedTemporaryFile(dir=settings.WORKER_TMPDIR, delete=False)
        tls_client_key_file.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
        tls_client_cert_file.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))

        # configure redis to use TLS
        ssl_options = {
            'ssl_keyfile': tls_client_key_file.name,
            'ssl_certfile': tls_client_cert_file.name,
            'ssl_ca_certs': certifi.where(),
            'ssl_cert_reqs': ssl.CERT_REQUIRED,
        }
        return {
            'broker_use_ssl': ssl_options,
            'redis_backend_use_ssl': ssl_options,
        }
    else:
        log.info('no PKCS12 file found, not configuring TLS.')
        return {}


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
