from pkg_resources import get_distribution

# Handle celery signals.
# When adding these signals, the internet_nl_dashboard app is removed from the commands.
import dashboard.signals  # noqa

__version__ = get_distribution(__name__.split('.', 1)[0]).version
