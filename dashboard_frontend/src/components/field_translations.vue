<script>
const internet_nl_field_mapping = {
    internet_nl_web_tls: 'test_sitetls',
    internet_nl_web_dnssec: 'test_sitednssec',
    internet_nl_web_ipv6: 'test_siteipv6',

    internet_nl_mail_dashboard_tls: 'test_mailtls',
    internet_nl_mail_dashboard_auth: 'test_mailauth',
    internet_nl_mail_dashboard_dnssec: 'test_maildnssec',
    internet_nl_mail_dashboard_ipv6: 'test_mailipv6',

    internet_nl_web_appsecpriv: 'test_siteappsecpriv',
    internet_nl_web_appsecpriv_csp: 'detail_web_appsecpriv_http_csp',
    internet_nl_web_appsecpriv_referrer_policy: 'detail_web_appsecpriv_http_referrer_policy',
    internet_nl_web_appsecpriv_x_content_type_options: 'detail_web_appsecpriv_http_x_content_type',
    internet_nl_web_appsecpriv_x_frame_options: 'detail_web_appsecpriv_http_x_frame',
    internet_nl_web_https_cert_domain: 'detail_web_tls_cert_hostmatch',
    internet_nl_web_https_http_redirect: 'detail_web_tls_https_forced',
    internet_nl_web_https_cert_chain: 'detail_web_tls_cert_trust',
    internet_nl_web_https_tls_version: 'detail_web_tls_version',
    internet_nl_web_https_tls_clientreneg: 'detail_web_tls_renegotiation_client',
    internet_nl_web_https_tls_ciphers: 'detail_web_tls_ciphers',
    internet_nl_web_https_http_available: 'detail_web_tls_https_exists',
    internet_nl_web_https_dane_exist: 'detail_web_tls_dane_exists',
    internet_nl_web_https_http_compress: 'detail_web_tls_http_compression',
    internet_nl_web_https_http_hsts: 'detail_web_tls_https_hsts',
    internet_nl_web_https_tls_secreneg: 'detail_web_tls_renegotiation_secure',
    internet_nl_web_https_dane_valid: 'detail_web_tls_dane_valid',
    internet_nl_web_https_cert_pubkey: 'detail_web_tls_cert_pubkey',
    internet_nl_web_https_cert_sig: 'detail_web_tls_cert_signature',
    internet_nl_web_https_tls_compress: 'detail_web_tls_compression',
    internet_nl_web_https_tls_keyexchange: 'detail_web_tls_fs_params',
    internet_nl_web_dnssec_valid: 'detail_web_dnssec_valid',
    internet_nl_web_dnssec_exist: 'detail_web_dnssec_exists',
    internet_nl_web_ipv6_ws_similar: 'detail_web_ipv6_web_ipv46',
    internet_nl_web_ipv6_ws_address: 'detail_web_ipv6_web_aaaa',
    internet_nl_web_ipv6_ns_reach: 'detail_web_mail_ipv6_ns_reach',
    internet_nl_web_ipv6_ws_reach: 'detail_web_ipv6_web_reach',
    internet_nl_web_ipv6_ns_address: 'detail_web_mail_ipv6_ns_aaaa',

    // added with api 2.0.0
    internet_nl_web_https_tls_cipherorder: 'detail_web_tls_cipher_order',
    internet_nl_web_https_tls_0rtt: 'detail_web_tls_zero_rtt',
    internet_nl_web_https_tls_ocsp: 'detail_web_tls_ocsp_stapling',
    internet_nl_web_https_tls_keyexchangehash: 'detail_web_tls_kex_hash_func',

    internet_nl_mail_starttls_cert_domain: 'detail_mail_tls_cert_hostmatch',
    internet_nl_mail_starttls_tls_version: 'detail_mail_tls_version',
    internet_nl_mail_starttls_cert_chain: 'detail_mail_tls_cert_trust',
    internet_nl_mail_starttls_tls_available: 'detail_mail_tls_starttls_exists',
    internet_nl_mail_starttls_tls_clientreneg: 'detail_mail_tls_renegotiation_client',
    internet_nl_mail_starttls_tls_ciphers: 'detail_mail_tls_ciphers',
    internet_nl_mail_starttls_dane_valid: 'detail_mail_tls_dane_valid',
    internet_nl_mail_starttls_dane_exist: 'detail_mail_tls_dane_exists',
    internet_nl_mail_starttls_tls_secreneg: 'detail_mail_tls_renegotiation_secure',
    internet_nl_mail_starttls_dane_rollover: 'detail_mail_tls_dane_rollover',
    internet_nl_mail_starttls_cert_pubkey: 'detail_mail_tls_cert_pubkey',
    internet_nl_mail_starttls_cert_sig: 'detail_mail_tls_cert_signature',
    internet_nl_mail_starttls_tls_compress: 'detail_mail_tls_compression',
    internet_nl_mail_starttls_tls_keyexchange: 'detail_mail_tls_fs_params',
    internet_nl_mail_auth_dmarc_policy: 'detail_mail_auth_dmarc_policy',
    internet_nl_mail_auth_dmarc_exist: 'detail_mail_auth_dmarc',
    internet_nl_mail_auth_spf_policy: 'detail_mail_auth_spf_policy',
    internet_nl_mail_auth_dkim_exist: 'detail_mail_auth_dkim',
    internet_nl_mail_auth_spf_exist: 'detail_mail_auth_spf',
    internet_nl_mail_dnssec_mailto_exist: 'detail_mail_dnssec_exists',
    internet_nl_mail_dnssec_mailto_valid: 'detail_mail_dnssec_valid',
    internet_nl_mail_dnssec_mx_valid: 'detail_mail_dnssec_mx_valid',
    internet_nl_mail_dnssec_mx_exist: 'detail_mail_dnssec_mx_exists',
    internet_nl_mail_ipv6_mx_address: 'detail_mail_ipv6_mx_aaaa',
    internet_nl_mail_ipv6_mx_reach: 'detail_mail_ipv6_mx_reach',
    internet_nl_mail_ipv6_ns_reach: 'detail_web_mail_ipv6_ns_reach',
    internet_nl_mail_ipv6_ns_address: 'detail_web_mail_ipv6_ns_aaaa',

    // added with api2.0
    internet_nl_mail_starttls_tls_cipherorder: 'detail_mail_tls_cipher_order',
    internet_nl_mail_starttls_tls_keyexchangehash: 'detail_mail_tls_kex_hash_func',
    internet_nl_mail_starttls_tls_0rtt: 'detail_mail_tls_zero_rtt',

    // categories and such
    web: 'base_test_website',
    category_web_ipv6_name_server: 'results_domain_mail_ipv6_name_servers',
    category_web_ipv6_web_server: 'results_domain_ipv6_web_server',
    category_web_dnssec_dnssec: 'test_sitednssec',
    category_web_tls_http: 'results_domain_tls_https',
    category_web_tls_tls: 'results_domain_tls_tls',
    category_web_tls_certificate: 'results_domain_mail_tls_certificate',
    category_web_tls_dane: 'results_domain_mail_tls_dane',
    category_web_security_options_appsecpriv: 'results_domain_appsecpriv_http_headers',
    mail: 'base_test_mail',
    category_mail_ipv6_name_servers: 'results_domain_mail_ipv6_name_servers',
    category_mail_ipv6_mail_servers: 'results_mail_ipv6_mail_servers',
    category_mail_dnssec_email_address_domain: 'results_mail_dnssec_domain',
    category_mail_dnssec_mail_server_domain: 'results_mail_dnssec_mail_servers',
    category_mail_dashboard_auth_dmarc: 'results_mail_auth_dmarc',
    category_mail_dashboard_aut_dkim: 'results_mail_auth_dkim',
    category_mail_dashboard_aut_spf: 'results_mail_auth_spf',
    category_mail_starttls_tls: 'results_mail_tls_starttls',
    category_mail_starttls_certificate: 'results_domain_mail_tls_certificate',
    category_mail_starttls_dane: 'results_domain_mail_tls_dane',
};

