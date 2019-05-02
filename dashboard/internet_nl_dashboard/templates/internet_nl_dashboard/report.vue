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

        <h2 v-if="selected_report.value">Column Visbility Filters</h2>
        <div v-for="(category_group, category_name, y) in categories" v-if="is_relevant_category(category_name)" style="width: 50%; float: left;">
            <h3><input type="checkbox" v-model='issue_filters[category_name]["visible"]'> {{ $t("report." + category_name) }}</h3>
            <span v-for="category_name in category_group">
                <input type="checkbox" v-model='issue_filters[category_name]["visible"]' :id="category_name + '_visible'">
                <label :for="category_name + '_visible'">{{ $t("report." + category_name) }}</label><br />
            </span>
        </div>
        <br style="clear: both;">

        <span v-if="selected_category" @click="select_category('')">Remove filter: {{ $t("report." + selected_category) }}</span>
        <span v-if="!selected_category">&nbsp;</span>

        <div v-if="selected_report.value">
        <label for="url_filter">Url filter:</label><input type="text" v-model="url_filter" id="url_filter">
        <br><br><br><br>
        </div>
        <h2 v-if="filtered_urls.length">Report</h2>
        <div>
            <table v-if="filtered_urls.length">
                <tr>
                    <th style="width: 300px">&nbsp;</th>
                    <th class="rotate" v-for="rating in filtered_urls[0].endpoints[0].ratings" v-if="filtered_urls[0].endpoints.length && is_relevant_for_category(rating.type)  && is_visible(rating.type)">
                        <div @click="select_category(rating.type)"><span>{{ $t("report." + rating.type) }}</span></div>
                    </th>
                </tr>

                <tr v-for="url in filtered_urls" v-if="url.endpoints.length">
                    <td >{{url.url}}</td>
                    <td v-for="rating in url.endpoints[0].ratings" v-if="is_relevant_for_category(rating.type) && is_visible(rating.type)">
                        <span v-if="rating.ok < 1">❌</span>
                        <span v-if="rating.ok > 0">✅</span>
                    </td>
                </tr>
            </table>
        </div>

        <div id="download" v-if="selected_report.value">
            <h2>Download</h2>
            Download raw data as:
            <ul>
            <li><a :href="'/data/download-spreadsheet/' + selected_report.value.report + '/xlsx/'">Excel Spreadsheet (Microsoft Office), .xlsx</a></li>
            <li><a :href="'/data/download-spreadsheet/' + selected_report.value.report + '/ods/'">Open Document Spreadsheet (Libre Office), .ods</a></li>
            <li><a :href="'/data/download-spreadsheet/' + selected_report.value.report + '/csv/'">Comma Separated (for programmers), .csv</a></li>
            </ul>
        </div>

    </div>
</template>
{% endverbatim %}

