const messages = {
    en: {
        icons: {
            list_closed: "List closed",
            list_opened: "List opened",
            report: "report",
            settings: "settings",
            bulk_add_new: "Add domains in bulk",
            scan: "scan",
            can_connect: "Can connect icon",
            unknown_connectivity: "Unknown connectivity icon",
            cannot_connect: "Can not connect",
            remove_filter: 'Show categories'
        },
        menu: {
            admin: 'Admin',
            domains: "Domains",
            scans: "Scans",
            reports: "Reports",
            account: "Account",
            log_off: "Log off",
            log_in: "Log in",
        },
        loading: {
            loading: "Loading...",
        },
        domains: {
            add_new_list: 'Add new list',
            button_close_label: 'Close',
            button_create_list_label: 'Create List',
        },
        domain_management: {

            title: "Domains",
            intro: "Manage lists with domains",
            bulk_upload_link: "Upload large amount of data by using the Bulk Address uploader, here.",

            icon_legend: {
                title: "Legend of used icons",
                intro: "The domains in the lists below will be included in each scan. Before a scan is performed, the eligibility of the " +
                    "service is checked. This check is always performed for the scan. To give an insight in how connected" +
                    "these services are, the last known state is presented as the first icon.",
                can_connect: "Can connect to this service, will (probably) be scanned.",
                unknown_connectivity: "Unknown if this service is available, will be scanned if available.",
                cannot_connect: "Service not available, will (probably) not be scanned."
            },


            button_labels: {
                configure: 'Configure',
                add_domains: 'Add domains',
                scan_now: 'Scan now',
                scan_now_scanning: 'Scanning',
                scan_now_scanning_title: 'The scan now option is available only once a day, when no scan is running.',
                delete: 'Delete',
                view_csv: 'View .csv',
                timeout_for_24_hours: 'Max 1 scan/day',
                scanning_disabled: 'Scanning disabled',
            },

            about_this_list: {
                header: 'About this list',
                last_scan_started: 'Last scan started',
                still_running: 'still running',
                finished: 'finished',
                not_scanned_before: 'Not scanned before',
                type_of_scan_performed: 'Type of scan performed',
                scan_frequency: 'Scan frequency',
                next_scheduled_scan: 'Next scheduled scan',
                scanning_disabled: 'Scanning of this list is disabled.',
                latest_report: 'Latest report',
            },

            domains: {
                header: 'Domains',
                intro: "These domains will be included in the scan. Their eligibility for scanning is checked just " +
                    "before requesting the scan, the information shown here may be outdated.",
                start_editing_url: 'Edit {0}.',
                cancel_editing_url: 'Cancel editing and store the original value: {0}',
                eligeble_mail: '{0} is eligeble for e-mail scans',
                unknown_eligeble_mail: 'Not yet known if {0} is scanable for mail',
                not_eligeble_mail: '{0} is not eligeble for e-mail scans. Will be checked again when starting a scan.',
                eligeble_web: '{0} is eligeble for web scans',
                unknown_eligeble_web: 'Not yet known if {0} is scannable for web',
                not_eligeble_web: '{0} is not eligeble for web scans. Will be checked again when starting a scan.',
                save_edited_url: 'Save changes, the change will be applied to {0}.',
                delete_edited_url: 'Delete {0} from this list.',

                button_labels: {
                    save: 'Save',
                    cancel: 'Cancel',
                    remove: 'Remove',
                }
            },

            edit_form: {
                title: 'Edit list settings',
                cancel: 'Cancel',
                ok: 'Update'
            },

            delete_form: {
                title: 'Delete list',
                message: 'Are you sure you want to\n' +
                    '                delete this list? Deleting this list cannot be undone.',
                cancel: 'No, take me back',
                ok: 'Yes, Delete'
            },

            scan_now_form: {
                title: 'Confirm to scan now',
                message: 'To start a scan now, please take the following in consideration: <br>' +
                    'A scan can only be started once a day, and only when no scan is already running. Note that a scan cannot be cancelled.',
                cancel: 'Cancel',
                ok: 'Scan now',
                starting: 'Starting...',
            },

            bulk_add_form: {
                title: 'Bulk add domains',
                message: 'You can add many domains in one go. To do this, seperate each domain with a comma.',
                ok: 'Add the above domains to the list',
                status: 'Status',
                nothing_added: 'nothing added yet.',
                added_n_to_list: 'Added {0} domains to this list.',
                ignored_n: 'Additionally, {0} domains have been\n' +
                    '                            ignored as they are already in this list.',
                warning: 'Warning!',
                warning_message: 'Some domains where not added because they are in an incorrect format. <br>\n' +
                    '                            The following domains where not added',
            }

        },
        // field name translation
        urllist: {
            field_label_id: 'id',
            field_label_name: 'List Name',
            field_label_enable_scans: 'Enable Scans',
            enable_scans_enabled: 'Enabled',
            enable_scans_disabled: 'Disabled',
            field_label_scan_type: 'What scan to run',
            scan_type_web: 'web',
            scan_type_mail: 'mail',
            field_label_automated_scan_frequency: 'How often should the scan run?',
            automated_scan_frequency_disabled: 'Disabled',
            automated_scan_frequency_every_half_year: 'Every half year',
            automated_scan_frequency_every_quarter: 'At the start of every quarter',
            automated_scan_frequency_every_month: 'Every 1st day of the month',
            automated_scan_frequency_twice_per_month: 'Twice per month',
        },
        report: {
            mail: 'E-Mail',
            web: 'Web',

            fields: {
                forum_standardistation: {
                    category_label: 'Forum Standaardisatie',
                    measurements_on_agreed_security_standards: 'Measurements on agreed security standards',
                    ipv6_monitor: 'IPv6 monitor',
                },
                additional_fields: {
                    label: 'Additional fields',
                },
            },

            icon_legend: {
                title: "Legend of used icons",

                // this has been placed here, because not_applicable and not_testable reuse icons and have
                // a different meaning. That translation is not available in internet.nl
                test_title: internet_nl_messages.en.internet_nl.faqs_report_test_title,
                test_good: internet_nl_messages.en.internet_nl.faqs_report_test_good,
                test_bad: internet_nl_messages.en.internet_nl.faqs_report_test_bad,
                test_warning: internet_nl_messages.en.internet_nl.faqs_report_test_warning,
                test_info: internet_nl_messages.en.internet_nl.faqs_report_test_info,
                subtest_title: internet_nl_messages.en.internet_nl.faqs_report_subtest_title,
                subtest_good: internet_nl_messages.en.internet_nl.faqs_report_subtest_good,
                subtest_bad: internet_nl_messages.en.internet_nl.faqs_report_subtest_bad,
                subtest_warning: internet_nl_messages.en.internet_nl.faqs_report_subtest_warning,
                subtest_info: internet_nl_messages.en.internet_nl.faqs_report_subtest_info,
                subtest_not_applicable:  "Not applicable ⇒ no score impact",
                subtest_not_testable:  "Not testable ⇒ no score impact",
            },

            header: {
                title: 'Reports',
                intro: 'Select one or multiple reports, these will be displayed below.',
                select_report: 'Select report...',
                max_elements: 'Maximum number of reports selected.',
                no_options: 'No reports available.',
            },

            charts: {
                adoption_timeline: {
                    annotation: {
                        title: 'Adoption of standards over time',
                        intro: 'This graph compares various measurements of the same list over time. ' +
                            'This provides a visual indication of the progress of standards adoption. A table with the ' +
                            'same values is avaiable below. This graph shows the average score of internet.nl. Note that ' +
                            'only the values of the first selected report are shown.'
                    },
                    title: 'Average adoption of standards. Overall.',
                    yAxis_label: 'Adoption',
                    xAxis_label: 'Date',
                    average_internet_nl_score: "Average internet.nl score",
                    accessibility_text: "A table with the content of this graph is shown below.",
                },
                magazine: {
                    intro: "Below graph only shows the average of all magazine fields. Other fields cannot be enabled/disabled and changing their visibility does " +
                        "not influence this average.",
                },
                adoption_bar_chart: {
                    annotation: {
                        title: 'Average adoption of standards ',
                        intro: 'This graph shows the average adoption per standard per report.',
                    },
                    title_single: 'Average adoption of standards, %{list_information}, %{number_of_domains} domains.',
                    title_multiple: 'Comparison of adoption of standards between %{number_of_reports} reports.',
                    yAxis_label: 'Adoption',
                    average: "Average",
                    accessibility_text: "A table with the content of this graph is shown below.",
                },
                cumulative_adoption_bar_chart: {
                    annotation: {
                        title: 'Average adoption of standards over multiple reports',
                        intro: 'This graph shows the average adoption per standard averaged over multiple reports.',
                    },
                    title: 'Average adoption of standards over %{number_of_reports} reports.',
                    yAxis_label: 'Adoption',
                    average: "Average",
                    accessibility_text: "A table with the content of this graph is shown below.",
                }
            },
            report: {
                title: 'Report',
                intro: 'This shows the results of the first selected report only.',
                url_filter: 'Filter on domain...',
                not_eligeble_for_scanning: 'Domain did not match scanning criteria at the time the scan was initiated. The scanning criteria are an SOA DNS record (not NXERROR) for mail and an A or AAAA DNS record for web.\n' +
                    '                                                This domain is ignored in all statistics.',
                zoom: {
                    buttons:
                        {
                            zoom: 'details',
                            remove_zoom: 'Back to the category view',
                            zoom_in_on: 'View details of {0}',
                        },
                    zoomed_in_on: 'Details from',
                    explanation: "Using the details buttons, it is possible to see the individual metrics for each category."
                },
                link_to_report: 'View score and report from %{url} on internet.nl.',
                empty_report: 'It looks like this report is empty... did you filter too much?',
                results: {
                    not_applicable: "Not applicable",
                    not_testable: "Not testable",
                    failed: "Failed",
                    warning: "Warning",
                    info: "Info",
                    passed: "Passed",
                    unknown: "Unknown"
                }
            },
            download: {
                title: 'Download all metrics in a spreadsheet',
                intro: 'Report data is available in the following formats:',
                xlsx: 'Excel Spreadsheet (Microsoft Office), .xlsx',
                ods: 'Open Document Spreadsheet (Libre Office), .ods',
                csv: 'Comma Separated (for programmers), .csv',
            },
            settings: {
                title: 'Select visible metrics',
                intro: 'To retain focus, select the fields that are relevant to your organization.',
                buttons: {
                    reset: 'Reset',
                    reset_label: 'Resets all values to their original status.',
                    save: 'Save',
                    save_label: 'Save the changes made in this form.',
                },
                restored_from_database: "Settings restored from database",
                updated: "Settings updated",

                show_category: "Show this category",
                show_dynamic_average: "Show dynamic average",
                only_show_dynamic_average: "Only show dynamic average",
            },

            // Nofix: should we use hierarchical translations, which is much prettier? How?
            // we're not going to do that, because it requires extra code that chops the
            // labels into pieces. And it's not really clear where to do that. It would require
            // a lot of work, extra code and things do not get clearer from it that much it's worth the effort.
            /*internet_nl: {
                mail: {
                    legacy: {
                        dmarc: 'DMARC',
                        dkim: 'DKIM',
                        spf: 'SPF',
                        dmarc_policy: 'DMARC policy',
                        spf_policy: 'SPF policy',
                        start_tls: 'STARTTLS',
                        start_tls_ncsc: 'STARTTLS NCSC',
                        dnssec: {
                            email_domain: 'DNSSEC e-mail domain',
                            mx: 'DNSSEC MX',
                        },
                        dane: 'DANE',
                        ipv6: {
                            nameserver: 'IPv6 nameserver',
                            mailserver: 'IPv6 mailserver',
                        }

                    }
                }
            },
            */

            // These fields do not have a hierarchical translation, this is how they are in websecmap.
            // they are not 1-1 with the frontend. So have their own label for greater consistency.
            // Test results
            not_testable: 'Not testable',
            not_applicable: 'Not applicable',

            // legacy values
            mail_legacy: 'Mail Baseline NL Government',
            web_legacy: 'Web Baseline NL Government',

            internet_nl_mail_legacy_dmarc: 'DMARC',
            internet_nl_mail_legacy_dmarc_explanation: 'Explanation',
            internet_nl_mail_legacy_dkim: 'DKIM',
            internet_nl_mail_legacy_dkim_explanation: 'Explanation',
            internet_nl_mail_legacy_spf: 'SPF',
            internet_nl_mail_legacy_spf_explanation: 'Explanation',
            internet_nl_mail_legacy_dmarc_policy: 'DMARC policy',
            internet_nl_mail_legacy_dmarc_policy_explanation: 'Explanation',
            internet_nl_mail_legacy_spf_policy: 'SPF policy',
            internet_nl_mail_legacy_spf_policy_explanation: 'Explanation',
            internet_nl_mail_legacy_start_tls: 'STARTTLS',
            internet_nl_mail_legacy_start_tls_explanation: 'Explanation',
            internet_nl_mail_legacy_start_tls_ncsc: 'STARTTLS NCSC',
            internet_nl_mail_legacy_start_tls_ncsc_explanation: 'Explanation',
            internet_nl_mail_legacy_dnssec_mx: 'DNSSEC MX',
            internet_nl_mail_legacy_dnssec_mx_explanation: 'Explanation',
            internet_nl_mail_legacy_dane: 'DANE',
            internet_nl_mail_legacy_dane_explanation: 'Explanation',
            internet_nl_mail_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_mail_legacy_ipv6_nameserver_explanation: 'Explanation',
            internet_nl_mail_legacy_ipv6_mailserver: "IPv6 mailserver",
            internet_nl_mail_legacy_ipv6_mailserver_explanation: 'Explanation',

            internet_nl_web_legacy_dnssec: 'DNSSEC',
            internet_nl_web_legacy_dnssec_explanation: 'Explanation...',
            internet_nl_web_legacy_tls_available: 'TLS',
            internet_nl_web_legacy_tls_available_explanation: 'Explanation...',
            internet_nl_web_legacy_tls_ncsc_web: 'TLS_NCSC',
            internet_nl_web_legacy_tls_ncsc_web_explanation: 'Explanation...',
            internet_nl_web_legacy_https_enforced: 'HTTPS',
            internet_nl_web_legacy_https_enforced_explanation: 'Explanation...',
            internet_nl_web_legacy_hsts: 'HSTS',
            internet_nl_web_legacy_hsts_explanation: 'Explanation...',
            internet_nl_web_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_web_legacy_ipv6_nameserver_explanation: 'Explanation...',
            internet_nl_web_legacy_ipv6_webserver: 'IPv6 webserver',
            internet_nl_web_legacy_ipv6_webserver_explanation: 'Explanation...',
            // internet_nl_web_legacy_dane: 'DANE',

            internet_nl_web_tls: internet_nl_messages.en.internet_nl.test_sitetls_label,
            internet_nl_web_dnssec: internet_nl_messages.en.internet_nl.test_sitednssec_label,
            internet_nl_web_ipv6: internet_nl_messages.en.internet_nl.test_siteipv6_label,

            internet_nl_mail_dashboard_tls: internet_nl_messages.en.internet_nl.test_mailtls_label,
            internet_nl_mail_dashboard_auth: internet_nl_messages.en.internet_nl.test_mailauth_label,
            internet_nl_mail_dashboard_dnssec: internet_nl_messages.en.internet_nl.test_maildnssec_label,
            internet_nl_mail_dashboard_ipv6: internet_nl_messages.en.internet_nl.test_mailipv6_label,

            // web category verdicts
            internet_nl_web_ipv6_verdict_good: internet_nl_messages.en.internet_nl.test_siteipv6_passed_summary,
            internet_nl_web_ipv6_verdict_bad: internet_nl_messages.en.internet_nl.test_siteipv6_failed_summary,
            internet_nl_web_appsecpriv_verdict_good: internet_nl_messages.en.internet_nl.test_siteappsecpriv_passed_summary,
            internet_nl_web_appsecpriv_verdict_bad: internet_nl_messages.en.internet_nl.test_siteappsecpriv_failed_summary,
            internet_nl_web_tls_verdict_good: internet_nl_messages.en.internet_nl.test_sitetls_passed_summary,
            internet_nl_web_tls_verdict_bad: internet_nl_messages.en.internet_nl.test_sitetls_failed_summary,
            internet_nl_web_dnssec_verdict_good: internet_nl_messages.en.internet_nl.test_sitednssec_passed_summary,
            internet_nl_web_dnssec_verdict_bad: internet_nl_messages.en.internet_nl.test_sitednssec_failed_summary,

            // mail category verdicts
            internet_nl_mail_dashboard_tls_verdict_good: internet_nl_messages.en.internet_nl.test_mailtls_passed_summary,
            internet_nl_mail_dashboard_tls_verdict_bad: internet_nl_messages.en.internet_nl.test_mailtls_failed_summary,
            internet_nl_mail_dashboard_auth_verdict_good: internet_nl_messages.en.internet_nl.test_mailauth_passed_summary,
            internet_nl_mail_dashboard_auth_verdict_bad: internet_nl_messages.en.internet_nl.test_mailauth_failed_summary,
            internet_nl_mail_dashboard_dnssec_verdict_good: internet_nl_messages.en.internet_nl.test_maildnssec_passed_summary,
            internet_nl_mail_dashboard_dnssec_verdict_bad: internet_nl_messages.en.internet_nl.test_maildnssec_failed_summary,
            internet_nl_mail_dashboard_ipv6_verdict_good: internet_nl_messages.en.internet_nl.test_mailipv6_passed_summary,
            internet_nl_mail_dashboard_ipv6_verdict_bad: internet_nl_messages.en.internet_nl.test_mailipv6_failed_summary,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/domain-results.html
            internet_nl_web_appsecpriv: internet_nl_messages.en.internet_nl.test_siteappsecpriv_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_csp: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_csp_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_referrer_policy_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_content_type_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_frame_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_xss_label,  // Added 24 May 2019
            internet_nl_web_https_cert_domain: internet_nl_messages.en.internet_nl.detail_web_tls_cert_hostmatch_label,
            internet_nl_web_https_http_redirect: internet_nl_messages.en.internet_nl.detail_web_tls_https_forced_label,
            internet_nl_web_https_cert_chain: internet_nl_messages.en.internet_nl.detail_web_tls_cert_trust_label,
            internet_nl_web_https_tls_version: internet_nl_messages.en.internet_nl.detail_web_tls_version_label,
            internet_nl_web_https_tls_clientreneg: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_client_label,
            internet_nl_web_https_tls_ciphers: internet_nl_messages.en.internet_nl.detail_web_tls_ciphers_label,
            internet_nl_web_https_http_available: internet_nl_messages.en.internet_nl.detail_web_tls_https_exists_label,
            internet_nl_web_https_dane_exist: internet_nl_messages.en.internet_nl.detail_web_tls_dane_exists_label,
            internet_nl_web_https_http_compress: internet_nl_messages.en.internet_nl.detail_web_tls_http_compression_label,
            internet_nl_web_https_http_hsts: internet_nl_messages.en.internet_nl.detail_web_tls_https_hsts_label,
            internet_nl_web_https_tls_secreneg: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_secure_label,
            internet_nl_web_https_dane_valid: internet_nl_messages.en.internet_nl.detail_web_tls_dane_valid_label,
            internet_nl_web_https_cert_pubkey: internet_nl_messages.en.internet_nl.detail_web_tls_cert_pubkey_label,
            internet_nl_web_https_cert_sig: internet_nl_messages.en.internet_nl.detail_web_tls_cert_signature_label,
            internet_nl_web_https_tls_compress: internet_nl_messages.en.internet_nl.detail_web_tls_compression_label,
            internet_nl_web_https_tls_keyexchange: internet_nl_messages.en.internet_nl.detail_web_tls_fs_params_label,
            internet_nl_web_dnssec_valid: internet_nl_messages.en.internet_nl.detail_web_dnssec_valid_label,
            internet_nl_web_dnssec_exist: internet_nl_messages.en.internet_nl.detail_web_dnssec_exists_label,
            internet_nl_web_ipv6_ws_similar: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_ipv46_label,
            internet_nl_web_ipv6_ws_address: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_aaaa_label,
            internet_nl_web_ipv6_ns_reach: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_web_ipv6_ws_reach: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_reach_label,
            internet_nl_web_ipv6_ns_address: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,

            // verdicts:
            internet_nl_web_appsecpriv_csp_verdict_good: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_csp_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy_verdict_good: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_referrer_policy_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options_verdict_good: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_content_type_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options_verdict_good: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_frame_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection_verdict_good: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_xss_verdict_good,  // Added 24 May 2019
            internet_nl_web_https_cert_domain_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_cert_hostmatch_verdict_good,
            internet_nl_web_https_http_redirect_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_https_forced_verdict_good,
            internet_nl_web_https_cert_chain_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_cert_trust_verdict_good,
            internet_nl_web_https_tls_version_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_version_verdict_good,
            internet_nl_web_https_tls_clientreneg_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_client_verdict_good,
            internet_nl_web_https_tls_ciphers_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_ciphers_verdict_good,
            internet_nl_web_https_http_available_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_https_exists_verdict_good,
            internet_nl_web_https_dane_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_dane_exists_verdict_good,
            internet_nl_web_https_http_compress_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_http_compression_verdict_good,
            internet_nl_web_https_http_hsts_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_https_hsts_verdict_good,
            internet_nl_web_https_tls_secreneg_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_secure_verdict_good,
            internet_nl_web_https_dane_valid_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_dane_valid_verdict_good,
            internet_nl_web_https_cert_pubkey_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_cert_pubkey_verdict_good,
            internet_nl_web_https_cert_sig_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_cert_signature_verdict_good,
            internet_nl_web_https_tls_compress_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_compression_verdict_good,
            internet_nl_web_https_tls_keyexchange_verdict_good: internet_nl_messages.en.internet_nl.detail_web_tls_fs_params_verdict_good,
            internet_nl_web_dnssec_valid_verdict_good: internet_nl_messages.en.internet_nl.detail_web_dnssec_valid_verdict_good,
            internet_nl_web_dnssec_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_web_dnssec_exists_verdict_good,
            internet_nl_web_ipv6_ws_similar_verdict_good: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_ipv46_verdict_good,
            internet_nl_web_ipv6_ws_address_verdict_good: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_aaaa_verdict_good,
            internet_nl_web_ipv6_ns_reach_verdict_good: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_good,
            internet_nl_web_ipv6_ws_reach_verdict_good: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_reach_verdict_good,
            internet_nl_web_ipv6_ns_address_verdict_good: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_good,

            internet_nl_web_appsecpriv_csp_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_csp_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_referrer_policy_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_content_type_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_frame_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_appsecpriv_http_x_xss_verdict_bad,  // Added 24 May 2019
            internet_nl_web_https_cert_domain_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_cert_hostmatch_verdict_bad,
            internet_nl_web_https_http_redirect_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_https_forced_verdict_bad,
            internet_nl_web_https_cert_chain_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_cert_trust_verdict_bad,
            internet_nl_web_https_tls_version_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_version_verdict_bad,
            internet_nl_web_https_tls_clientreneg_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_client_verdict_bad,
            internet_nl_web_https_tls_ciphers_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_ciphers_verdict_bad,
            internet_nl_web_https_http_available_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_https_exists_verdict_bad,
            internet_nl_web_https_dane_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_dane_exists_verdict_bad,
            internet_nl_web_https_http_compress_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_http_compression_verdict_bad,
            internet_nl_web_https_http_hsts_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_https_hsts_verdict_bad,
            internet_nl_web_https_tls_secreneg_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_secure_verdict_bad,
            internet_nl_web_https_dane_valid_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_dane_valid_verdict_bad,
            internet_nl_web_https_cert_pubkey_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_cert_pubkey_verdict_bad,
            internet_nl_web_https_cert_sig_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_cert_signature_verdict_bad,
            internet_nl_web_https_tls_compress_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_compression_verdict_bad,
            internet_nl_web_https_tls_keyexchange_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_tls_fs_params_verdict_bad,
            internet_nl_web_dnssec_valid_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_dnssec_valid_verdict_bad,
            internet_nl_web_dnssec_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_dnssec_exists_verdict_bad,
            internet_nl_web_ipv6_ws_similar_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_ipv46_verdict_bad,
            internet_nl_web_ipv6_ws_address_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_aaaa_verdict_bad,
            internet_nl_web_ipv6_ns_reach_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_bad,
            internet_nl_web_ipv6_ws_reach_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_ipv6_web_reach_verdict_bad,
            internet_nl_web_ipv6_ns_address_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_bad,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
            internet_nl_mail_server_configured: 'Mail Server Configured (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_servers_testable: 'Mail Server Testable (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_starttls_dane_ta: 'Mail STARTTLS Dane TA (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_non_sending_domain: 'Mail Non Sending Domain (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_policy_only: 'Mail Auth DMARC Policy Only (not in UI)',   // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_ext_destination: 'Mail Auth DMARC Ext Destination (not in UI)',  // Added 24th of May 2019

            internet_nl_mail_starttls_cert_domain: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_hostmatch_label,
            internet_nl_mail_starttls_tls_version: internet_nl_messages.en.internet_nl.detail_mail_tls_version_label,
            internet_nl_mail_starttls_cert_chain: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_trust_label,
            internet_nl_mail_starttls_tls_available: internet_nl_messages.en.internet_nl.detail_mail_tls_starttls_exists_label,
            internet_nl_mail_starttls_tls_clientreneg: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_client_label,
            internet_nl_mail_starttls_tls_ciphers: internet_nl_messages.en.internet_nl.detail_mail_tls_ciphers_label,
            internet_nl_mail_starttls_dane_valid: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_valid_label,
            internet_nl_mail_starttls_dane_exist: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_exists_label,
            internet_nl_mail_starttls_tls_secreneg: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_secure_label,
            internet_nl_mail_starttls_dane_rollover: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_rollover_label,
            internet_nl_mail_starttls_cert_pubkey: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_pubkey_label,
            internet_nl_mail_starttls_cert_sig: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_signature_label,
            internet_nl_mail_starttls_tls_compress: internet_nl_messages.en.internet_nl.detail_mail_tls_compression_label,
            internet_nl_mail_starttls_tls_keyexchange: internet_nl_messages.en.internet_nl.detail_mail_tls_fs_params_label,
            internet_nl_mail_auth_dmarc_policy: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_policy_label,
            internet_nl_mail_auth_dmarc_exist: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_label,
            internet_nl_mail_auth_spf_policy: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_policy_label,
            internet_nl_mail_auth_dkim_exist: internet_nl_messages.en.internet_nl.detail_mail_auth_dkim_label,
            internet_nl_mail_auth_spf_exist: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_label,
            internet_nl_mail_dnssec_mailto_exist: internet_nl_messages.en.internet_nl.detail_mail_dnssec_exists_label,
            internet_nl_mail_dnssec_mailto_valid: internet_nl_messages.en.internet_nl.detail_mail_dnssec_valid_label,
            internet_nl_mail_dnssec_mx_valid: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_valid_label,
            internet_nl_mail_dnssec_mx_exist: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_exists_label,
            internet_nl_mail_ipv6_mx_address: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_aaaa_label,
            internet_nl_mail_ipv6_mx_reach: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_reach_label,
            internet_nl_mail_ipv6_ns_reach: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_mail_ipv6_ns_address: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,

            //
            internet_nl_mail_starttls_cert_domain_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_hostmatch_verdict_good,
            internet_nl_mail_starttls_tls_version_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_version_verdict_good,
            internet_nl_mail_starttls_cert_chain_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_trust_verdict_good,
            internet_nl_mail_starttls_tls_available_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_starttls_exists_verdict_good,
            internet_nl_mail_starttls_tls_clientreneg_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_client_verdict_good,
            internet_nl_mail_starttls_tls_ciphers_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_ciphers_verdict_good,
            internet_nl_mail_starttls_dane_valid_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_valid_verdict_good,
            internet_nl_mail_starttls_dane_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_exists_verdict_good,
            internet_nl_mail_starttls_tls_secreneg_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_secure_verdict_good,
            internet_nl_mail_starttls_dane_rollover_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_rollover_verdict_good,
            internet_nl_mail_starttls_cert_pubkey_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_pubkey_verdict_good,
            internet_nl_mail_starttls_cert_sig_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_signature_verdict_good,
            internet_nl_mail_starttls_tls_compress_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_compression_verdict_good,
            internet_nl_mail_starttls_tls_keyexchange_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_tls_fs_params_verdict_good,
            internet_nl_mail_auth_dmarc_policy_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_policy_verdict_good,
            internet_nl_mail_auth_dmarc_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_verdict_good,
            internet_nl_mail_auth_spf_policy_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_policy_verdict_good,
            internet_nl_mail_auth_dkim_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_auth_dkim_verdict_good,
            internet_nl_mail_auth_spf_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_verdict_good,
            internet_nl_mail_dnssec_mailto_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_dnssec_exists_verdict_good,
            internet_nl_mail_dnssec_mailto_valid_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_dnssec_valid_verdict_good,
            internet_nl_mail_dnssec_mx_valid_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_valid_verdict_good,
            internet_nl_mail_dnssec_mx_exist_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_exists_verdict_good,
            internet_nl_mail_ipv6_mx_address_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_aaaa_verdict_good,
            internet_nl_mail_ipv6_mx_reach_verdict_good: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_reach_verdict_good,
            internet_nl_mail_ipv6_ns_reach_verdict_good: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_good,
            internet_nl_mail_ipv6_ns_address_verdict_good: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_good,

            //
            internet_nl_mail_starttls_cert_domain_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_hostmatch_verdict_bad,
            internet_nl_mail_starttls_tls_version_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_version_verdict_bad,
            internet_nl_mail_starttls_cert_chain_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_trust_verdict_bad,
            internet_nl_mail_starttls_tls_available_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_starttls_exists_verdict_bad,
            internet_nl_mail_starttls_tls_clientreneg_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_client_verdict_bad,
            internet_nl_mail_starttls_tls_ciphers_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_ciphers_verdict_bad,
            internet_nl_mail_starttls_dane_valid_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_valid_verdict_bad,
            internet_nl_mail_starttls_dane_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_exists_verdict_bad,
            internet_nl_mail_starttls_tls_secreneg_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_renegotiation_secure_verdict_bad,
            internet_nl_mail_starttls_dane_rollover_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_dane_rollover_verdict_bad,
            internet_nl_mail_starttls_cert_pubkey_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_pubkey_verdict_bad,
            internet_nl_mail_starttls_cert_sig_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_cert_signature_verdict_bad,
            internet_nl_mail_starttls_tls_compress_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_compression_verdict_bad,
            internet_nl_mail_starttls_tls_keyexchange_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_tls_fs_params_verdict_bad,
            internet_nl_mail_auth_dmarc_policy_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_policy_verdict_bad,
            internet_nl_mail_auth_dmarc_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_auth_dmarc_verdict_bad,
            internet_nl_mail_auth_spf_policy_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_policy_verdict_bad,
            internet_nl_mail_auth_dkim_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_auth_dkim_verdict_bad,
            internet_nl_mail_auth_spf_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_auth_spf_verdict_bad,
            internet_nl_mail_dnssec_mailto_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_dnssec_exists_verdict_bad,
            internet_nl_mail_dnssec_mailto_valid_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_dnssec_valid_verdict_bad,
            internet_nl_mail_dnssec_mx_valid_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_valid_verdict_bad,
            internet_nl_mail_dnssec_mx_exist_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_exists_verdict_bad,
            internet_nl_mail_ipv6_mx_address_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_aaaa_verdict_bad,
            internet_nl_mail_ipv6_mx_reach_verdict_bad: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_reach_verdict_bad,
            internet_nl_mail_ipv6_ns_reach_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_bad,
            internet_nl_mail_ipv6_ns_address_verdict_bad: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_bad,
        },
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'All scans that have happened for this account are displayed here. It gives an insight into how ' +
                'recent the most current information is. It can also help you with comparisons to select the ideal ' +
                'scan.',
            id: ' scan #',
            type: 'Type',
            list: 'List',
            started_on: 'Started',
            finished_on: 'Finished',
            message: 'Status',
            live: 'API',
            no_scans: 'No scans have been performed yet.',
            report: 'Report',
            runtime: 'Runtime',
            open_in_api: 'Open on internet.nl API',
            open_report: 'Open report',
            last_check: 'Last status update',
            report_is_being_generated: 'Report is being generated.',
            processing_results: 'Processing results.',
        },
        auto_refresh: {
            refresh_happening_in: 'Auto refresh in:',
            units: 's',
            refresh_now: 'refresh now'
        },
        upload: {
            bulk_data_uploader: {
                title: 'Bulk Address Uploader',
                introduction: 'It\'s possible to upload large amounts of internet addresses and lists using spreadsheets. To do so,\n' +
                    '            please expand on the example spreadsheets listed below. This shows how the data has to be structured.\n' +
                    '            Examples with and without data are provided as Open Document Spreadsheet, Microsoft Office Excel and Comma Separated.',
            },
            empty_file: 'Empty file',
            file_with_example_data: 'File with example data',
            open_document_spreadsheet: 'Open Document Spreadsheet (Libre Office)',
            microsoft_office_excel: 'Excel Spreadsheet (Microsoft Office)',
            comma_separated: 'Comma Separated (for programmers)',

            drag_and_drop_uploader: {
                title: 'Drag and drop uploader',
                first_instruction: 'To upload a bulk address file, drag it onto the \'upload\' rectangle below.',
                nomouse: 'A more conventional upload option is available below the drag and drop uploader.',
                process: 'Uploading happens in two stages.\n' +
                    '        First the progress bar is filled, this means the data is sent to this website successfully. Then\n' +
                    '        some processing happens on the server. When this processing is finished, the uploaded file icon below\n' +
                    '        will change to either Success (green, with a checkmark) or Failed (red, with a cross).',
                details_after_upload: 'Details on the status of the uploaded file can be seen afterwards in the \'recent uploads\' section below\n' +
                    '        this uploader.',
                warnings: 'Important: It\'s possible to upload up until 10000 urls in 200 categories per upload. The more\n' +
                    '        is uploaded, the more time it will take. Please wait until the upload is confirmed.',
                fallback_select_a_file: 'Select a file to upload:',
            },

            recent_uploads: {
                title: 'Recent uploads',
                intro: 'This list shows your recent uploads. The status messages give an impression of what has been ' +
                    'created or added. If something went wrong, the status contains hints on what to do next.' +
                    'if your upload was not successful',
                date: 'Date',
                filename: 'Filename',
                filesize: 'Size',
                status: 'Status',
                no_uploads: 'No files uploaded.',
            }
        }
    },
    nl: {
        menu: {
            admin: 'Beheer',
            domains: "Domeinen",
            scans: "Scans",
            reports: "Rapporten",
            account: "Account",
            log_off: "Uitloggen",
            log_in: "Inloggen",
        },

        loading: {
            loading: "Laden...",
        },
        domains: {
            add_new_list: 'Lijst toevoegen',
            button_close_label: 'Sluiten',
            button_create_list_label: 'Maak deze lijst',
        },
        domain_management: {

            title: "Domeinen",
            intro: "Beheer lijsten met domeinen",
            bulk_upload_link: "Een groot aantal domeinen kan worden geüpload met de Bulk Addressen Uploader, hier.",

            icon_legend: {
                title: "Legenda van gebruikte pictogrammen",
                intro: "De domeinen in de lijsten hieronder worden gebruikt bij iedere scan. Voordat een scan is uitgevoerd " +
                    "wordt per domein gekeken of het domein aan de voorwaarden voldoet om gescand te worden. In de lijst " +
                    "hieronder wordt daarvan een beeld gegeven, echter kan dat beeld verouderd zijn: dit wordt ververst " +
                    "voor iedere scan.",
                can_connect: "Deze dienst is bereikbaar en wordt (waarschijnlijk) gescanned.",
                unknown_connectivity: "Niet bekend of deze dienst beschikbaar is, dit wordt later gecontroleerd.",
                cannot_connect: "Deze dienst is niet beschikbaar, en wordt (waarschijnlijk) niet gescand."
            },

            button_labels: {
                configure: 'Instellingen',
                add_domains: 'Domeinen toevoegen',
                scan_now: 'Nu scannen',
                scan_now_scanning: 'Aan het scannen',
                scan_now_scanning_title: 'Nu scannen is alleen beschikbaar als er geen scan draait, en kan maximaal 1x per dag worden aangeroepen.',
                delete: 'Verwijder',
                view_csv: 'Bekijk.csv',
                timeout_for_24_hours: 'Max 1 scan/dag',
                scanning_disabled: 'Scans uitgeschakeld',
            },

            about_this_list: {
                header: 'Over deze lijst',
                last_scan_started: 'Laatste scan gestart op',
                still_running: 'loopt nog',
                finished: 'afgerond',
                not_scanned_before: 'Niet eerder gescand',
                type_of_scan_performed: 'Soort scan',
                scan_frequency: 'Scan frequentie',
                next_scheduled_scan: 'Volgende ingeplande scan',
                scanning_disabled: 'Scannen van deze lijst is uitgeschakeld.',
                latest_report: 'Meest actuele rapportage',
            },

            domains: {
                header: 'Domeinen',
                eligeble_mail: 'E-mail scannen is mogelijk',
                unknown_eligeble_mail: 'Onbekend of E-mail scannen mogelijk is',
                not_eligeble_mail: 'Kan geen E-mail scan uitvoeren (wordt opnieuw gecheckt bij het starten van de scan)',
                eligeble_web: 'Web scan is mogelijk',
                unknown_eligeble_web: 'Niet bekend of het mogelijk is een web scan uit te voeren',
                not_eligeble_web: 'Web scan kan niet worden uitgevoerd. Dit wordt opnieuw gecheckt bij het starten van de scan.',

                button_labels: {
                    save: 'Opslaan',
                    cancel: 'Annuleren',
                    remove: 'Verwijderen',
                }
            },

            edit_form: {
                title: 'Lijst instellingen',
                cancel: 'Annuleer',
                ok: 'Opslaan'
            },

            delete_form: {
                title: 'Lijst verwijderen',
                message: 'Weet u zeker dat u deze lijst wil verwijderen? Dit kan niet ongedaan worden gemaakt.',
                cancel: 'Nee, niet verwijderen',
                ok: 'Ja, verwijder'
            },

            scan_now_form: {
                title: 'Bevestig om opnieuw te scannen',
                message: 'Een scan die nu wordt gestart heeft de volgende eigenschappen: <br>' +
                    'Een handmatige scan kan eens per dag worden gestart, mits er nog geen scan wordt uitgevoerd op deze lijst.',
                cancel: 'Annuleer',
                ok: 'Nu scannen',
                starting: 'Opstarten...',
            },

            bulk_add_form: {
                title: 'Toevoegen van domeinen',
                message: 'Voeg hieronder een of meerdere domeinen toe, gescheiden door een komma.',
                ok: 'Voeg bovenstaande domeinen toe aan de lijst',
                status: 'Status',
                nothing_added: 'nog niets toegevoegd.',
                added_n_to_list: 'Er zijn {0} domeinen aan de lijst toegevoegd.',
                ignored_n: 'Verder zijn er {0} domeinen genegeerd omdat ze al in de lijst zaten.',
                warning: 'Waarschuwing!',
                warning_message: 'Sommige domeinen zijn niet in een geldig formaat. Controleer de volgende domeinen en' +
                    'probeer het opnieuw:',
            }

        },
        // field name translation
        urllist: {
            field_label_id: 'id',
            field_label_name: 'Lijst naam',
            field_label_enable_scans: 'Scans uitvoeren',
            enable_scans_enabled: 'Ingeschakeld',
            enable_scans_disabled: 'Uitgeschakeld',
            field_label_scan_type: 'Welk type scan moet er worden uitgevoerd',
            scan_type_web: 'Website en webadres',
            scan_type_mail: 'E-Mail',
            field_label_automated_scan_frequency: 'Moet deze scan vaker worden uitgevoerd?',
            automated_scan_frequency_disabled: 'Nee, niet automatisch scannen',
            automated_scan_frequency_every_half_year: 'Ja, aan het begin van elk half jaar',
            automated_scan_frequency_every_quarter: 'Ja, aan het begin van elk kwartaal',
            automated_scan_frequency_every_month: 'Ja, aan het begin van elke maand',
            automated_scan_frequency_twice_per_month: 'Ja, om de twee weken vanaf de 1e van de maand',
        },
        report: {
            mail: 'E-Mail',
            web: 'Web',

            fields: {
                forum_standardistation: {
                    category_label: 'Forum Standaardisatie',
                    measurements_on_agreed_security_standards: 'Measurements on agreed security standards',
                    ipv6_monitor: 'IPv6 monitor',
                },
                additional_fields: {
                    label: 'Additionele velden',
                },
            },

            icon_legend: {
                title: "Legenda van gebruikte pictogrammen",

                // this has been placed here, because not_applicable and not_testable reuse icons and have
                // a different meaning. That translation is not available in internet.nl
                test_title: internet_nl_messages.nl.internet_nl.faqs_report_test_title,
                test_good: internet_nl_messages.nl.internet_nl.faqs_report_test_good,
                test_bad: internet_nl_messages.nl.internet_nl.faqs_report_test_bad,
                test_warning: internet_nl_messages.nl.internet_nl.faqs_report_test_warning,
                test_info: internet_nl_messages.nl.internet_nl.faqs_report_test_info,
                subtest_title: internet_nl_messages.nl.internet_nl.faqs_report_subtest_title,
                subtest_good: internet_nl_messages.nl.internet_nl.faqs_report_subtest_good,
                subtest_bad: internet_nl_messages.nl.internet_nl.faqs_report_subtest_bad,
                subtest_warning: internet_nl_messages.nl.internet_nl.faqs_report_subtest_warning,
                subtest_info: internet_nl_messages.nl.internet_nl.faqs_report_subtest_info,
                subtest_not_applicable:  "Niet van toepassing ⇒ geen score impact",
                subtest_not_testable:  "Niet testbaar ⇒ geen score impact",
            },

            header: {
                title: 'Rapporten',
                intro: '',
                select_report: 'Selecteer rapport...',
                max_elements: 'Maximum aantal rapporten geselecteerd.',
                no_options: 'Geen rapporten beschikbaar.',
            },

            charts: {
                adoption_timeline: {
                    annotation: {
                        title: 'Adoptie van standaarden over tijd.',
                        intro: 'Deze grafiek toont verschillende metingen van dezelfde lijst over tijd. ' +
                            'Dit geeft zicht over de voortgang van de adoptie van standaarden. Het toont de gemiddelde score van internet.nl. ' +
                            'Deze grafiek toont alleen de gemiddelden van het eerst geselecteerde rapport.'
                    },
                    title: 'Gemiddelde adoptie van standaarden over tijd.',
                    yAxis_label: 'Adoptiegraad',
                    xAxis_label: 'Datum',
                    average_internet_nl_score: "Gemiddelde internet.nl score",
                    accessibility_text: "Een tabel met de inhoud van deze grafiek wordt hieronder getoond.",
                },
                magazine: {
                    intro: "Onderstaande grafiek toont het gemiddelde van alle magazine velden. Deze grafiek kan niet worden aangepast, ook niet door de zichtbaarheid van velden aan te passen.",
                },
                adoption_bar_chart: {
                    annotation: {
                        title: 'Adoptie van standaarden',
                        intro: 'Deze grafiek toont het percentage adoptie per categorie en onderliggende metingen.',
                    },
                    title_single: 'Adoptie van standaarden, %{list_information}, %{number_of_domains} domeinen.',
                    title_multiple: 'Vergelijking adoptie van standaarden tussen %{number_of_reports} rapporten.',
                    yAxis_label: 'Adoptiegraad',
                    average: "Gemiddeld",
                    accessibility_text: "Een tabel met de inhoud van deze grafiek wordt hieronder getoond.",
                },
                cumulative_adoption_bar_chart: {
                    annotation: {
                        title: 'Gemiddelde adoptie, waarbij rapporten bij elkaar worden opgeteld',
                        intro: 'In deze grafiek worden de geselecteerde rapporten bij elkaar opgeteld, en daar het gemiddelde van getoond.',
                    },
                    title: 'Gemiddelde adoptie van standaarden van %{number_of_reports} rapporten.',
                    yAxis_label: 'Adoptiegraad',
                    average: "Gemiddeld",
                    accessibility_text: "Een tabel met de inhoud van deze grafiek wordt hieronder getoond.",
                }
            },
            report: {
                title: 'Rapport',
                intro: 'Dit overzicht laat alleen de resultaten van het het eerst geselecteerde rapport zien.',
                not_eligeble_for_scanning: 'Dit domein voldeed niet aan de scan-criteria op het moment van scannen. Deze criteria zijn een SOA DNS record (geen NXERROR) voor mail en een A of AAAA DNS record voor web.\n' +
                    ' Dit domein komt niet terug in de statistieken.',
                url_filter: 'Filter op domein...',
                zoom: {
                    buttons:
                        {
                            zoom: 'details',
                            remove_zoom: 'Terug naar hoofdniveau',
                            zoom_in_on: 'Bekijk de details van {0}',
                        },
                    zoomed_in_on: 'Details van ',
                    explanation: "Met de detail buttons is het mogelijk om details van ieder categorie naar voren te halen."
                },
                link_to_report: 'Bekijk de score en rapportage van %{url} op internet.nl.',
                empty_report: 'Geen meetgegevens gevonden, wordt er misschien teveel gefilterd?',
                results: {
                    not_applicable: "Niet van toepassing",
                    not_testable: "Niet testbaar",
                    failed: "Niet goed",
                    warning: "Waarschuwing",
                    info: "Info",
                    passed: "Goed",
                    unknown: "Unknown"
                }
            },
            download: {
                title: 'Downloaden',
                intro: 'De data in dit rapport is beschikbaar in de volgende formaten:',
                xlsx: 'Excel Spreadsheet (voor o.a. Microsoft Office), .xlsx',
                ods: 'Open Document Spreadsheet (voor o.a. Libre Office), .ods',
                csv: 'Comma Separated (voor programmeurs), .csv',
            },
            settings: {
                title: 'Selecteer zichtbare meetwaarden',
                intro: 'Selecteer de velden die relevant zijn voor uw organisatie.',
                buttons: {
                    reset: 'Reset',
                    reset_label: 'Zet de originele waardes terug naar de waardes in de database',
                    save: 'Opslaan',
                    save_label: 'Sla de wijzigingen in de zichtbare meetwaarden op.',
                },
                restored_from_database: "Zichtbare meetwaarden zijn teruggezet naar de waardes in de database",
                updated: "Zichtbare meetwaarden opgeslagen",

                show_category: "Toon deze categorie",
                show_dynamic_average: "Bereken dynamisch het gemiddelde van alle zichtbare velden",
                only_show_dynamic_average: "Toon alleen het dynamisch berekende gemiddelde",
            },

            // legacy values
            mail_legacy: 'Measurements on agreed security standards + IPv6 Monitor',
            web_legacy: 'Measurements on agreed security standards + IPv6 Monitor',

            internet_nl_mail_legacy_dmarc: 'DMARC',
            internet_nl_mail_legacy_dmarc_explanation: 'Uitleg',
            internet_nl_mail_legacy_dkim: 'DKIM',
            internet_nl_mail_legacy_dkim_explanation: 'Uitleg',
            internet_nl_mail_legacy_spf: 'SPF',
            internet_nl_mail_legacy_spf_explanation: 'Uitleg',
            internet_nl_mail_legacy_dmarc_policy: 'DMARC policy',
            internet_nl_mail_legacy_dmarc_policy_explanation: 'Uitleg',
            internet_nl_mail_legacy_spf_policy: 'SPF policy',
            internet_nl_mail_legacy_spf_policy_explanation: 'Uitleg',
            internet_nl_mail_legacy_start_tls: 'STARTTLS',
            internet_nl_mail_legacy_start_tls_explanation: 'Uitleg',
            internet_nl_mail_legacy_start_tls_ncsc: 'STARTTLS NCSC',
            internet_nl_mail_legacy_start_tls_ncsc_explanation: 'Uitleg',
            internet_nl_mail_legacy_dnssec_mx: 'DNSSEC MX',
            internet_nl_mail_legacy_dnssec_mx_explanation: 'Uitleg',
            internet_nl_mail_legacy_dane: 'DANE',
            internet_nl_mail_legacy_dane_explanation: 'Uitleg',
            internet_nl_mail_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_mail_legacy_ipv6_nameserver_explanation: 'Uitleg',
            internet_nl_mail_legacy_ipv6_mailserver: "IPv6 mailserver",
            internet_nl_mail_legacy_ipv6_mailserver_explanation: 'Uitleg',

            internet_nl_web_legacy_dnssec: 'DNSSEC',
            internet_nl_web_legacy_dnssec_explanation: 'Uitleg...',
            internet_nl_web_legacy_tls_available: 'TLS',
            internet_nl_web_legacy_tls_available_explanation: 'Uitleg...',
            internet_nl_web_legacy_tls_ncsc_web: 'TLS_NCSC',
            internet_nl_web_legacy_tls_ncsc_web_explanation: 'Uitleg...',
            internet_nl_web_legacy_https_enforced: 'HTTPS',
            internet_nl_web_legacy_https_enforced_explanation: 'Uitleg...',
            internet_nl_web_legacy_hsts: 'HSTS',
            internet_nl_web_legacy_hsts_explanation: 'Uitleg...',
            internet_nl_web_legacy_ipv6_nameserver: 'IPv6 nameserver',
            internet_nl_web_legacy_ipv6_nameserver_explanation: 'Uitleg...',
            internet_nl_web_legacy_ipv6_webserver: 'IPv6 webserver',
            internet_nl_web_legacy_ipv6_webserver_explanation: 'Uitleg...',

            // use the labels from fallback language.

            // types of tests
            internet_nl_web_tls: internet_nl_messages.nl.internet_nl.test_sitetls_label,
            internet_nl_web_dnssec: internet_nl_messages.nl.internet_nl.test_sitednssec_label,
            internet_nl_web_ipv6: internet_nl_messages.nl.internet_nl.test_siteipv6_label,

            internet_nl_mail_dashboard_tls: internet_nl_messages.nl.internet_nl.test_mailtls_label,
            internet_nl_mail_dashboard_auth: internet_nl_messages.nl.internet_nl.test_mailauth_label,
            internet_nl_mail_dashboard_dnssec: internet_nl_messages.nl.internet_nl.test_maildnssec_label,
            internet_nl_mail_dashboard_ipv6: internet_nl_messages.nl.internet_nl.test_mailipv6_label,

            // web category verdicts
            internet_nl_web_ipv6_verdict_good: internet_nl_messages.nl.internet_nl.test_siteipv6_passed_summary,
            internet_nl_web_ipv6_verdict_bad: internet_nl_messages.nl.internet_nl.test_siteipv6_failed_summary,
            internet_nl_web_appsecpriv_verdict_good: internet_nl_messages.nl.internet_nl.test_siteappsecpriv_passed_summary,
            internet_nl_web_appsecpriv_verdict_bad: internet_nl_messages.nl.internet_nl.test_siteappsecpriv_failed_summary,
            internet_nl_web_tls_verdict_good: internet_nl_messages.nl.internet_nl.test_sitetls_passed_summary,
            internet_nl_web_tls_verdict_bad: internet_nl_messages.nl.internet_nl.test_sitetls_failed_summary,
            internet_nl_web_dnssec_verdict_good: internet_nl_messages.nl.internet_nl.test_sitednssec_passed_summary,
            internet_nl_web_dnssec_verdict_bad: internet_nl_messages.nl.internet_nl.test_sitednssec_failed_summary,

            // mail category verdicts
            internet_nl_mail_dashboard_tls_verdict_good: internet_nl_messages.nl.internet_nl.test_mailtls_passed_summary,
            internet_nl_mail_dashboard_tls_verdict_bad: internet_nl_messages.nl.internet_nl.test_mailtls_failed_summary,
            internet_nl_mail_dashboard_auth_verdict_good: internet_nl_messages.nl.internet_nl.test_mailauth_passed_summary,
            internet_nl_mail_dashboard_auth_verdict_bad: internet_nl_messages.nl.internet_nl.test_mailauth_failed_summary,
            internet_nl_mail_dashboard_dnssec_verdict_good: internet_nl_messages.nl.internet_nl.test_maildnssec_passed_summary,
            internet_nl_mail_dashboard_dnssec_verdict_bad: internet_nl_messages.nl.internet_nl.test_maildnssec_failed_summary,
            internet_nl_mail_dashboard_ipv6_verdict_good: internet_nl_messages.nl.internet_nl.test_mailipv6_passed_summary,
            internet_nl_mail_dashboard_ipv6_verdict_bad: internet_nl_messages.nl.internet_nl.test_mailipv6_failed_summary,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/domain-results.html
            internet_nl_web_appsecpriv: internet_nl_messages.nl.internet_nl.results_domain_appsecpriv_http_headers_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_csp: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_csp_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_referrer_policy_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_content_type_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_frame_label,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_xss_label,  // Added 24 May 2019

            internet_nl_web_https_cert_domain: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_hostmatch_label,
            internet_nl_web_https_http_redirect: internet_nl_messages.nl.internet_nl.detail_web_tls_https_forced_label,
            internet_nl_web_https_cert_chain: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_trust_label,
            internet_nl_web_https_tls_version: internet_nl_messages.nl.internet_nl.detail_web_tls_version_label,
            internet_nl_web_https_tls_clientreneg: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_client_label,
            internet_nl_web_https_tls_ciphers: internet_nl_messages.nl.internet_nl.detail_web_tls_ciphers_label,
            internet_nl_web_https_http_available: internet_nl_messages.nl.internet_nl.detail_web_tls_https_exists_label,
            internet_nl_web_https_dane_exist: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_exists_label,
            internet_nl_web_https_http_compress: internet_nl_messages.nl.internet_nl.detail_web_tls_http_compression_label,
            internet_nl_web_https_http_hsts: internet_nl_messages.nl.internet_nl.detail_web_tls_https_hsts_label,
            internet_nl_web_https_tls_secreneg: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_secure_label,
            internet_nl_web_https_dane_valid: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_valid_label,
            internet_nl_web_https_cert_pubkey: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_pubkey_label,
            internet_nl_web_https_cert_sig: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_signature_label,
            internet_nl_web_https_tls_compress: internet_nl_messages.nl.internet_nl.detail_web_tls_compression_label,
            internet_nl_web_https_tls_keyexchange: internet_nl_messages.nl.internet_nl.detail_web_tls_fs_params_label,
            internet_nl_web_dnssec_valid: internet_nl_messages.nl.internet_nl.detail_web_dnssec_valid_label,
            internet_nl_web_dnssec_exist: internet_nl_messages.nl.internet_nl.detail_web_dnssec_exists_label,
            internet_nl_web_ipv6_ws_similar: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_ipv46_label,
            internet_nl_web_ipv6_ws_address: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_aaaa_label,
            internet_nl_web_ipv6_ns_reach: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_web_ipv6_ws_reach: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_reach_label,
            internet_nl_web_ipv6_ns_address: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,

            internet_nl_web_appsecpriv_csp_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_csp_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_referrer_policy_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_content_type_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_frame_verdict_good,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_xss_verdict_good,  // Added 24 May 2019
            internet_nl_web_https_cert_domain_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_hostmatch_verdict_good,
            internet_nl_web_https_http_redirect_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_https_forced_verdict_good,
            internet_nl_web_https_cert_chain_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_trust_verdict_good,
            internet_nl_web_https_tls_version_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_version_verdict_good,
            internet_nl_web_https_tls_clientreneg_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_client_verdict_good,
            internet_nl_web_https_tls_ciphers_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_ciphers_verdict_good,
            internet_nl_web_https_http_available_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_https_exists_verdict_good,
            internet_nl_web_https_dane_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_exists_verdict_good,
            internet_nl_web_https_http_compress_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_http_compression_verdict_good,
            internet_nl_web_https_http_hsts_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_https_hsts_verdict_good,
            internet_nl_web_https_tls_secreneg_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_secure_verdict_good,
            internet_nl_web_https_dane_valid_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_valid_verdict_good,
            internet_nl_web_https_cert_pubkey_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_pubkey_verdict_good,
            internet_nl_web_https_cert_sig_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_signature_verdict_good,
            internet_nl_web_https_tls_compress_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_compression_verdict_good,
            internet_nl_web_https_tls_keyexchange_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_tls_fs_params_verdict_good,
            internet_nl_web_dnssec_valid_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_dnssec_valid_verdict_good,
            internet_nl_web_dnssec_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_dnssec_exists_verdict_good,
            internet_nl_web_ipv6_ws_similar_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_ipv46_verdict_good,
            internet_nl_web_ipv6_ws_address_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_aaaa_verdict_good,
            internet_nl_web_ipv6_ns_reach_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_good,
            internet_nl_web_ipv6_ws_reach_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_reach_verdict_good,
            internet_nl_web_ipv6_ns_address_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_good,

            internet_nl_web_appsecpriv_csp_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_csp_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_referrer_policy_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_referrer_policy_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_content_type_options_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_content_type_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_frame_options_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_frame_verdict_bad,  // Added 24 May 2019
            internet_nl_web_appsecpriv_x_xss_protection_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_appsecpriv_http_x_xss_verdict_bad,  // Added 24 May 2019
            internet_nl_web_https_cert_domain_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_hostmatch_verdict_bad,
            internet_nl_web_https_http_redirect_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_https_forced_verdict_bad,
            internet_nl_web_https_cert_chain_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_trust_verdict_bad,
            internet_nl_web_https_tls_version_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_version_verdict_bad,
            internet_nl_web_https_tls_clientreneg_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_client_verdict_bad,
            internet_nl_web_https_tls_ciphers_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_ciphers_verdict_bad,
            internet_nl_web_https_http_available_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_https_exists_verdict_bad,
            internet_nl_web_https_dane_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_exists_verdict_bad,
            internet_nl_web_https_http_compress_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_http_compression_verdict_bad,
            internet_nl_web_https_http_hsts_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_https_hsts_verdict_bad,
            internet_nl_web_https_tls_secreneg_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_secure_verdict_bad,
            internet_nl_web_https_dane_valid_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_dane_valid_verdict_bad,
            internet_nl_web_https_cert_pubkey_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_pubkey_verdict_bad,
            internet_nl_web_https_cert_sig_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_signature_verdict_bad,
            internet_nl_web_https_tls_compress_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_compression_verdict_bad,
            internet_nl_web_https_tls_keyexchange_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_tls_fs_params_verdict_bad,
            internet_nl_web_dnssec_valid_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_dnssec_valid_verdict_bad,
            internet_nl_web_dnssec_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_dnssec_exists_verdict_bad,
            internet_nl_web_ipv6_ws_similar_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_ipv46_verdict_bad,
            internet_nl_web_ipv6_ws_address_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_aaaa_verdict_bad,
            internet_nl_web_ipv6_ns_reach_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_bad,
            internet_nl_web_ipv6_ws_reach_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_ipv6_web_reach_verdict_bad,
            internet_nl_web_ipv6_ns_address_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_bad,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
            internet_nl_mail_server_configured: 'Mail Server Configured (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_servers_testable: 'Mail Server Testable (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_starttls_dane_ta: 'Mail STARTTLS Dane TA (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_non_sending_domain: 'Mail Non Sending Domain (not in UI)',  // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_policy_only: 'Mail Auth DMARC Policy Only (not in UI)',   // Added 24th of May 2019
            internet_nl_mail_auth_dmarc_ext_destination: 'Mail Auth DMARC Ext Destination (not in UI)',  // Added 24th of May 2019

            internet_nl_mail_starttls_cert_domain: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_hostmatch_label,
            internet_nl_mail_starttls_tls_version: internet_nl_messages.nl.internet_nl.detail_mail_tls_version_label,
            internet_nl_mail_starttls_cert_chain: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_trust_label,
            internet_nl_mail_starttls_tls_available: internet_nl_messages.nl.internet_nl.detail_mail_tls_starttls_exists_label,
            internet_nl_mail_starttls_tls_clientreneg: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_client_label,
            internet_nl_mail_starttls_tls_ciphers: internet_nl_messages.nl.internet_nl.detail_mail_tls_ciphers_label,
            internet_nl_mail_starttls_dane_valid: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_valid_label,
            internet_nl_mail_starttls_dane_exist: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_exists_label,
            internet_nl_mail_starttls_tls_secreneg: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_secure_label,
            internet_nl_mail_starttls_dane_rollover: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_rollover_label,
            internet_nl_mail_starttls_cert_pubkey: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_pubkey_label,
            internet_nl_mail_starttls_cert_sig: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_signature_label,
            internet_nl_mail_starttls_tls_compress: internet_nl_messages.nl.internet_nl.detail_mail_tls_compression_label,
            internet_nl_mail_starttls_tls_keyexchange: internet_nl_messages.nl.internet_nl.detail_mail_tls_fs_params_label,
            internet_nl_mail_auth_dmarc_policy: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_policy_label,
            internet_nl_mail_auth_dmarc_exist: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_label,
            internet_nl_mail_auth_spf_policy: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_policy_label,
            internet_nl_mail_auth_dkim_exist: internet_nl_messages.nl.internet_nl.detail_mail_auth_dkim_label,
            internet_nl_mail_auth_spf_exist: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_label,
            internet_nl_mail_dnssec_mailto_exist: internet_nl_messages.en.internet_nl.detail_mail_dnssec_exists_label,
            internet_nl_mail_dnssec_mailto_valid: internet_nl_messages.en.internet_nl.detail_mail_dnssec_valid_label,
            internet_nl_mail_dnssec_mx_valid: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_valid_label,
            internet_nl_mail_dnssec_mx_exist: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_exists_label,
            internet_nl_mail_ipv6_mx_address: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_aaaa_label,
            internet_nl_mail_ipv6_mx_reach: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_reach_label,
            internet_nl_mail_ipv6_ns_reach: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_mail_ipv6_ns_address: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,

            //
            internet_nl_mail_starttls_cert_domain_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_hostmatch_verdict_good,
            internet_nl_mail_starttls_tls_version_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_version_verdict_good,
            internet_nl_mail_starttls_cert_chain_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_trust_verdict_good,
            internet_nl_mail_starttls_tls_available_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_starttls_exists_verdict_good,
            internet_nl_mail_starttls_tls_clientreneg_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_client_verdict_good,
            internet_nl_mail_starttls_tls_ciphers_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_ciphers_verdict_good,
            internet_nl_mail_starttls_dane_valid_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_valid_verdict_good,
            internet_nl_mail_starttls_dane_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_exists_verdict_good,
            internet_nl_mail_starttls_tls_secreneg_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_secure_verdict_good,
            internet_nl_mail_starttls_dane_rollover_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_rollover_verdict_good,
            internet_nl_mail_starttls_cert_pubkey_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_pubkey_verdict_good,
            internet_nl_mail_starttls_cert_sig_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_signature_verdict_good,
            internet_nl_mail_starttls_tls_compress_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_compression_verdict_good,
            internet_nl_mail_starttls_tls_keyexchange_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_tls_fs_params_verdict_good,
            internet_nl_mail_auth_dmarc_policy_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_policy_verdict_good,
            internet_nl_mail_auth_dmarc_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_verdict_good,
            internet_nl_mail_auth_spf_policy_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_policy_verdict_good,
            internet_nl_mail_auth_dkim_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_auth_dkim_verdict_good,
            internet_nl_mail_auth_spf_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_verdict_good,
            internet_nl_mail_dnssec_mailto_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_exists_verdict_good,
            internet_nl_mail_dnssec_mailto_valid_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_valid_verdict_good,
            internet_nl_mail_dnssec_mx_valid_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_valid_verdict_good,
            internet_nl_mail_dnssec_mx_exist_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_exists_verdict_good,
            internet_nl_mail_ipv6_mx_address_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_aaaa_verdict_good,
            internet_nl_mail_ipv6_mx_reach_verdict_good: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_reach_verdict_good,
            internet_nl_mail_ipv6_ns_reach_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_good,
            internet_nl_mail_ipv6_ns_address_verdict_good: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_good,

            //
            internet_nl_mail_starttls_cert_domain_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_hostmatch_verdict_bad,
            internet_nl_mail_starttls_tls_version_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_version_verdict_bad,
            internet_nl_mail_starttls_cert_chain_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_trust_verdict_bad,
            internet_nl_mail_starttls_tls_available_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_starttls_exists_verdict_bad,
            internet_nl_mail_starttls_tls_clientreneg_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_client_verdict_bad,
            internet_nl_mail_starttls_tls_ciphers_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_ciphers_verdict_bad,
            internet_nl_mail_starttls_dane_valid_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_valid_verdict_bad,
            internet_nl_mail_starttls_dane_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_exists_verdict_bad,
            internet_nl_mail_starttls_tls_secreneg_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_renegotiation_secure_verdict_bad,
            internet_nl_mail_starttls_dane_rollover_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_dane_rollover_verdict_bad,
            internet_nl_mail_starttls_cert_pubkey_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_pubkey_verdict_bad,
            internet_nl_mail_starttls_cert_sig_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_cert_signature_verdict_bad,
            internet_nl_mail_starttls_tls_compress_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_compression_verdict_bad,
            internet_nl_mail_starttls_tls_keyexchange_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_tls_fs_params_verdict_bad,
            internet_nl_mail_auth_dmarc_policy_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_policy_verdict_bad,
            internet_nl_mail_auth_dmarc_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_auth_dmarc_verdict_bad,
            internet_nl_mail_auth_spf_policy_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_policy_verdict_bad,
            internet_nl_mail_auth_dkim_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_auth_dkim_verdict_bad,
            internet_nl_mail_auth_spf_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_auth_spf_verdict_bad,
            internet_nl_mail_dnssec_mailto_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_exists_verdict_bad,
            internet_nl_mail_dnssec_mailto_valid_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_valid_verdict_bad,
            internet_nl_mail_dnssec_mx_valid_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_valid_verdict_bad,
            internet_nl_mail_dnssec_mx_exist_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_exists_verdict_bad,
            internet_nl_mail_ipv6_mx_address_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_aaaa_verdict_bad,
            internet_nl_mail_ipv6_mx_reach_verdict_bad: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_reach_verdict_bad,
            internet_nl_mail_ipv6_ns_reach_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_verdict_bad,
            internet_nl_mail_ipv6_ns_address_verdict_bad: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_verdict_bad,
        },
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'Alle scans die zijn uitgevoerd voor dit account staan hier. Het geeft een overzicht in hoe recent ' +
                'de data is. Het geeft ook inzicht in of de meest recente scan al is afgerond.',
            id: 'scan #',
            type: 'Soort',
            list: 'Lijst',
            started_on: 'Gestart',
            finished_on: 'Klaar',
            message: 'Status',
            live: 'API',
            no_scans: 'Nog geen scans uitgevoerd.',
            report: 'Rapport',
            runtime: 'Looptijd',
            open_in_api: 'Open internet.nl API resultaat',
            open_report: 'Open rapport',
            last_check: 'Laatste status update',
            report_is_being_generated: 'Report wordt gemaakt.',
            processing_results: 'Resultaten worden verwerkt.',
        },
        auto_refresh: {
            refresh_happening_in: 'Lijst wordt ververst over:',
            units: 's',
            refresh_now: 'ververs nu'
        },
        upload: {
            bulk_data_uploader: {
                title: 'Bulk Address Uploader',
                introduction: 'Hiermee is het mogelijk om grote hoeveelheden internet adressen en lijsten toe ' +
                    'te voegen. Dit gebeurd met spreadsheets. Begin met het downloaden van de voorbeelden hieronder, ' +
                    'deze geven aan wat het juiste formaat is. De voorbeeldbestanden zijn te downloaden in het ' +
                    'Open Document formaat, Microsoft Office formaat en Kommagescheiden.',
            },
            empty_file: 'Leeg bestand',
            file_with_example_data: 'Bestand met voorbeelddata',
            open_document_spreadsheet: 'Open Document Werkblad (Libre Office)',
            microsoft_office_excel: 'Excel Werkblad (Microsoft Office)',
            comma_separated: 'Kommagescheiden (voor programmeurs)',

            drag_and_drop_uploader: {
                title: 'Drag and drop uploader',
                first_instruction: 'Sleep het gewenste bestand in de \'upload\' rechthoek hieronder.',
                nomouse: 'Een meer gebruikelijke upload methode is beschikbaar onder het drag and drop gedeelte.',
                process: 'Het uploaden gebeurd in twee fasen. In de eerste fase wordt de voortgangsbalk gevuld. Als ' +
                    'deze vol is, is het bestand naar de server gestuurd. Dan is de upload nog niet compleet: de gegevens ' +
                    'worden nu verwerkt. Op het moment dat de gegevens verwerkt zijn verschijnt dit als een groen vinkje of' +
                    'rood kruis op het bestand.',
                details_after_upload: 'Details over de status van de upload kunnen naderhand worden bekeken ' +
                    'in het \'recente uploads\' onderdeel onder het upload veld.',
                warnings: 'Let op: Het is mogelijk om tot 10.000 adressen en 200 categorien te sturen per keer. Hoe meer' +
                    ' gegevens, hoe langer het kan duren voordat de upload volledig is. Wees geduldig en wacht tot de upload afgerond is.',
                fallback_select_a_file: 'Selecteer een bestand om te uploaden:',
            },

            recent_uploads: {
                title: 'Recent geupload',
                intro: 'Deze lijst geeft de meest recente uploads weer. De status berichten geven aan wat er is toegevoegd. ' +
                    'Mocht er iets verkeerd zijn gegaan bij het uploaden, dan is hier advies te vinden over wat te verbeteren.',
                date: 'Datum',
                filename: 'Bestand',
                filesize: 'Grootte',
                status: 'Status (in het Engels)',
                no_uploads: 'Nog geen bestanden geüpload.',
            }
        }
    },
};