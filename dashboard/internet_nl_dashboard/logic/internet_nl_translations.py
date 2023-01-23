# SPDX-License-Identifier: Apache-2.0
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Union

import markdown
import polib
import requests
from django.utils.text import slugify

# Todo: refactor this to languages from settings.py
SUPPORTED_LOCALES: List[str] = ['nl', 'en']

log = logging.getLogger(__package__)

# .parent = logic; .parent.parent = internet_nl_dashboard;
DASHBOARD_APP_DIRECTORY = Path(__file__).parent.parent
VUE_I18N_OUTPUT_PATH = f'{DASHBOARD_APP_DIRECTORY}/static/js/translations/'
DJANGO_I18N_OUTPUT_PATH = f"{DASHBOARD_APP_DIRECTORY}/locale/"
# log.debug(f"VUE_I18N_OUTPUT_PATH: {VUE_I18N_OUTPUT_PATH}")
# log.debug(f"DJANGO_I18N_OUTPUT_PATH: {DJANGO_I18N_OUTPUT_PATH}")


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
    done: how to load languages dynamically in vue i18s? Could there be a callback or something?

    :return: None
    """

    translated_locales: List[Dict[str, Union[str, List[Any]]]] = []
    combined_vue_i18n_content = ""

    for locale in SUPPORTED_LOCALES:
        raw_content: bytes = get_locale_content(locale)
        store_as_django_locale(locale, raw_content)
        structured_content = load_as_po_file(raw_content)
        translated_locales.append({'locale': locale, 'content': structured_content})

        # support a per-language kind of file, in case we're going to do dynamic loading of languages.
        vue_i18n_content: str = convert_vue_i18n_format(locale, structured_content)
        combined_vue_i18n_content += vue_i18n_content
        store_vue_i18n_file(f'internet_nl.{locale}', vue_i18n_content)

    # the locales are easiest stored together. This makes language switching a lot easier.
    store_vue_i18n_file('internet_nl', combined_vue_i18n_content)


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

    url = f"https://raw.githubusercontent.com/NLnetLabs/Internet.nl/master/translations/{locale}/main.po"
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
    filepath = f"{DJANGO_I18N_OUTPUT_PATH}{locale}/LC_MESSAGES/django.po"

    # If the language does not exist yet, make the folder supporting this language.
    os.makedirs(Path(filepath).parent, exist_ok=True)

    with open(filepath, 'w') as file:
        file.write(content.decode('UTF-8'))


def load_as_po_file(raw_content: bytes) -> List[Any]:
    """
    The POfile library requires a file to exist, so we create a temporary one that will be read and parsed.
    The parsed content will be returned.

    See here how that works:
    https://bitbucket.org/izi/polib/wiki/Home

    :param raw_content: string that contains the contents of a .po file.
    :return:
    """
    with tempfile.NamedTemporaryFile() as file:
        file.write(raw_content)
        file.flush()
        return polib.pofile(file.name)


def convert_vue_i18n_format(locale: str, po_content: Any) -> str:
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

    :return:
    """

    content: str = _vue_format_start()

    content += _vue_format_locale_start(locale)

    for entry in po_content:
        # to save a boatload of data, we're not storing the 'content' from the pages of internet.nl
        # we'll just have to point to this content.
        if entry.msgid.endswith('content'):
            continue

        content += f"            {_js_safe_msgid(entry.msgid)}: '{_js_safe_msgstr(entry.msgstr)}',\n"
    content += _vue_format_locale_end()
    content += _vue_format_end()

    return content


def get_po_as_dictionary(file):
    structured_content = polib.pofile(file)
    po_file_as_dictionary = {}
    for entry in structured_content:
        if entry.msgid.endswith('content'):
            continue
        po_file_as_dictionary[_js_safe_msgid(entry.msgid)] = _js_safe_msgstr(entry.msgstr)

    return po_file_as_dictionary


def get_po_as_dictionary_v2(language='en'):
    """Much easier to use with only the language parameters and no magic or miserable path stuff."""

    po_file_location = f"{DJANGO_I18N_OUTPUT_PATH}{language}/LC_MESSAGES/django.po"
    try:
        log.debug(f"Loading locale file: {po_file_location}")
        return get_po_as_dictionary(po_file_location)
    except OSError as error:
        raise SystemError(f"Missing PO file 'django.po' at {po_file_location}. Note that an exception about "
                          f"incorrect syntax may be misleading. This is also given when there is no file. "
                          f"The exception that is given: {error}. Is this language available?") from error