<script>
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
        // Supporting multiple reports at the same time is hard to understand. Don't know how / if we can do
        // comparisons.
        reports: [],

        // instead we support one report with one set of urls. This is the source set of urls that can be copied at will
        original_urls: [],

        // this is the set of urls where filters are applied.
        filtered_urls:[],

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

        issue_filters:{
            'web': {'visible': true},
            'mail': {'visible': true},
            'internet_nl_web_tls': {'visible': true},
            'internet_nl_web_dnssec': {'visible': true},
            'internet_nl_web_ipv6': {'visible': true},
            'internet_nl_mail_dashboard_tls': {'visible': true},
            'internet_nl_mail_dashboard_auth': {'visible': true},
            'internet_nl_mail_dashboard_dnssec': {'visible': true},
            'internet_nl_mail_dashboard_ipv6': {'visible': true},
            'internet_nl_web_https_cert_domain': {'visible': true},
            'internet_nl_web_https_http_redirect': {'visible': true},
            'internet_nl_web_https_cert_chain': {'visible': true},
            'internet_nl_web_https_tls_version': {'visible': true},
            'internet_nl_web_https_tls_clientreneg': {'visible': true},
            'internet_nl_web_https_tls_ciphers': {'visible': true},
            'internet_nl_web_https_http_available': {'visible': true},
            'internet_nl_web_https_dane_exist': {'visible': true},
            'internet_nl_web_https_http_compress': {'visible': true},
            'internet_nl_web_https_http_hsts': {'visible': true},
            'internet_nl_web_https_tls_secreneg': {'visible': true},
            'internet_nl_web_https_dane_valid': {'visible': true},
            'internet_nl_web_https_cert_pubkey': {'visible': true},
            'internet_nl_web_https_cert_sig': {'visible': true},
            'internet_nl_web_https_tls_compress': {'visible': true},
            'internet_nl_web_https_tls_keyexchange': {'visible': true},
            'internet_nl_web_dnssec_valid': {'visible': true},
            'internet_nl_web_dnssec_exist': {'visible': true},
            'internet_nl_web_ipv6_ws_similar': {'visible': true},
            'internet_nl_web_ipv6_ws_address': {'visible': true},
            'internet_nl_web_ipv6_ns_reach': {'visible': true},
            'internet_nl_web_ipv6_ws_reach': {'visible': true},
            'internet_nl_web_ipv6_ns_address': {'visible': true},
            'internet_nl_mail_starttls_cert_domain': {'visible': true},
            'internet_nl_mail_starttls_tls_version': {'visible': true},
            'internet_nl_mail_starttls_cert_chain': {'visible': true},
            'internet_nl_mail_starttls_tls_available': {'visible': true},
            'internet_nl_mail_starttls_tls_clientreneg': {'visible': true},
            'internet_nl_mail_starttls_tls_ciphers': {'visible': true},
            'internet_nl_mail_starttls_dane_valid': {'visible': true},
            'internet_nl_mail_starttls_dane_exist': {'visible': true},
            'internet_nl_mail_starttls_tls_secreneg': {'visible': true},
            'internet_nl_mail_starttls_dane_rollover': {'visible': true},
            'internet_nl_mail_starttls_cert_pubkey': {'visible': true},
            'internet_nl_mail_starttls_cert_sig': {'visible': true},
            'internet_nl_mail_starttls_tls_compress': {'visible': true},
            'internet_nl_mail_starttls_tls_keyexchange': {'visible': true},
            'internet_nl_mail_auth_dmarc_policy': {'visible': true},
            'internet_nl_mail_auth_dmarc_exist': {'visible': true},
            'internet_nl_mail_auth_spf_policy': {'visible': true},
            'internet_nl_mail_auth_dkim_exist': {'visible': true},
            'internet_nl_mail_auth_spf_exist': {'visible': true},
            'internet_nl_mail_dnssec_mailto_exist': {'visible': true},
            'internet_nl_mail_dnssec_mailto_valid': {'visible': true},
            'internet_nl_mail_dnssec_mx_valid': {'visible': true},
            'internet_nl_mail_dnssec_mx_exist': {'visible': true},
            'internet_nl_mail_ipv6_mx_address': {'visible': true},
            'internet_nl_mail_ipv6_mx_reach': {'visible': true},
            'internet_nl_mail_ipv6_ns_reach': {'visible': true},
            'internet_nl_mail_ipv6_ns_address': {'visible': true},
        },

        // url_filter allows the filtering of names in the list of urls.
        url_filter: '',

        selected_category: '',

        // such basic functionality missing in vue, it even got removed.
        debounce_timer: 0,

        available_recent_reports: [],
        selected_report: {'report': 0, 'type': ''}

    },
    mounted: function(){
        this.get_available_recent_reports();
    },
    // common issue that debounce does not work on a watch:
    // https://stackoverflow.com/questions/47172952/vuejs-2-debounce-not-working-on-a-watch-option
    created() {
        this.debounce = _.debounce( (func) => {
          // console.log('Debounced term: ' + func);
          func.apply();
        }, 300)
    },
    methods: {
        load: function(report_id) {
            this.get_report_data(report_id);
        },
        get_report_data: function(report_id){
            fetch(`/data/report/get/${report_id}/`).then(response => response.json()).then(data => {
                this.reports = data;

                this.original_urls = data[0].calculation.urls;
                this.filtered_urls = data[0].calculation.urls;

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        get_available_recent_reports: function(){
            fetch(`/data/report/recent/`).then(response => response.json()).then(data => {
                options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].created_on = this.humanize_date(data[i].created_on);
                    options.push({'value': {'report': data[i].id, 'type': data[i].type}, 'label': `${data[i].id}: ${data[i].list_name} (type: ${data[i].type}, from: ${data[i].created_on})`})
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

        is_relevant_category: function(category_name) {
            if (this.selected_report.value === undefined)
                return false;

            if (this.selected_report.value.type === 'web' && category_name === 'web' && category_name === 'web')
                return true;

            if (this.selected_report.value.type === 'mail' && category_name === 'mail')
                return true;

            if (this.selected_category === category_name)
                return true;

            return false;
        },

        select_category: function(category_name){

            if (Object.keys(this.categories).includes(category_name))
                this.selected_category = category_name;
            else
                this.selected_category = "";
        },

        is_visible(issue_name){
            return this.issue_filters[issue_name].visible;
        },

        filter_urls(keyword) {
            let urls = [];

            this.original_urls.forEach(function(value) {
                if (value.url.includes(keyword))
                    urls.push(value)
            });

            this.filtered_urls = urls;

        },
    },
    watch: {
        selected_report: function () {
            // load selected organization id
            this.load(this.selected_report.value.report);
        },
        url_filter: function(newValue, oldValue){
            this.filter_urls(newValue);
            // aside from debouncing not working, as it doesn't understand the vue context, it is not needed
            // up until 400 + items in the list.
            // this.debounce(function() {this.methods.filter_urls(newValue);});
        }
    }

});
</script>
