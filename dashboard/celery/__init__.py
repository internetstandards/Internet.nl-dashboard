"""
This is a copy of the websecmap celery file, the only change is that a different settings file is imported,
including both the websecmap and dashboard tasks.
"""

# https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
# http://oddbird.net/2017/03/20/serializing-things/
# http://docs.celeryproject.org/en/latest/userguide/security.html

import logging
import os
import time

import flower.utils.broker
from celery import Celery, Task
from django.conf import settings

from websecmap.celery.worker import QUEUES_MATCHING_ROLES

log = logging.getLogger(__package__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")

app = Celery(__name__)
app.config_from_object('django.conf:settings', namespace='CELERY')
# use same result backend as we use for broker url
# If broker_url is None, you  might not have started websecmap correctly. See docs/source/conf.py for a correct example.
app.conf.result_backend = app.conf.broker_url.replace('amqp://', 'rpc://')


# autodiscover all celery tasks in tasks.py files inside websecmap modules
appname = __name__.split('.', 1)[0]
app.autodiscover_tasks([app for app in settings.INSTALLED_APPS
                        if app.startswith('dashboard') or app.startswith('websecmap')])

# http://docs.celeryproject.org/en/master/whatsnew-4.0.html?highlight=priority#redis-priorities-reversed
# http://docs.celeryproject.org/en/master/history/whatsnew-3.0.html?highlight=priority
# priorities 0-9 are divided into 4 steps.
# https://github.com/celery/celery/blob/a87ef75884e59c78da21b1482bb66cf649fbb7d3/docs/history/whatsnew-3.0.rst#redis-priority-support
# https://github.com/celery/celery/blob/f83b072fba7831f60106c81472e3477608baf289/docs/whatsnew-4.0.rst#redis-priorities-reversed
# contrary to 'documentation' in release notes the redis priorities do not seem aligned with rabbitmq
app.conf.broker_transport_options = {
    'priority_steps': [1, 5, 9],
}
if 'redis://' in app.conf.broker_url:
    PRIO_HIGH = 1
    PRIO_NORMAL = 5
    PRIO_LOW = 9
else:
    PRIO_HIGH = 9
    PRIO_NORMAL = 5
    PRIO_LOW = 1

# lookup table for routing keys for different IP versions
IP_VERSION_QUEUE = {
    4: 'scanners.ipv4',
    6: 'scanners.ipv6',
}


class DefaultTask(Task):
    """Default settings for all websecmap tasks."""

    priority = PRIO_NORMAL


app.Task = DefaultTask


class ParentFailed(Exception):
    """Error to indicate parent task has failed."""

    def __init__(self, message, *args, cause=None):
        """Allow to set parent exception as cause."""
        if cause:
            self.__cause__ = cause
        super(ParentFailed, self).__init__(message, *args)


@app.task(queue='isolated', bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(queue='isolated')
def waitsome(sleep):
    """Wait some time and return epoch at completion."""

    time.sleep(sleep)
    return time.time()


@app.task(queue='isolated', rate_limit='1/s')
def rate_limited(sleep):
    """Wait some time but limit to maximum tasks of 1 per second."""

    time.sleep(sleep)
    return time.time()


def status():
    """Return a dictionary with the status of the Celery task processing system."""
    inspect = app.control.inspect()

    # query workforce statistics using control.inspect API and extract some relevant data from it
    stats = inspect.stats() or {}
    active = inspect.active()
    reserved = inspect.reserved()
    active_queues = inspect.active_queues()
    workers = [{
        'name': worker_name,
        'queues': [q['name'] for q in active_queues.get(worker_name, [])],
        'tasks_processed': sum(worker_stats['total'].values()),
        'tasks_active': len(active.get(worker_name, [])),
        'tasks_reserved': len(reserved.get(worker_name, [])),
        'prefetch_count': worker_stats['prefetch_count'],
        'concurrency': worker_stats['pool']['max-concurrency'],
    } for worker_name, worker_stats in stats.items()]

    workers = sorted(workers, key=lambda k: (k['name']), reverse=False)

    if 'redis://' in app.conf.broker_url:
        queue_names = [q.name for q in QUEUES_MATCHING_ROLES['queuemonitor']]

        # on localhost and remote workers there is no event loop. This causes an exception.
        # Inspired on https://github.com/tornadoweb/tornado/issues/2352 and
        # https://github.com/tornadoweb/tornado/issues/2308
        # this attempt seems to create an event loop without any further issues. This will allow the code to complete.
        # the reason _why_ there was no event loop in these cases is completely unclear to me. The code in
        # flower just uses @gen.coroutine and is not to blame.
        # https://github.com/mher/flower/blob/master/flower/utils/broker.py
        # 'solves': RuntimeError: There is no current event loop in thread 'Thread-3'.
        try:
            import asyncio
            asyncio.set_event_loop(asyncio.new_event_loop())
        except BaseException:
            # an eventloop already exists.
            pass

        # use flower to not reinvent the wheel on querying queue statistics
        queue_stats = []
        try:
            broker = flower.utils.broker.Broker(app.conf.broker_url, broker_options=app.conf.broker_transport_options)
            queue_stats = broker.queues(queue_names).result()
        except RuntimeError as e:
            log.error("Could not connect to flower to retrieve queue stats.")
            log.exception(e)

        queues = [{'name': x['name'], 'tasks_pending': x['messages']} for x in queue_stats]
    else:
        raise NotImplementedError('Currently only Redis is supported!')

    queues = sorted(queues, key=lambda k: (k['name']), reverse=False)

    alerts = []
    if not workers:
        alerts.append('No active workers!')
    if len(workers) > 9000:
        alerts.append('Number of workers is OVER 9000!!!!1111')

    return {
        'alerts': alerts,
        'workers': workers,
        'queues': queues
    }
