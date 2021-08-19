from typing import Any, Dict

from django.utils import timezone


def operation_response(
        error: bool = False, success: bool = False, message: str = "", data: Dict = None
) -> Dict[str, Any]:
    return {'error': error,
            'success': success,
            'message': message,
            'state': "error" if error else "success",
            'data': data,
            'timestamp': timezone.now()
            }


# WARNING! ORDERING IS RELEVANT!
# Ordered sets of fields, that have a correct natural order that is maintained througout the application
# The ordering is used in the spreadsheet export. The way the fields are ordered is relevant.

WEB_OVERALL_FIELDS = [
    'internet_nl_score',
    'internet_nl_score_report',
]

WEB_IPV6_CATEGORY = ['internet_nl_web_ipv6']

WEB_IPV6_FIELDS = [
    'internet_nl_web_ipv6_ns_address',
    'internet_nl_web_ipv6_ns_reach',

    'internet_nl_web_ipv6_ws_address',
    'internet_nl_web_ipv6_ws_reach',
    'internet_nl_web_ipv6_ws_similar'
]

WEB_DNSSEC_CATEGORY = ['internet_nl_web_dnssec']

WEB_DNSSEC_FIELDS = [
    'internet_nl_web_dnssec_exist',
    'internet_nl_web_dnssec_valid',
]

WEB_TLS_CATEGORY = ['internet_nl_web_tls']

WEB_TLS_HTTP_FIELDS = [
    'internet_nl_web_https_http_available',
    'internet_nl_web_https_http_redirect',
    'internet_nl_web_https_http_compress',
    'internet_nl_web_https_http_hsts',
]

WEB_TLS_TLS_FIELDS = [
    'internet_nl_web_https_tls_version',
    'internet_nl_web_https_tls_ciphers',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_web_https_tls_cipherorder',
    'internet_nl_web_https_tls_keyexchange',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_web_https_tls_keyexchangehash',
    'internet_nl_web_https_tls_compress',
    'internet_nl_web_https_tls_secreneg',
    'internet_nl_web_https_tls_clientreneg',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_web_https_tls_0rtt',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_web_https_tls_ocsp',
]

WEB_TLS_CERTIFICATE_FIELDS = [
    'internet_nl_web_https_cert_chain',
    'internet_nl_web_https_cert_pubkey',
    'internet_nl_web_https_cert_sig',
    'internet_nl_web_https_cert_domain',
]

WEB_TLS_DANE_FIELDS = [
    'internet_nl_web_https_dane_exist',
    'internet_nl_web_https_dane_valid',
]

WEB_APPSECPRIV_CATEGORY = ['internet_nl_web_appsecpriv']

WEB_APPSECPRIV_FIELDS = [
    'internet_nl_web_appsecpriv_x_frame_options',
    'internet_nl_web_appsecpriv_x_content_type_options',
    'internet_nl_web_appsecpriv_csp',
    'internet_nl_web_appsecpriv_referrer_policy',
]

WEB_LEGACY_FIELDS = [
    'internet_nl_web_legacy_dnssec',
    'internet_nl_web_legacy_tls_available',
    'internet_nl_web_legacy_tls_ncsc_web',
    'internet_nl_web_legacy_https_enforced',
    'internet_nl_web_legacy_hsts',
    # api 2.0 extra fields
    'internet_nl_web_legacy_category_ipv6',
    'internet_nl_web_legacy_ipv6_nameserver',
    'internet_nl_web_legacy_ipv6_webserver',
    # Deleted on request
    # 'internet_nl_web_legacy_dane',

    # added may 2020, api v2
    'internet_nl_web_legacy_tls_1_3',
]

MAIL_OVERALL_FIELDS = WEB_OVERALL_FIELDS

MAIL_IPV6_CATEGORY = ['internet_nl_mail_dashboard_ipv6']

MAIL_IPV6_FIELDS = [

    # name servers
    'internet_nl_mail_ipv6_ns_address',
    'internet_nl_mail_ipv6_ns_reach',

    # mail server(s)
    'internet_nl_mail_ipv6_mx_address',
    'internet_nl_mail_ipv6_mx_reach',
]

MAIL_DNSSEC_CATEGORY = ['internet_nl_mail_dashboard_dnssec']

