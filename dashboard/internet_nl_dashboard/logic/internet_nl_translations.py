import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import markdown
import polib
import requests
from django.utils.text import slugify

SUPPORTED_LOCALES = ['nl', 'en']
VUE_I18N_OUTPUT_PATH = 'dashboard/internet_nl_dashboard/static/js/translations/'
DJANGO_I18N_OUTPUT_PATH = 'dashboard/internet_nl_dashboard/locale/'


def convert_internet_nl_content_to_vue():
    """
    Uses polib to get the contents of a .po file. This file is then 'mangled' into a vue i18n object. This
    object is stored as a .vue file and can be included in your views (or your views can connect to it).

    The upside is that translations from internet.nl get a place here. The downside is that when they delete a key
    or things change drastically, the keys will be missing here.

    done: verify that when the entire translation is missing / empty, the application continues to function with
          just the ugly labels or fallback labels. -> Yes, this happens. It's ugly, but it still works.

    done: where will the generated files be placed? -> static/js/translations/
    done: download the file from the remote location
    done: how to share i18n objects within vue from different sources? Can just be called using the path...
          So you can just in your own i18n reuse previously defined translations.
    done: how to dynamically support multiple languages? And how does the i18n object doesn't become insanely big?
          -> just load them into the same file. The language file for NL and EN is now 300 kb and will grow 150 kb
          per language. There will be a moment when it's just too much and languages need to be loaded dynamically.
          For now there is no option to do that yet.
    done: should we merge all translation files into one? probably... -> yes, this is now happening and it
          doesn't scale. All languages are also saved separately. It's not clear how to dynamically load them.
          Up until 1 MB of languages is probably fine.
    done: Remove some of the larger variables we're not going to use anyway (we can just point to internet.nl for that
          content). This saves about 50 kilobyte per language. Each language is now about 100kb with relevant content.
    todo: how to load languages dynamically in vue i18s? Could there be a callback or something?

    :return: None
    """

    translated_locales: List[Dict[str, List[Any]]] = []

    for locale in SUPPORTED_LOCALES:
        raw_content = get_locale_content(locale)
        store_as_django_locale(locale, raw_content)
        structured_content = load_as_po_file(raw_content)
        translated_locales.append({'locale': locale, 'content': structured_content})

        # support a per-language kind of file, in case we're going to do dynamic loading of languages.
        vue_i18n_content = convert_vue_i18n_format([{'locale': locale, 'content': structured_content}])
        store_vue_i18n_file('internet_nl.%s' % locale, vue_i18n_content)

    # the locales are easiest stored together. This makes language switching a lot easier.
    vue_i18n_content = convert_vue_i18n_format(translated_locales)
    store_vue_i18n_file('internet_nl', vue_i18n_content)


def get_locale_content(locale: str) -> bytes:
    """
    A simple download and return response function.

    Input files:
    https://github.com/NLnetLabs/Internet.nl/blob/master/translations/nl/main.po
    -> https://raw.githubusercontent.com/NLnetLabs/Internet.nl/master/translations/nl/main.po

    https://github.com/NLnetLabs/Internet.nl/tree/master/translations/en/main.po
    -> https://raw.githubusercontent.com/NLnetLabs/Internet.nl/master/translations/en/main.po

    :param locale: 2 letter locale.
    :return: str
    """

    url = "https://raw.githubusercontent.com/NLnetLabs/Internet.nl/master/translations/%s/main.po" % locale
    response = requests.get(url)
    return response.content


def store_as_django_locale(locale, content):
    """
    Stores content from internet.nl translations (or any content) in the appropriate locale folder
    in this project. If the locale folder does not exist, it will be created.

    These texts are used on the main pages, up until when this is converted to a Vue at some point.

    :param content:
    :param locale:
    :return:
    """

    filepath = "%s%s" % (DJANGO_I18N_OUTPUT_PATH, f"%s/LC_MESSAGES/django.po" % locale)

    # If the language does not exist yet, make the folder supporting this language.
    os.makedirs(Path(filepath).parent, exist_ok=True)

    with open(filepath, 'w') as f:
        f.write(content.decode('UTF-8'))