def _vue_format_start() -> str:
    return """const internet_nl_messages = {
"""


def _vue_format_locale_start(locale) -> str:
    return """    %s: {
        internet_nl: {
""" % locale


def _vue_format_locale_end() -> str:
    return """        },
    },
"""


def _vue_format_end() -> str:
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

    if text.startswith(f"<{html_tag}>") and text.endswith(f"</{html_tag}>"):
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
    with open(f"{VUE_I18N_OUTPUT_PATH}{filename}.js", 'w') as file:
        file.write(content)


def translate_field(field_label, translation_dictionary: Dict[str, str]):
    """
    Try to solve the very inconsistent naming from the internet.nl translations (random dashes, case mixes etc)

    :param field_label:
    :param translation_dictionary allows you to use several dictionaries, for example an English or Dutch one. You
    can get this from get_po_as_dictionary_v2.
    :return:
    """
    field_mapping = {
        # mail fields, see dashboard.js
        'internet_nl_mail_starttls_cert_domain': 'detail_mail_tls_cert_hostmatch_label',
        'internet_nl_mail_starttls_tls_version': 'detail_mail_tls_version_label',
        'internet_nl_mail_starttls_cert_chain': 'detail_mail_tls_cert_trust_label',
        'internet_nl_mail_starttls_tls_available': 'detail_mail_tls_starttls_exists_label',
        'internet_nl_mail_starttls_tls_clientreneg': 'detail_mail_tls_renegotiation_client_label',
        'internet_nl_mail_starttls_tls_ciphers': 'detail_mail_tls_ciphers_label',
        'internet_nl_mail_starttls_dane_valid': 'detail_mail_tls_dane_valid_label',
        'internet_nl_mail_starttls_dane_exist': 'detail_mail_tls_dane_exists_label',
        'internet_nl_mail_starttls_tls_secreneg': 'detail_mail_tls_renegotiation_secure_label',
        'internet_nl_mail_starttls_dane_rollover': 'detail_mail_tls_dane_rollover_label',
        'internet_nl_mail_starttls_cert_pubkey': 'detail_mail_tls_cert_pubkey_label',
        'internet_nl_mail_starttls_cert_sig': 'detail_mail_tls_cert_signature_label',
        'internet_nl_mail_starttls_tls_compress': 'detail_mail_tls_compression_label',
        'internet_nl_mail_starttls_tls_keyexchange': 'detail_mail_tls_fs_params_label',
        'internet_nl_mail_auth_dmarc_policy': 'detail_mail_auth_dmarc_policy_label',
        'internet_nl_mail_auth_dmarc_exist': 'detail_mail_auth_dmarc_label',
        'internet_nl_mail_auth_spf_policy': 'detail_mail_auth_spf_policy_label',
        'internet_nl_mail_auth_dkim_exist': 'detail_mail_auth_dkim_label',
        'internet_nl_mail_auth_spf_exist': 'detail_mail_auth_spf_label',
        'internet_nl_mail_dnssec_mailto_exist': 'detail_mail_dnssec_exists_label',
        'internet_nl_mail_dnssec_mailto_valid': 'detail_mail_dnssec_valid_label',
        'internet_nl_mail_dnssec_mx_valid': 'detail_mail_dnssec_mx_valid_label',
        'internet_nl_mail_dnssec_mx_exist': 'detail_mail_dnssec_mx_exists_label',
        'internet_nl_mail_ipv6_mx_address': 'detail_mail_ipv6_mx_aaaa_label',
        'internet_nl_mail_ipv6_mx_reach': 'detail_mail_ipv6_mx_reach_label',
        'internet_nl_mail_ipv6_ns_reach': 'detail_web_mail_ipv6_ns_reach_label',
        'internet_nl_mail_ipv6_ns_address': 'detail_web_mail_ipv6_ns_aaaa_label',
        'internet_nl_mail_starttls_tls_cipherorder': 'detail_mail_tls_cipher_order_label',
        'internet_nl_mail_starttls_tls_keyexchangehash': 'detail_mail_tls_kex_hash_func_label',
        'internet_nl_mail_starttls_tls_0rtt': 'detail_mail_tls_zero_rtt_label',
        'internet_nl_mail_rpki_exists': 'detail_mail_rpki_exists_label',
        'internet_nl_mail_rpki_valid': 'detail_mail_rpki_valid_label',
        'internet_nl_mail_ns_rpki_exists': 'detail_web_mail_rpki_ns_exists_label',
        'internet_nl_mail_ns_rpki_valid': 'detail_web_mail_rpki_ns_valid_label',
        'internet_nl_mail_mx_ns_rpki_exists': 'detail_mail_rpki_mx_ns_exists_label',
        'internet_nl_mail_mx_ns_rpki_valid': 'detail_mail_rpki_mx_ns_valid_label',


        # web fields, see dashboard.js
        'internet_nl_web_appsecpriv': 'results_domain_appsecpriv_http_headers_label',
        'internet_nl_web_appsecpriv_csp': 'detail_web_appsecpriv_http_csp_label',
        'internet_nl_web_appsecpriv_referrer_policy': 'detail_web_appsecpriv_http_referrer_policy_label',
        'internet_nl_web_appsecpriv_x_content_type_options': 'detail_web_appsecpriv_http_x_content_type_label',
        'internet_nl_web_appsecpriv_x_frame_options': 'detail_web_appsecpriv_http_x_frame_label',
        'internet_nl_web_appsecpriv_securitytxt': 'detail_web_appsecpriv_http_securitytxt_label',
        'internet_nl_web_https_cert_domain': 'detail_web_tls_cert_hostmatch_label',
        'internet_nl_web_https_http_redirect': 'detail_web_tls_https_forced_label',
        'internet_nl_web_https_cert_chain': 'detail_web_tls_cert_trust_label',
        'internet_nl_web_https_tls_version': 'detail_web_tls_version_label',
        'internet_nl_web_https_tls_clientreneg': 'detail_web_tls_renegotiation_client_label',
        'internet_nl_web_https_tls_ciphers': 'detail_web_tls_ciphers_label',
        'internet_nl_web_https_http_available': 'detail_web_tls_https_exists_label',
        'internet_nl_web_https_dane_exist': 'detail_web_tls_dane_exists_label',
        'internet_nl_web_https_http_compress': 'detail_web_tls_http_compression_label',
        'internet_nl_web_https_http_hsts': 'detail_web_tls_https_hsts_label',
        'internet_nl_web_https_tls_secreneg': 'detail_web_tls_renegotiation_secure_label',
        'internet_nl_web_https_dane_valid': 'detail_web_tls_dane_valid_label',
        'internet_nl_web_https_cert_pubkey': 'detail_web_tls_cert_pubkey_label',
        'internet_nl_web_https_cert_sig': 'detail_web_tls_cert_signature_label',
        'internet_nl_web_https_tls_compress': 'detail_web_tls_compression_label',
        'internet_nl_web_https_tls_keyexchange': 'detail_web_tls_fs_params_label',
        'internet_nl_web_dnssec_valid': 'detail_web_dnssec_valid_label',
        'internet_nl_web_dnssec_exist': 'detail_web_dnssec_exists_label',
        'internet_nl_web_ipv6_ws_similar': 'detail_web_ipv6_web_ipv46_label',
        'internet_nl_web_ipv6_ws_address': 'detail_web_ipv6_web_aaaa_label',
        'internet_nl_web_ipv6_ns_reach': 'detail_web_mail_ipv6_ns_reach_label',
        'internet_nl_web_ipv6_ws_reach': 'detail_web_ipv6_web_reach_label',
        'internet_nl_web_ipv6_ns_address': 'detail_web_mail_ipv6_ns_aaaa_label',
        'internet_nl_web_https_tls_cipherorder': 'detail_web_tls_cipher_order_label',
        'internet_nl_web_https_tls_0rtt': 'detail_web_tls_zero_rtt_label',
        'internet_nl_web_https_tls_ocsp': 'detail_web_tls_ocsp_stapling_label',
        'internet_nl_web_https_tls_keyexchangehash': 'detail_web_tls_kex_hash_func_label',
        'internet_nl_web_rpki_exists': 'detail_web_rpki_exists_label',
        'internet_nl_web_rpki_valid': 'detail_web_rpki_valid_label',
        'internet_nl_web_ns_rpki_exists': 'detail_web_mail_rpki_ns_exists_label',
        'internet_nl_web_ns_rpki_valid': 'detail_web_mail_rpki_ns_valid_label',

        'internet_nl_web_rpki': 'test_siterpki_label',
        'internet_nl_web_tls': 'test_sitetls_label',
        'internet_nl_web_dnssec': 'test_sitednssec_label',
        'internet_nl_web_ipv6': 'test_siteipv6_label',

        'internet_nl_mail_dashboard_tls': 'test_mailtls_label',
        'internet_nl_mail_dashboard_auth': 'test_mailauth_label',
        'internet_nl_mail_dashboard_dnssec': 'test_maildnssec_label',
        'internet_nl_mail_dashboard_ipv6': 'test_mailipv6_label',
        'internet_nl_mail_dashboard_rpki': 'test_mailrpki_label',

        'internet_nl_score': '% Score',
        'internet_nl_score_report': 'Report',

        # directly translated fields.
        'internet_nl_mail_legacy_dmarc': 'DMARC',
        'internet_nl_mail_legacy_dkim': 'DKIM',
        'internet_nl_mail_legacy_spf': 'SPF',
        'internet_nl_mail_legacy_dmarc_policy': 'DMARC policy',
        'internet_nl_mail_legacy_spf_policy': 'SPF policy',
        'internet_nl_mail_legacy_start_tls': 'STARTTLS',
        'internet_nl_mail_legacy_start_tls_ncsc': 'STARTTLS NCSC',
        'internet_nl_mail_legacy_dnssec_email_domain': 'DNSSEC e-mail domain',
        'internet_nl_mail_legacy_dnssec_mx': 'DNSSEC MX',
        'internet_nl_mail_legacy_dane': 'DANE',
        'internet_nl_mail_legacy_category_ipv6': 'IPv6',
        'internet_nl_mail_legacy_ipv6_nameserver': 'IPv6 nameserver',
        'internet_nl_mail_legacy_ipv6_mailserver': 'IPv6 mailserver',

        'internet_nl_web_legacy_dnssec': 'DNSSEC',
        'internet_nl_web_legacy_tls_available': 'TLS available',
        'internet_nl_web_legacy_tls_ncsc_web': 'TLS NCSC web',
        'internet_nl_web_legacy_https_enforced': 'HTTPS redirect',
        'internet_nl_web_legacy_hsts': 'HSTS',
        'internet_nl_web_legacy_category_ipv6': 'IPv6',
        'internet_nl_web_legacy_ipv6_nameserver': 'IPv6 nameserver',
        'internet_nl_web_legacy_ipv6_webserver': 'IPv6 webserver',
        # Deleted on request
        # 'internet_nl_web_legacy_dane': 'DANE',

        'internet_nl_web_legacy_tls_1_3': 'TLS 1.3 Support',
        'internet_nl_mail_legacy_mail_sending_domain': 'E-mail sending domain',
        'internet_nl_mail_legacy_mail_server_testable': 'Mail server testable',
        'internet_nl_mail_legacy_mail_server_reachable': 'Mail server reachable',
        'internet_nl_mail_legacy_domain_has_mx': 'Mail server has MX record',
        'internet_nl_mail_legacy_tls_1_3': 'TLS 1.3 Support',

        'legacy': 'Extra Fields',
        'internet_nl_mail_dashboard_overall_score': 'Score',
        'internet_nl_web_overall_score': 'Score',
    }

    # handle inconsistent naming and (why cannot i load something else than django.po?)
    try:
        return translation_dictionary.get(field_mapping[field_label], field_mapping[field_label])
    except KeyError:
        # This can happen when something is already translated and the translations overwrite the original values.
        # When the re-translation is applied, the fields have been replaced by the translations and thus cannot be found
        log.debug(f"Could not find a translation for {field_label}, returning the label as is.")
        return field_label
