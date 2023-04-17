# SPDX-License-Identifier: Apache-2.0
"""
Run these tests with tox -e test -- -k test_translation
"""
from pathlib import Path
from unittest import mock

from requests import Response

from dashboard.internet_nl_dashboard.logic.internet_nl_translations import (convert_vue_i18n_format, get_locale_content,
                                                                            get_po_as_dictionary_v2, load_as_po_file,
                                                                            translate_field)

path = Path(__file__).parent


# Create the desired normal response, by simply forcing the correct properties to be present.
# This is probably not the way to do it, yet i found the other methods be mostly obscure.
perfect_response = Response()
perfect_response._content = "yolo"


def file_get_contents(filepath):
    with open(filepath, 'r') as content_file:
        return content_file.read()


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

    if args[0] == 'https://raw.githubusercontent.com/NLnetLabs/Internet.nl/master/translations/nl/main.po':
        return MockResponse(file_get_contents(f'{path}/translation files/main.po').encode(), 200)

    return MockResponse(None, 404)


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_urllists(db, tmpdir) -> None:

    content = get_locale_content('nl')
    assert len(content) > 1000

    list_po_content = load_as_po_file(content)
    assert len(list_po_content) > 10

    formatted = convert_vue_i18n_format('nl', list_po_content)
    assert len(formatted) > 1000

    # create the expected directory structure
    # doesn't understand parents=true, even though it's python 3.6... LocalPath is a mute version of the system one?
    # It's terrible, so we have to write the directory structure ourselves, as if we are living in the 90's.
    # tmpdir.mkdir(OUTPUT_PATH, exist_ok=True)
    # there is no way this would be the 'go to' solution, as it's just plain stupid (realpath should be pwd or smthng)
    # import subprocess
    # subprocess.check_output(['mkdir', '-p', '%s%s' % (tmpdir.cwd(), OUTPUT_PATH)])

    # verify that this does not create a file in the filesystem, but only in the test environment.
    # store_vue_i18n_file('nl', formatted)


def test_field_translation():
    # Load dutch translation for a field
    translation_dictionary = get_po_as_dictionary_v2('nl')
    translated = translate_field('internet_nl_web_https_tls_version', translation_dictionary=translation_dictionary)
    assert translated == "TLS-versie"

    # Now verify that we can live switch to an english translation
    translation_dictionary = get_po_as_dictionary_v2('en')
    translated = translate_field('internet_nl_web_https_tls_version', translation_dictionary=translation_dictionary)
    assert translated == "TLS version"

    # And switch back to dutch again
    translation_dictionary = get_po_as_dictionary_v2('nl')
    translated = translate_field('internet_nl_web_https_tls_version', translation_dictionary=translation_dictionary)
    assert translated == "TLS-versie"