def load_as_po_file(raw_content: bytes) -> List[Any]:
    """
    The POfile library requires a file to exist, so we create a temporary one that will be read and parsed.
    The parsed content will be returned.

    See here how that works:
    https://bitbucket.org/izi/polib/wiki/Home

    :param raw_content: string that contains the contents of a .po file.
    :return:
    """
    with tempfile.NamedTemporaryFile() as f:
        f.write(raw_content)
        f.flush()
        return polib.pofile(f.name)


def convert_vue_i18n_format(translated_locales: List[Dict[str, List[Any]]]) -> str:
    """
    done: will markdown be parsed to html in this method? Or should we do that on the fly, everywhere...
          It seems the logical place will be to parse it here. Otherwise the rest of the application becomes more
          complex. Using markdown will have the benefit of the output being a single html string with proper
          formatting.

    todo: change parameters {{ param }} to hello: '%{msg} world'
          see: http://kazupon.github.io/vue-i18n/guide/formatting.html#list-formatting
          The change is very large we don't need to do that, as we don't need those sentences.

    The content is added to the 'internet_nl' key, like this:

    const internet_nl_messages = {
        en: {
            internet_nl: {
                key: 'value',
                key: 'value'

            },
        },
    }

    There is a slight challenge that translations in vue are based on javascript properties, meaning, no quotes.

    :param translated_locales: List that holds a dict with the locale name, and the associated content.
    :return:
    """

    content = _vue_format_start()
    for item in translated_locales:
        content += _vue_format_locale_start(item['locale'])

        for entry in item['content']:
            # to save a boatload of data, we're not storing the 'content' from the pages of internet.nl
            # we'll just have to point to this content.
            if entry.msgid.endswith('content'):
                continue

            content += "            %s: '%s'," % (_js_safe_msgid(entry.msgid),
                                                  _js_safe_msgstr(entry.msgstr)) + '\n'
        content += _vue_format_locale_end()
    content += _vue_format_end()

    return content


def _vue_format_start():
    return """const internet_nl_messages = {
"""


def _vue_format_locale_start(locale):
    return """    %s: {
        internet_nl: {
""" % locale


def _vue_format_locale_end():
    return """        },
    },
"""


def _vue_format_end():
    return """};"""


def _js_safe_msgid(text):
    return slugify(text).replace('-', '_')


def _js_safe_msgstr(msgstr):
    # a poor mans escape for single quotes.
    msgstr = msgstr.replace("'", "\\\'")
    html = markdown.markdown(msgstr)
    one_line_html = html.replace('\n', '')

    # as happening on internet.nl, if the line is just a single paragraph, the paragraph tags are removed.
    # this is convenient for use in labels etc, that have their own markup.
    # see: https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/bin/pofiles.py
    one_line_html = _strip_simple_item(one_line_html, 'p')

    return one_line_html


def _strip_simple_item(text, html_tag):

    if text.startswith("<%s>" % html_tag) and text.endswith("</%s>" % html_tag):
        # Opening: <> and closing: </>
        len_opening_tag = len(html_tag) + 2
        len_closing_tag = len_opening_tag + 1

        return text[len_opening_tag:len(text)-len_closing_tag]

    return text


def store_vue_i18n_file(filename: str, content: str) -> None:
    """
    Temporarily the files are stored at: ~/dashboard/internet_nl_dashboard/static/translation/[locale].vue until we
    know how the vue include system works.

    :param filename:
    :param content:
    :return:
    """

    filepath = "%s%s.js" % (VUE_I18N_OUTPUT_PATH, filename)

    with open(filepath, 'w') as f:
        f.write(content)
