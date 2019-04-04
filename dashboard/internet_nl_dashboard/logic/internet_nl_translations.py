import tempfile
from typing import List

import markdown
import polib
import requests
from django.utils.text import slugify

SUPPORTED_LOCALES = ['nl', 'en']
OUTPUT_PATH = 'dashboard/internet_nl_dashboard/static/js/translations/'


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
    todo: how to dynamically support multiple languages? And how does the i18n object doesn't become insanely big?
    todo: should we merge all translation files into one? probably...

    :return: None
    """

    for locale in SUPPORTED_LOCALES:
        raw_content = get_locale_content(locale)
        structured_content = load_as_po_file(raw_content)
        vue_i18n_content = convert_vue_i18n_format(locale, structured_content)
        store_vue_i18n_file(locale, vue_i18n_content)


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


def load_as_po_file(raw_content: bytes) -> List[polib.POEntry]:
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


def convert_vue_i18n_format(locale: str, structured_content: List[polib.POEntry]) -> str:
    """
    todo: will markdown be parsed to html in this method? Or should we do that on the fly, everywhere...
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

    :param locale:
    :param structured_content:
    :return:
    """

    content = """
const internet_nl_messages = {
    %s: {
        internet_nl: {
""" % locale

    for entry in structured_content:
        content += "            %s: '%s'," % (_js_safe_msgid(entry.msgid),
                                              _js_safe_msgstr(entry.msgstr)) + '\n'

    content += """        },
    },
}
"""

    return content


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


def store_vue_i18n_file(locale: str, content: str) -> None:
    """
    Temporarily the files are stored at: ~/dashboard/internet_nl_dashboard/static/translation/[locale].vue until we
    know how the vue include system works.

    :param locale:
    :param content:
    :return:
    """

    filepath = "%s%s.vue" % (OUTPUT_PATH, locale)

    with open(filepath, 'w') as f:
        f.write(content)
