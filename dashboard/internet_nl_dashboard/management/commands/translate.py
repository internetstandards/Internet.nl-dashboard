# Some help to translate the django part.
# This tries to help you avoid remembering the "messages" mess from Django.
import logging

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

log = logging.getLogger(__package__)


class Command(BaseCommand):
    help = "Automatically updates any explicitly maintained translations. Helps you on your way."

    """
    # Replaces django-admin makemessages -a with explicitly maintained translation commands.

    # You should not have to remember those commands: they are a burden.
    # This command automatically updates any explicitly maintained translation for you.

    # Just use this command twice: first to create the translations, secondly to compile them.
    # In any case it does both, first makemessages and then compilmessages.

    # Languages are defined in settings.

    # Django uses language codes inconstently, in this project we always use two letter language codes until
    # something better comes along.
    # https://docs.djangoproject.com/en/1.11/topics/i18n/#term-language-code
    # Django should use one approach, preferably ditch their own invention of language codes
    # and just go for locales centrally defined, such as a list from ISO.
    """

    def handle(self, *args, **options):
        # -a means _all_ languages in the config. Only makes the languages for the "django" domain, so no javascript.
        # all *.py, *.html and *.txt files
        # only show a pointer to the file, instead of file+line number. The line number causes pollution when updating
        # and it's pretty easy to discover the translation anyway.
        log.debug("Making messages for all locales from *.py, *.html and *.txt files.")
        call_command('makemessages', '--ignore', 'vendor', '--ignore', '.tox',  '-a', '--add-location', 'file')

        # -d djangojs =
        # https://docs.djangoproject.com/en/2.0/topics/i18n/translation/#creating-message-files-from-js-code
        # Now add messages for *.js files
        log.debug("Making messages for all locales from *.js files.")
        call_command('makemessages', '--ignore', 'vendor', '--ignore', '.tox',
                     '--add-location', 'file', '-a', '-d', 'djangojs')

        log.debug("Compiling messages")
        for language in settings.LANGUAGES:

            # Compiles .po files created by makemessages to .mo files for use with the built-in gettext support.
            # Default is to process all.
            # if you don't specify the locale, it will do ALL LOCALES IT KNOWS! which takes a long time to do nothing
            # This command is not feature complete and WILL also compile messages in the .tox directory which is a
            # waste of time and obfuscates output.
            # https://code.djangoproject.com/ticket/29973#ticket
            # Ready for checkin :) Awesome features, saves a lot of time
            call_command('compilemessages', '-l', language[0])

        log.info('You can find the locale files in ./locale/(language code)/LC_MESSAGES/django(js).po')
        log.info('Compiled files are located in ./locale/(language code)/LC_MESSAGES/django(js).mo')
        log.info('')
        log.info('Run this command again to have your changes compiled.')
        log.info('Remember to keep the amount of translations in javascript as low as possible. Design > translation.')
