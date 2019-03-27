from pkg_resources import get_distribution

__version__ = get_distribution(__name__.split('.', 1)[0]).version
