import os
from datetime import datetime, timedelta

from dashboard import settings
from dashboard.internet_nl_dashboard import log


def renew_lock(process_name: str) -> bool:
    lockfile = f"{settings.LOCKFILE_DIR}{process_name}.lock"
    with open(lockfile, 'wt') as handle:
        return handle.write('locked') > 1


def remove_lock(process_name: str) -> None:
    lockfile = f"{settings.LOCKFILE_DIR}{process_name}.lock"
    os.remove(lockfile)


def lock_exists(process_name: str) -> bool:
    lockfile = f"{settings.LOCKFILE_DIR}{process_name}.lock"
    return os.path.isfile(lockfile)


def remove_expired_lock(process_name, timeout_in_seconds) -> None:
    if lock_exists(process_name) and lock_expired(process_name, timeout_in_seconds):
        remove_lock(process_name)


def lock_expired(process_name: str, timeout_in_seconds: int = 300) -> bool:
    lockfile = f"{settings.LOCKFILE_DIR}{process_name}.lock"
    locktime = datetime.fromtimestamp(os.path.getmtime(lockfile))
    expiration_time = locktime + timedelta(seconds=timeout_in_seconds)
    return datetime.now() > expiration_time


def temporary_file_lock(process_name: str, timeout_in_seconds: int = 300) -> bool:

    if not lock_exists(process_name):
        log.info("No lockfile found, creating new lock file.")
        return renew_lock(process_name)

    if lock_expired(process_name, timeout_in_seconds):
        log.info("Logfile expired, renewing lock.")
        return renew_lock(process_name)

    log.info("Could not acquire lock, it has not expired.")
    return False