const additional_mapping = {
    test_title: 'faqs_report_test_title',
    test_good: 'faqs_report_test_good',
    test_bad: 'faqs_report_test_bad',
    test_warning: 'faqs_report_test_warning',
    test_info: 'faqs_report_test_info',
    subtest_title: 'faqs_report_subtest_title',
    subtest_good: 'faqs_report_subtest_good',
    subtest_bad: 'faqs_report_subtest_bad',
    subtest_warning: 'faqs_report_subtest_warning',
    subtest_info: 'faqs_report_subtest_info',
}


// categories are translated with _passed_summary or _failed_summary. The rest with their label. Should be in
// the retrieved translations anyway.
function import_field_translations(internet_nl_messages, language) {
    let mapping = {};
    for (let key of Object.keys(internet_nl_field_mapping)) {
        mapping[key] = internet_nl_messages[language].internet_nl[internet_nl_field_mapping[key] + '_label']
    }
    for (let key of Object.keys(additional_mapping)) {
        mapping[key] = internet_nl_messages[language].internet_nl[additional_mapping[key]]
    }
    return mapping;
}

function interpolate_translations(internet_nl_messages) {
    let translation = {
        'en': {
            fields: {
                forum_standardistation: {
                    category_label: 'Extra Fields',
                    measurements_on_agreed_security_standards: 'Extra Fields',
                    ipv6_monitor: 'IPv6 monitor',
                    status_fields: 'Status Fields',
                },
                additional_fields: {
                    label: 'Additional fields',
                },
            },

            mail_legacy: 'Extra Fields',
            web_legacy: 'Extra Fields',

            internet_nl_mail_legacy_dmarc: 'DMARC',
            internet_nl_mail_legacy_dmarc_explanation: 'Calculated by using the value from: mail_auth_dkim_exist.',
            internet_nl_mail_legacy_dkim: 'DKIM',
            internet_nl_mail_legacy_dkim_explanation: 'Calculated by using the value from: mail_auth_dkim_exist if it passes. If that\'s not available, see if the domain sends e-mail. If it does not, it\'s not applicable. Otherwise this fails.',
            internet_nl_mail_legacy_spf: 'SPF',
            internet_nl_mail_legacy_spf_explanation: 'Calculated by using the value from: mail_auth_spf_exist.',
            internet_nl_mail_legacy_dmarc_policy: 'DMARC policy',
            internet_nl_mail_legacy_dmarc_policy_explanation: 'Calculated by using the value from: mail_auth_dmarc_policy.',
            internet_nl_mail_legacy_spf_policy: 'SPF policy',
            internet_nl_mail_legacy_spf_policy_explanation: 'Calculated by using the value from: mail_auth_spf_policy.',
            internet_nl_mail_legacy_start_tls: 'STARTTLS',
            internet_nl_mail_legacy_start_tls_explanation: 'Calculated by using the value from: mail_starttls_tls_available. Can be overwritten by mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_start_tls_ncsc: 'STARTTLS NCSC',
            internet_nl_mail_legacy_start_tls_ncsc_explanation: 'Calculated by using the worst value from: mail_starttls_tls_available, ' +
                'mail_starttls_tls_keyexchange, mail_starttls_tls_compress, mail_starttls_tls_secreneg, ' +
                'mail_starttls_tls_ciphers, mail_starttls_tls_clientreneg,  mail_starttls_tls_version, ' +
                'mail_starttls_tls_cipherorder, mail_starttls_tls_keyexchangehash, mail_starttls_tls_0rtt, ' +
                'mail_starttls_cert_sig, mail_starttls_cert_pubkey, mail_starttls_cert_chain,  mail_starttls_cert_domain. ' +
                'Can be overwritten by mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_dnssec_mx: 'DNSSEC MX',
            internet_nl_mail_legacy_dnssec_mx_explanation: 'Calculated by using the worst value from: mail_dnssec_mx_exist, mail_dnssec_mx_valid. Will be set to no_mx if there is no mx.',
            internet_nl_mail_legacy_dane: 'DANE',
            internet_nl_mail_legacy_dane_explanation: 'Calculated by using the worst value from: mail_starttls_dane_exist, mail_starttls_dane_valid. Can be overwritten by mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_mail_legacy_ipv6_nameserver_explanation: 'Calculated by using the worst value from: mail_ipv6_ns_address, mail_ipv6_ns_reach. Will be set to no_mx if there is no mx.',
            internet_nl_mail_legacy_ipv6_mailserver: "IPv6 mailserver",
            internet_nl_mail_legacy_ipv6_mailserver_explanation: 'Calculated by using the worst value from: mail_ipv6_mx_address, mail_ipv6_mx_reach. Will be set to no_mx if there is no mx.',

            internet_nl_web_legacy_dnssec: 'DNSSEC',
            internet_nl_web_legacy_dnssec_explanation: 'Calculated by using the worst value from: web_dnssec_exist and web_dnssec_valid.',
            internet_nl_web_legacy_tls_available: 'TLS',
            internet_nl_web_legacy_tls_available_explanation: 'Calculated by using the value from: web_https_http_available.',
            internet_nl_web_legacy_tls_ncsc_web: 'TLS_NCSC',
            internet_nl_web_legacy_tls_ncsc_web_explanation: "Calculated by using the worst value from: web_https_tls_keyexchange, " +
                "web_https_tls_compress, web_https_tls_secreneg, web_https_tls_ciphers, web_https_tls_clientreneg, " +
                "web_https_tls_version, web_https_tls_cipherorder, web_https_tls_0rtt, web_https_tls_ocsp, " +
                "web_https_tls_keyexchangehash, web_https_cert_sig, web_https_cert_pubkey, web_https_cert_chain, web_https_cert_domain.",
            internet_nl_web_legacy_https_enforced: 'HTTPS redirect',
            internet_nl_web_legacy_https_enforced_explanation: 'Calculated by using the value from: web_https_http_redirect.',
            internet_nl_web_legacy_hsts: 'HSTS',
            internet_nl_web_legacy_hsts_explanation: 'Calculated by using the value from: web_https_http_hsts.',
            internet_nl_web_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_web_legacy_ipv6_nameserver_explanation: 'Calculated by using the worst value from: web_ipv6_ns_address and web_ipv6_ns_reach.',
            internet_nl_web_legacy_ipv6_webserver: 'IPv6 webserver',
            internet_nl_web_legacy_ipv6_webserver_explanation: 'Calculated by using the worst value from: web_ipv6_ws_address, web_ipv6_ws_reach and web_ipv6_ws_similar.',
            internet_nl_web_legacy_dane: 'DANE',
            internet_nl_web_legacy_dane_explanation: 'Calculated by using the worst value from: web_https_dane_exist and web_https_dane_valid.',

            // New extra fields in API 2.0
            internet_nl_web_legacy_tls_1_3: 'TLS 1.3 Support',
            internet_nl_mail_legacy_mail_non_sending_domain: 'Non e-mail sending domain',
            internet_nl_mail_legacy_mail_sending_domain: 'E-mail sending domain',
            internet_nl_mail_legacy_mail_server_testable: 'Mail server testable',
            internet_nl_mail_legacy_mail_server_reachable: 'Mail server reachable',
            internet_nl_mail_legacy_domain_has_mx: 'Mail server has MX record',
            internet_nl_mail_legacy_tls_1_3: 'TLS 1.3 Support',
            internet_nl_web_legacy_tls_1_3_explanation: 'Derives TLS1.3 support through the 0-RTT test. Explicitly testing for TLS1.3 support is not part of the compliance tool. However, TLS1.3 support could be derived from the 0-RTT test as the function is only available starting from TLS1.3. As there is no explicit TLS1.3 connection during testing, the test assumes that the server chose TLS1.3 when given the opportunity to do so.',
            internet_nl_mail_legacy_mail_non_sending_domain_explanation: 'Checks if the domain is configured for _not_ sending email. For this test this is translated as:\n' +
                '    SPF record with v=spf1 -all, and\n' +
                '    DMARC record with v=DMARC1;p=reject;.\n',
            internet_nl_mail_legacy_mail_sending_domain_explanation: 'Checks if the domain is configured for sending email. For this test this is translated as being the anything else than:\n' +
                '    SPF record with v=spf1 -all, and\n' +
                '    DMARC record with v=DMARC1;p=reject;.\n',
            internet_nl_mail_legacy_mail_server_testable_explanation: 'All mailservers communicated back and results are complete.',
            internet_nl_mail_legacy_mail_server_reachable_explanation: 'Network connectivity was possible with at least one mailserver.',
            internet_nl_mail_legacy_domain_has_mx_explanation: 'Mailservers are configured for the domain.',
            internet_nl_mail_legacy_tls_1_3_explanation: 'Derives TLS1.3 support through the 0-RTT test. Explicitly testing for TLS1.3 support is not part of the compliance tool. However, TLS1.3 support could be derived from the 0-RTT test as the function is only available starting from TLS1.3. As there is no explicit TLS1.3 connection during testing, the test assumes that the server chose TLS1.3 when given the opportunity to do so.',
            internet_nl_mail_legacy_category_ipv6: "IPv6 mail",
            internet_nl_web_legacy_category_ipv6: "IPv6 web",

            internet_nl_mail_legacy_category_ipv6_explanation: "Calculated by taken the category value for IPv6.",
            internet_nl_web_legacy_category_ipv6_explanation: "Calculated by taken the category value for IPv6.",

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
            internet_nl_mail_server_configured: 'Mail Server Configured (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_servers_testable: 'Mail Server Testable (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_starttls_dane_ta: 'Mail STARTTLS Dane TA (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_non_sending_domain: 'Mail Non Sending Domain (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_policy_only: 'Mail Auth DMARC Policy Only (not in UI)',   // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_ext_destination: 'Mail Auth DMARC Ext Destination (not in UI)',  // Added 24th of May 2019
        }, 'nl': {

            fields: {
                forum_standardistation: {
                    category_label: 'Extra Velden',
                    measurements_on_agreed_security_standards: 'Extra Velden',
                    ipv6_monitor: 'IPv6 monitor',
                    status_fields: 'Status Velden'
                },
                additional_fields: {
                    label: 'Additionele velden',
                },
            },

            mail_legacy: 'Extra Velden',
            web_legacy: 'Extra Velden',

            internet_nl_mail_legacy_dmarc: 'DMARC',
            internet_nl_mail_legacy_dmarc_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: mail_auth_dkim_exist.',
            internet_nl_mail_legacy_dkim: 'DKIM',
            internet_nl_mail_legacy_dkim_explanation: 'Berekend door de waarde het veld "mail_auth_dkim_exist" te gebruiken als deze passed is. Als dat niet zo is wordt er gekeken of het domein e-mail verstuurd, zo nee: dan is dit not_applicable. Zo wel dan faalt deze test.',
            internet_nl_mail_legacy_spf: 'SPF',
            internet_nl_mail_legacy_spf_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: mail_auth_spf_exist.',
            internet_nl_mail_legacy_dmarc_policy: 'DMARC policy',
            internet_nl_mail_legacy_dmarc_policy_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: mail_auth_dmarc_policy.',
            internet_nl_mail_legacy_spf_policy: 'SPF policy',
            internet_nl_mail_legacy_spf_policy_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: mail_auth_spf_policy.',
            internet_nl_mail_legacy_start_tls: 'STARTTLS',
            internet_nl_mail_legacy_start_tls_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: mail_starttls_tls_available. Kan overschreven worden door de mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_start_tls_ncsc: 'STARTTLS NCSC',
            internet_nl_mail_legacy_start_tls_ncsc_explanation: 'Wordt berekend door de slechtste waarde te gebruiken van de volgende velden: mail_starttls_tls_available, ' +
                'mail_starttls_tls_keyexchange, mail_starttls_tls_compress, mail_starttls_tls_secreneg, ' +
                'mail_starttls_tls_ciphers, mail_starttls_tls_clientreneg,  mail_starttls_tls_version, ' +
                'mail_starttls_tls_cipherorder, mail_starttls_tls_keyexchangehash, mail_starttls_tls_0rtt, ' +
                'mail_starttls_cert_sig, mail_starttls_cert_pubkey, mail_starttls_cert_chain,  mail_starttls_cert_domain. ' +
                'Kan overschreven worden door mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_dnssec_mx: 'DNSSEC MX',
            internet_nl_mail_legacy_dnssec_mx_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: mail_dnssec_mx_exist, mail_dnssec_mx_valid. Wordt op no_mx gezet als er geen mx is.',
            internet_nl_mail_legacy_dane: 'DANE',
            internet_nl_mail_legacy_dane_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: mail_starttls_dane_exist, mail_starttls_dane_valid. Kan overschreven worden door de mail_servers_testable_status (no_mx, unreachable, not_testable).',
            internet_nl_mail_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_mail_legacy_ipv6_nameserver_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: mail_ipv6_ns_address, mail_ipv6_ns_reach. Wordt op no_mx gezet als er geen mx is.',
            internet_nl_mail_legacy_ipv6_mailserver: "IPv6 mailserver",
            internet_nl_mail_legacy_ipv6_mailserver_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: mail_ipv6_mx_address, mail_ipv6_mx_reach. Wordt op no_mx gezet als er geen mx is.',

            internet_nl_web_legacy_dnssec: 'DNSSEC',
            internet_nl_web_legacy_dnssec_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: web_dnssec_exist, web_dnssec_valid.',
            internet_nl_web_legacy_tls_available: 'TLS',
            internet_nl_web_legacy_tls_available_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: web_https_http_available.',
            internet_nl_web_legacy_tls_ncsc_web: 'TLS_NCSC',
            internet_nl_web_legacy_tls_ncsc_web_explanation: "Wordt berekend door de slechtste waarde te gebruiken van de volgende velden: web_https_tls_keyexchange, " +
                "web_https_tls_compress, web_https_tls_secreneg, web_https_tls_ciphers, web_https_tls_clientreneg, " +
                "web_https_tls_version, web_https_tls_cipherorder, web_https_tls_0rtt, web_https_tls_ocsp, " +
                "web_https_tls_keyexchangehash, web_https_cert_sig, web_https_cert_pubkey, web_https_cert_chain, web_https_cert_domain.",
            internet_nl_web_legacy_https_enforced: 'HTTPS redirect',
            internet_nl_web_legacy_https_enforced_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: web_https_http_redirect.',
            internet_nl_web_legacy_hsts: 'HSTS',
            internet_nl_web_legacy_hsts_explanation: 'Berekend door de waarde van het volgende veld te gebruiken: web_https_http_hsts.',
            internet_nl_web_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_web_legacy_ipv6_nameserver_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: web_ipv6_ws_address, web_ipv6_ws_reach en web_ipv6_ws_similar.',
            internet_nl_web_legacy_ipv6_webserver: 'IPv6 webserver',
            internet_nl_web_legacy_ipv6_webserver_explanation: 'Berekend door de slechtste waarde van de volgende velden te gebruiken: web_https_dane_exist en web_https_dane_valid.',

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
            internet_nl_mail_server_configured: 'Mail Server Configured (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_servers_testable: 'Mail Server Testable (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_starttls_dane_ta: 'Mail STARTTLS Dane TA (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_non_sending_domain: 'Mail Non Sending Domain (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_policy_only: 'Mail Auth DMARC Policy Only (not in UI)',   // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_ext_destination: 'Mail Auth DMARC Ext Destination (not in UI)',  // Added 24th of May 2019


        }
    };

    translation.nl = Object.assign(translation.nl, import_field_translations(internet_nl_messages, 'nl'));
    translation.en = Object.assign(translation.en, import_field_translations(internet_nl_messages, 'en'));

    return translation;
}

import internet_nl_messages from './translations/internet_nl.js'

const sharedMessages = interpolate_translations(internet_nl_messages);
export default sharedMessages;
</script>