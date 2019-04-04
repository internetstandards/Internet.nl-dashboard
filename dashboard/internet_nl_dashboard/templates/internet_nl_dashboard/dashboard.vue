{% verbatim %}
<style>
/* https://css-tricks.com/rotated-table-column-headers/*/
    th.rotate {
  /* Something you can count on */
  height: 100px;
  white-space: nowrap;
}

th.rotate > div {
  transform:
    /* Magic Numbers */
    translate(15px, 62px)
    /* 45 is really 360 - 45 */
    rotate(315deg);
  width: 30px;
}
th.rotate > div > span {
    border-bottom: 1px solid #ccc;
    padding: 5px 10px;
}
</style>
<template type="x-template" id="report_template">
    <div>
        <h2>Select Report</h2>
        <v-select v-model="selected_report" :options="available_recent_reports"></v-select>
        <h2>Report</h2>

        <h2>Categories</h2>
        <span v-if="selected_category" @click="select_category('')">Remove filter: {{selected_category}}</span>
        <span v-if="!selected_category">&nbsp;</span>
        <div v-for="report in reports">
            <table>
                <tr>
                    <th style="width: 300px">&nbsp;</th>
                    <th class="rotate" v-for="rating in report.calculation.urls[0].endpoints[0].ratings" v-if="report.calculation.urls[0].endpoints.length && is_relevant_for_category(rating.type)">
                        <div @click="select_category(rating.type)"><span>{{ $t("dashboard." + rating.type) }}</span></div>
                    </th>
                </tr>

                <tr v-for="url in report.calculation.urls" v-if="url.endpoints.length">
                    <td >{{url.url}}</td>
                    <td v-for="rating in url.endpoints[0].ratings" v-if="is_relevant_for_category(rating.type)">
                        <span v-if="rating.ok < 1">❌</span>
                        <span v-if="rating.ok > 0">✅</span>
                    </td>
                </tr>
            </table>
        </div>

    </div>
</template>
{% endverbatim %}

<script>
const messages = {
    en: {
        dashboard: {
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
        }
    },
    nl: {
        dashboard: {
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
        }
    }
};

const i18n = new VueI18n({
    locale: get_cookie('dashboard_language'),
    fallbackLocale: 'en',
    messages,
});


// todo: order of the fields, and possible sub sub categories
// todo: allow filtering on what results to show
// todo: store filter options for reports (as generic or per report? or as a re-applicable set?)
vueReport = new Vue({
    i18n,
    name: 'report',
    el: '#report',
    template: '#report_template',
    mixins: [humanize_mixin],
    data: {
        reports: [],
        categories: {
            'web': [
                'internet_nl_web_tls',
                'internet_nl_web_dnssec',
                'internet_nl_web_ipv6'
            ],
            'mail': [
                'internet_nl_mail_dashboard_tls',
                'internet_nl_mail_dashboard_auth',
                'internet_nl_mail_dashboard_dnssec',
                'internet_nl_mail_dashboard_ipv6'
            ],
            'internet_nl_web_tls': [
                'internet_nl_web_https_cert_domain',
                'internet_nl_web_https_http_redirect',
                'internet_nl_web_https_cert_chain',
                'internet_nl_web_https_tls_version',
                'internet_nl_web_https_tls_clientreneg',
                'internet_nl_web_https_tls_ciphers',
                'internet_nl_web_https_http_available',
                'internet_nl_web_https_dane_exist',
                'internet_nl_web_https_http_compress',
                'internet_nl_web_https_http_hsts',
                'internet_nl_web_https_tls_secreneg',
                'internet_nl_web_https_dane_valid',
                'internet_nl_web_https_cert_pubkey',
                'internet_nl_web_https_cert_sig',
                'internet_nl_web_https_tls_compress',
                'internet_nl_web_https_tls_keyexchange'
            ],
            'internet_nl_web_dnssec': [
                'internet_nl_web_dnssec_valid',
                'internet_nl_web_dnssec_exist'
            ],
            'internet_nl_web_ipv6': [
                'internet_nl_web_ipv6_ws_similar',
                'internet_nl_web_ipv6_ws_address',
                'internet_nl_web_ipv6_ns_reach',
                'internet_nl_web_ipv6_ws_reach',
                'internet_nl_web_ipv6_ns_address'
            ],
            'internet_nl_mail_dashboard_tls': [
                'internet_nl_mail_starttls_cert_domain',
                'internet_nl_mail_starttls_tls_version',
                'internet_nl_mail_starttls_cert_chain',
                'internet_nl_mail_starttls_tls_available',
                'internet_nl_mail_starttls_tls_clientreneg',
                'internet_nl_mail_starttls_tls_ciphers',
                'internet_nl_mail_starttls_dane_valid',
                'internet_nl_mail_starttls_dane_exist',
                'internet_nl_mail_starttls_tls_secreneg',
                'internet_nl_mail_starttls_dane_rollover',
                'internet_nl_mail_starttls_cert_pubkey',
                'internet_nl_mail_starttls_cert_sig',
                'internet_nl_mail_starttls_tls_compress',
                'internet_nl_mail_starttls_tls_keyexchange'

            ],
            'internet_nl_mail_dashboard_auth': [
                'internet_nl_mail_auth_dmarc_policy',
                'internet_nl_mail_auth_dmarc_exist',
                'internet_nl_mail_auth_spf_policy',
                'internet_nl_mail_auth_dkim_exist',
                'internet_nl_mail_auth_spf_exist'
            ],
            'internet_nl_mail_dashboard_dnssec': [
                'internet_nl_mail_dnssec_mailto_exist',
                'internet_nl_mail_dnssec_mailto_valid',
                'internet_nl_mail_dnssec_mx_valid',
                'internet_nl_mail_dnssec_mx_exist'
            ],
            'internet_nl_mail_dashboard_ipv6': [
                'internet_nl_mail_ipv6_mx_address',
                'internet_nl_mail_ipv6_mx_reach',
                'internet_nl_mail_ipv6_ns_reach',
                'internet_nl_mail_ipv6_ns_address'
            ]
        },

        selected_category: '',

        available_recent_reports: [],
        selected_report: 0

    },
    mounted: function(){
        this.get_available_recent_reports();
    },
    methods: {
        load: function(report_id) {
            this.get_report_data(report_id);
        },
        get_report_data: function(report_id){
            fetch(`/data/report/get/${report_id}/`).then(response => response.json()).then(data => {
                this.reports = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        get_available_recent_reports: function(){
            fetch(`/data/report/recent/`).then(response => response.json()).then(data => {
                options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].created_on = this.humanize_date(data[i].created_on);
                    options.push({'value': data[i].id, 'label': `${data[i].id}: ${data[i].list_name} (type: ${data[i].type}, from: ${data[i].created_on})`})
                }
                this.available_recent_reports = options;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        is_relevant_for_category: function(value){
            if (this.selected_category !== "") {
                if (this.categories[this.selected_category].includes(value)) {
                    return true;
                }
            }
            else
                // If not category has been selected, just return the overarching categories.
                return this.categories['web'].includes(value) || this.categories['mail'].includes(value)
        },

        select_category: function(category_name){

            if (Object.keys(this.categories).includes(category_name))
                this.selected_category = category_name;
            else
                this.selected_category = "";


        },
    },
    watch: {
        selected_report: function () {
            // load selected organization id
            this.load(this.selected_report.value);
        }
    }

});
</script>
