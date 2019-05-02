const messages = {
    en: {
        report: {
            // types of tests
            internet_nl_web_tls: internet_nl_messages.en.internet_nl.test_sitetls_label,
            internet_nl_web_dnssec: internet_nl_messages.en.internet_nl.test_sitednssec_label,
            internet_nl_web_ipv6: internet_nl_messages.en.internet_nl.test_siteipv6_label,

            internet_nl_mail_dashboard_tls: internet_nl_messages.en.internet_nl.test_mailtls_label,
            internet_nl_mail_dashboard_auth: internet_nl_messages.en.internet_nl.test_mailauth_label,
            internet_nl_mail_dashboard_dnssec: internet_nl_messages.en.internet_nl.test_maildnssec_label,
            internet_nl_mail_dashboard_ipv6: internet_nl_messages.en.internet_nl.test_mailipv6_label,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/domain-results.html
            internet_nl_web_https_cert_domain: internet_nl_messages.en.internet_nl.detail_web_tls_cert_hostmatch_label,
            internet_nl_web_https_http_redirect: internet_nl_messages.en.internet_nl.detail_web_tls_https_forced_label,
            internet_nl_web_https_cert_chain: internet_nl_messages.en.internet_nl.detail_web_tls_cert_trust_label,
            internet_nl_web_https_tls_version: internet_nl_messages.en.internet_nl.detail_web_tls_version_label,
            internet_nl_web_https_tls_clientreneg: internet_nl_messages.en.internet_nl.detail_web_tls_renegotiation_client_label,
            internet_nl_web_https_tls_ciphers: internet_nl_messages.en.internet_nl.detail_web_tls_ciphers_label,
            internet_nl_web_https_http_available: internet_nl_messages.en.internet_nl.todo,
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

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
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
            internet_nl_mail_dnssec_mailto_exist: internet_nl_messages.en.internet_nl.todo,
            internet_nl_mail_dnssec_mailto_valid: internet_nl_messages.en.internet_nl.todo,
            internet_nl_mail_dnssec_mx_valid: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_valid_label,
            internet_nl_mail_dnssec_mx_exist: internet_nl_messages.en.internet_nl.detail_mail_dnssec_mx_exists_label,
            internet_nl_mail_ipv6_mx_address: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_aaaa_label,
            internet_nl_mail_ipv6_mx_reach: internet_nl_messages.en.internet_nl.detail_mail_ipv6_mx_reach_label,
            internet_nl_mail_ipv6_ns_reach: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_mail_ipv6_ns_address: internet_nl_messages.en.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,
        },
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'All scans that have happened for this account are displayed here. It gives an insight into how ' +
                'recent the most current information is. It can also help you with comparisons to select the ideal ' +
                'scan.',
            id: '#',
            type: 'Type',
            list: 'List',
            started_on: 'Started',
            finished_on: 'Finished',
            message: 'Status',
            live: 'API',
            no_scans: 'No scans have been performed yet.',
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
        report: {
            // types of tests
            internet_nl_web_tls: internet_nl_messages.nl.internet_nl.test_sitetls_label,
            internet_nl_web_dnssec: internet_nl_messages.nl.internet_nl.test_sitednssec_label,
            internet_nl_web_ipv6: internet_nl_messages.nl.internet_nl.test_siteipv6_label,

            internet_nl_mail_dashboard_tls: internet_nl_messages.nl.internet_nl.test_mailtls_label,
            internet_nl_mail_dashboard_auth: internet_nl_messages.nl.internet_nl.test_mailauth_label,
            internet_nl_mail_dashboard_dnssec: internet_nl_messages.nl.internet_nl.test_maildnssec_label,
            internet_nl_mail_dashboard_ipv6: internet_nl_messages.nl.internet_nl.test_mailipv6_label,

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/domain-results.html
            internet_nl_web_https_cert_domain: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_hostmatch_label,
            internet_nl_web_https_http_redirect: internet_nl_messages.nl.internet_nl.detail_web_tls_https_forced_label,
            internet_nl_web_https_cert_chain: internet_nl_messages.nl.internet_nl.detail_web_tls_cert_trust_label,
            internet_nl_web_https_tls_version: internet_nl_messages.nl.internet_nl.detail_web_tls_version_label,
            internet_nl_web_https_tls_clientreneg: internet_nl_messages.nl.internet_nl.detail_web_tls_renegotiation_client_label,
            internet_nl_web_https_tls_ciphers: internet_nl_messages.nl.internet_nl.detail_web_tls_ciphers_label,
            internet_nl_web_https_http_available: internet_nl_messages.nl.internet_nl.todo,
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

            // https://github.com/NLnetLabs/Internet.nl/blob/cece8255ac7f39bded137f67c94a10748970c3c7/checks/templates/mail-results.html
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
            internet_nl_mail_dnssec_mailto_exist: internet_nl_messages.nl.internet_nl.todo,
            internet_nl_mail_dnssec_mailto_valid: internet_nl_messages.nl.internet_nl.todo,
            internet_nl_mail_dnssec_mx_valid: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_valid_label,
            internet_nl_mail_dnssec_mx_exist: internet_nl_messages.nl.internet_nl.detail_mail_dnssec_mx_exists_label,
            internet_nl_mail_ipv6_mx_address: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_aaaa_label,
            internet_nl_mail_ipv6_mx_reach: internet_nl_messages.nl.internet_nl.detail_mail_ipv6_mx_reach_label,
            internet_nl_mail_ipv6_ns_reach: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_reach_label,
            internet_nl_mail_ipv6_ns_address: internet_nl_messages.nl.internet_nl.detail_web_mail_ipv6_ns_aaaa_label,
        },
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'Alle scans die zijn uitgevoerd voor dit account staan hier. Het geeft een overzicht in hoe recent ' +
                'de data is. Het geeft ook inzicht in of de meest recente scan al is afgerond.',
            id: '#',
            type: 'Soort',
            list: 'Lijst',
            started_on: 'Gestart',
            finished_on: 'Klaar',
            message: 'Status',
            live: 'API',
            no_scans: 'Nog geen scans uitgevoerd.',
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