MAIL_DNSSEC_FIELDS = [
    # email address domain
    'internet_nl_mail_dnssec_mailto_exist',
    'internet_nl_mail_dnssec_mailto_valid',

    # mail server domain(s)
    'internet_nl_mail_dnssec_mx_exist',
    'internet_nl_mail_dnssec_mx_valid',
]

MAIL_AUTH_CATEGORY = ['internet_nl_mail_dashboard_auth']

MAIL_AUTH_FIELDS = [

    # DMARC
    'internet_nl_mail_auth_dmarc_exist',
    'internet_nl_mail_auth_dmarc_policy',
    # 'internet_nl_mail_auth_dmarc_policy_only',  # Added 24th of May 2019
    # 'internet_nl_mail_auth_dmarc_ext_destination',  # Added 24th of May 2019

    # DKIM
    'internet_nl_mail_auth_dkim_exist',

    # SPF
    'internet_nl_mail_auth_spf_exist',
    'internet_nl_mail_auth_spf_policy',

]

MAIL_TLS_CATEGORY = ['internet_nl_mail_dashboard_tls']

MAIL_TLS_TLS_FIELDS = [
    'internet_nl_mail_starttls_tls_available',
    'internet_nl_mail_starttls_tls_version',
    'internet_nl_mail_starttls_tls_ciphers',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_mail_starttls_tls_cipherorder',
    'internet_nl_mail_starttls_tls_keyexchange',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_mail_starttls_tls_keyexchangehash',
    'internet_nl_mail_starttls_tls_compress',
    'internet_nl_mail_starttls_tls_secreneg',
    'internet_nl_mail_starttls_tls_clientreneg',
    # api 2.0 tls 1.3 fields, may 2020
    'internet_nl_mail_starttls_tls_0rtt',
]

MAIL_TLS_CERTIFICATE_FIELDS = [
    'internet_nl_mail_starttls_cert_chain',
    'internet_nl_mail_starttls_cert_pubkey',
    'internet_nl_mail_starttls_cert_sig',
    'internet_nl_mail_starttls_cert_domain',
]

MAIL_TLS_DANE_FIELDS = [
    'internet_nl_mail_starttls_dane_exist',
    'internet_nl_mail_starttls_dane_valid',
    'internet_nl_mail_starttls_dane_rollover',
]

MAIL_LEGACY_FIELDS = [
    'internet_nl_mail_legacy_dmarc',
    'internet_nl_mail_legacy_dkim',
    'internet_nl_mail_legacy_spf',
    'internet_nl_mail_legacy_dmarc_policy',
    'internet_nl_mail_legacy_spf_policy',
    'internet_nl_mail_legacy_start_tls',
    'internet_nl_mail_legacy_start_tls_ncsc',
    'internet_nl_mail_legacy_dnssec_email_domain',
    'internet_nl_mail_legacy_dnssec_mx',
    'internet_nl_mail_legacy_dane',
    'internet_nl_mail_legacy_category_ipv6',
    'internet_nl_mail_legacy_ipv6_nameserver',
    'internet_nl_mail_legacy_ipv6_mailserver',

    # Added may 2020 internet.nl api v2
    'internet_nl_mail_legacy_mail_non_sending_domain',
    'internet_nl_mail_legacy_mail_sending_domain',
    'internet_nl_mail_legacy_mail_server_testable',
    'internet_nl_mail_legacy_mail_server_reachable',
    'internet_nl_mail_legacy_domain_has_mx',
    'internet_nl_mail_legacy_tls_1_3',
]

# Obsoleted metrics:
# 'internet_nl_mail_non_sending_domain',  # Added 24th of May 2019
# 'internet_nl_mail_server_configured',  # Added 24th of May 2019
# 'internet_nl_mail_servers_testable',  # Added 24th of May 2019
# 'internet_nl_mail_starttls_dane_ta',  # Added 24th of May 2019
# 'internet_nl_mail_auth_dmarc_policy_only',  # Added 24th of May 2019
# 'internet_nl_mail_auth_dmarc_ext_destination',  # Added 24th of May 2019

MAIL_CATEGORIES = MAIL_IPV6_CATEGORY + MAIL_DNSSEC_CATEGORY + MAIL_AUTH_CATEGORY + MAIL_TLS_CATEGORY
