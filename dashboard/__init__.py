try:
    # this file is added during build
    # pylint: disable=E0401
    from .__version__ import VERSION
except ModuleNotFoundError:
    # if not available, that means the application is running in development
    VERSION = "0.0.0.dev0"

__version__ = VERSION
