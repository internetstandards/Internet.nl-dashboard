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

        <div v-if="selected_report.value.report">
            <h2>Column Visbility Filters</h2>

            <div class="chart-container" style="position: relative; height:300px; width:100%">
                <line-chart :color_scheme="color_scheme" :chart_data="issue_timeline_of_related_urllist" :axis="['pct_ok', 'pct_not_ok']"></line-chart>
            </div>

            <div class="chart-container" style="position: relative; height:500px; width:100%">
                <percentage-bar-chart :title="graph_bar_chart_title" :translation_key="'charts.report_bar_chart'" :color_scheme="color_scheme" v-if='reports.length && "statistics_per_issue_type" in reports[0]' :chart_data="[reports[0].statistics_per_issue_type]" :axis="categories[selected_category]"></percentage-bar-chart>
            </div>

            <div class="chart-container" style="position: relative; height:500px; width:100%">
                <radar-chart :title="graph_radar_chart_title" :color_scheme="color_scheme" v-if='reports.length && "statistics_per_issue_type" in reports[0]' :chart_data="[reports[0].statistics_per_issue_type]" :axis="categories[selected_category]"></radar-chart>
            </div>

            <div v-for="category in categories">
                <div v-for="(category_group, category_name, y) in categories[category]" style="width: 50%; float: left;">
                    <h3><input type="checkbox" v-model='issue_filters[category_name].visible'> {{ $t("report." + category_name) }}</h3>
                    <span v-for="category_name in category_group">
                        <input type="checkbox" v-model='issue_filters[category_name].visible' :id="category_name + '_visible'">
                        <label :for="category_name + '_visible'">{{ $t("report." + category_name) }}</label><br />
                    </span>
                </div>
            </div>
            <br style="clear: both;">

            <span v-if="selected_category" @click="select_category(selected_report.value.urllist_scan_type)">Remove filter: {{ $t("report." + selected_category) }}</span>
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
                        <th class="rotate" v-for="category in categories[selected_category]" v-if="filtered_urls[0].endpoints.length">
                            <div @click="select_category(category)">
                                <span>{{ $t("report." + category) }}</span></div>
                        </th>
                    </tr>

                    <tr v-for="url in filtered_urls" v-if="url.endpoints.length">
                        <td >{{url.url}}</td>
                        <td v-for="category_name in categories[selected_category]" v-if="category_name in url.endpoints[0].ratings_by_type">
                            <span v-if="url.endpoints[0].ratings_by_type[category_name].ok < 1" :title="category_name">❌</span>
                            <span v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0" :title="category_name">✅</span>
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
    </div>
</template>
{% endverbatim %}

<script>
// Done: order of the fields, and possible sub sub categories
// todo: beta: allow filtering on what results to show
// todo: store filter options for reports (as generic or per report? or as a re-applicable set?) Per user account.
// todo: how to add a item for legacy views?
// todo: how to translate graphs?
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
            // fallback category
            '': [
                'mail',
                'web',
            ],
            'web': [
                'internet_nl_web_tls',
                'internet_nl_web_dnssec',
                'internet_nl_web_ipv6',
                'web_legacy'
            ],
            'mail': [
                'internet_nl_mail_dashboard_tls',
                'internet_nl_mail_dashboard_auth',
                'internet_nl_mail_dashboard_dnssec',
                'internet_nl_mail_dashboard_ipv6',
                'mail_legacy'
            ],
            'internet_nl_web_tls': [
                'internet_nl_web_https_tls_version',
                'internet_nl_web_https_tls_clientreneg',
                'internet_nl_web_https_tls_ciphers',
                'internet_nl_web_https_tls_secreneg',
                'internet_nl_web_https_tls_compress',
                'internet_nl_web_https_tls_keyexchange',

                'internet_nl_web_https_http_redirect',
                'internet_nl_web_https_http_available',
                'internet_nl_web_https_http_compress',
                'internet_nl_web_https_http_hsts',

                'internet_nl_web_https_dane_exist',
                'internet_nl_web_https_dane_valid',

                'internet_nl_web_https_cert_domain',
                'internet_nl_web_https_cert_chain',
                'internet_nl_web_https_cert_pubkey',
                'internet_nl_web_https_cert_sig',

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
                'internet_nl_mail_starttls_tls_version',
                'internet_nl_mail_starttls_tls_ciphers',
                'internet_nl_mail_starttls_tls_secreneg',
                'internet_nl_mail_starttls_tls_clientreneg',
                'internet_nl_mail_starttls_tls_keyexchange',
                'internet_nl_mail_starttls_tls_compress',

                'internet_nl_mail_starttls_cert_domain',
                'internet_nl_mail_starttls_cert_chain',
                'internet_nl_mail_starttls_cert_sig',
                'internet_nl_mail_starttls_cert_pubkey',

                'internet_nl_mail_starttls_dane_exist',
                'internet_nl_mail_starttls_dane_valid',
                'internet_nl_mail_starttls_dane_rollover',

            ],
            'internet_nl_mail_dashboard_auth': [
                'internet_nl_mail_auth_dmarc_exist',
                'internet_nl_mail_auth_dmarc_policy',

                'internet_nl_mail_auth_dkim_exist',

                'internet_nl_mail_auth_spf_exist',
                'internet_nl_mail_auth_spf_policy',
            ],
            'internet_nl_mail_dashboard_dnssec': [
                'internet_nl_mail_dnssec_mailto_exist',
                'internet_nl_mail_dnssec_mailto_valid',

                'internet_nl_mail_dnssec_mx_exist',
                'internet_nl_mail_dnssec_mx_valid',
            ],
            'internet_nl_mail_dashboard_ipv6': [
                'internet_nl_mail_ipv6_ns_reach',
                'internet_nl_mail_ipv6_ns_address',

                'internet_nl_mail_ipv6_mx_reach',
                'internet_nl_mail_ipv6_mx_address',
            ],
            'mail_legacy': [
                'internet_nl_mail_legacy_dane',
                'internet_nl_mail_legacy_tls_available',
                'internet_nl_mail_legacy_spf',
                'internet_nl_mail_legacy_dkim',
                'internet_nl_mail_legacy_dmarc',
                'internet_nl_mail_legacy_dnsssec_mailserver_domain',
                'internet_nl_mail_legacy_dnssec_email_domain',
                'internet_nl_mail_legacy_ipv6_mailserver',
                'internet_nl_mail_legacy_ipv6_nameserver',
            ],
            'web_legacy': [
                'internet_nl_web_legacy_dane',
                'internet_nl_web_legacy_tls_ncsc_web',
                'internet_nl_web_legacy_hsts',
                'internet_nl_web_legacy_https_enforced',
                'internet_nl_web_legacy_tls_available',
                'internet_nl_web_legacy_ipv6_webserver',
                'internet_nl_web_legacy_ipv6_nameserver',
            ]
        },

        issue_filters:{
            'web': {'visible': true},
            'web_legacy': {'visible': true},
            'mail': {'visible': true},
            'mail_legacy': {'visible': true},
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
        selected_report: {'label': '', 'value': {'report': 0, 'type': '', 'urllist_id': 0}},

        // graphs:
        issue_timeline_of_related_urllist: [],
        color_scheme: {
            'high_background': 'rgba(255, 99, 132, 0.2)',
            'high_border': 'rgba(255, 99, 132, 0.2)',
            'medium_background': 'rgba(255, 102, 0, 0.2)',
            'medium_border': 'rgba(255,102,0,1)',
            'low_background': 'rgba(255, 255, 0, 0.2)',
            'low_border': 'rgba(255,255,0,1)',
            'ok_background': 'rgba(50, 255, 50, 0.2)',
            'ok_border': 'rgba(50, 255, 50, 1)',
            'addresses_background': 'rgba(0, 0, 0, 0.2)',
            'addresses_border': 'rgba(0,0,0,1)',
            'services_background': 'rgba(0, 40, 255, 0.2)',
            'services_border': 'rgba(0,40,255,1)',
            'primary_background': 'rgba(255, 112, 50, 0.6)',
            'primary_border': 'rgba(255, 112, 50, 1)',
            'secondary_background': 'rgba(21, 66, 115, 0.6)',
            'secondary_border': 'rgba(21, 66, 115, 1)',
        },
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

                this.selected_category = this.selected_report.value.urllist_scan_type;

                this.original_urls = data[0].calculation.urls;
                this.filtered_urls = data[0].calculation.urls;
                this.get_timeline();
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        get_available_recent_reports: function(){
            fetch(`/data/report/recent/`).then(response => response.json()).then(data => {
                options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].created_on = this.humanize_date(data[i].created_on);
                    options.push({
                        'value': data[i],
                        'label': `${data[i].id}: ${data[i].list_name} (type: ${data[i].type}, from: ${data[i].created_on})`})
                }
                this.available_recent_reports = options;

                // if the page was requested with a page ID, start loading that report.
                // this supports: http://localhost:8000/reports/83/
                if (window.location.href.split('/').length > 3) {
                    get_id = window.location.href.split('/')[4];
                    // can we change the select2 to a certain value?

                    this.available_recent_reports.forEach((option) => {
                       if (option.value.id + "" === get_id){
                           this.selected_report = option;
                       }
                    });

                }

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
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
                this.selected_category = this.selected_report.value.urllist_scan_type;
        },

        filter_urls(keyword) {
            let urls = [];

            this.original_urls.forEach(function(value) {
                if (value.url.includes(keyword))
                    urls.push(value)
            });

            this.filtered_urls = urls;

        },
        get_timeline(){
            // selected_report.urllist_id contains the key to the timeline.
            // data/report/urllist_report_graph_data/10/

            if (this.selected_report.value.urllist_id === 0) {
                return;
            }

            fetch(`/data/report/urllist_report_graph_data/${this.selected_report.value.urllist_id}/`).then(response => response.json()).then(data => {
                this.issue_timeline_of_related_urllist = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});

        }
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
    },
    computed: {
        // graph titles:
        graph_radar_chart_title: function(){
            return i18n.t('charts.report_radar_chart.title', {
                'list_information': this.selected_report.value.list_name,
                'report_information': this.humanize_date(this.selected_report.created_on),
                'number_of_domains': this.original_urls.length
            });
        },

        graph_bar_chart_title: function(){
            return i18n.t('charts.report_bar_chart.title', {
                'list_information': this.selected_report.value.list_name,
                'report_information': this.humanize_date(this.selected_report.created_on),
                'number_of_domains': this.original_urls.length
            });
        },

    }

});

const chart_mixin = {

    props: {
        chart_data: {type: Array, required: true},
        axis: {type: Array, required: false},
        color_scheme: {type: Object, required: false},
        title: {type: String, required: false},
        translation_key: {type: String, required: false}
    },
    data: function () {
        return {
            chart: {}
        }
    },
    render: function(createElement) {
        return createElement(
            'canvas',
            {
                ref: 'canvas'
            },
        )
    },
    mounted: function () {
        this.buildChart();
        this.renderData();
    },
    watch: {
        chart_data: function(){
            this.renderData();
        },

        title: function(){
            this.renderTitle();
        },

        // Supports changing the colors of this graph ad-hoc.
        // charts.js is not reactive.
        color_scheme: function(){
            // this.renderData();
        },
    }
};


Vue.component('percentage-bar-chart', {
    i18n,
    mixins: [chart_mixin],

    methods: {

        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'bar',
                data: {},
                plugins: [ChartDataLabels],
                options: {
                    plugins:{
                        datalabels: {
                            // todo: add percentage sign to label
                            // todo: add label on top of bar, not in center.
                            color: '#262626',
                            clamp: true, // always shows the number, also when the number 100%
                            anchor: 'end', // show the number at the top of the bar.
                            align: 'end', // shows the value outside of the bar,
                            // format as a percentage
                            formatter: function(value, context) {
                                return value + '%';
                            }
                        }
                    },
                    legend: {
                        display: false
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: this.title
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    // this is now a percentage graph.
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: 100,
                                callback: function(label, index, labels) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
								labelString: i18n.t(this.translation_key + '.yAxis_label')
							},
                        }]
				    },
                }
            });

        },
        renderData: function(){
            // have to add it as list, so we'll need to convert it back...
            let data = this.chart_data[0];

            if (data === undefined) {
                // nothing to show
                this.chart.data.labels = [];
                this.chart.data.datasets = [];
                this.chart.update();
                return;
            }

            let labels = Array();
            let chartdata = [];

            console.log(data);

            this.axis.forEach((ax) => {
                if (ax in data) {
                    labels.push(i18n.t("report." + ax));
                    chartdata.push(data[ax].pct_ok);
                }
            });

            this.chart.data.labels = labels;
            this.chart.data.datasets = [{
                data: chartdata,
                backgroundColor: this.color_scheme.primary_background,
                borderColor: this.color_scheme.primary_border,
                borderWidth: 1,
                lineTension: 0,
            }];

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});

Vue.component('radar-chart', {
    mixins: [chart_mixin],

    methods: {

        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'radar',
                data: {

                },
                options: {
                    legend: {
                        display: false
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: this.title
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    scale: {

                            ticks: {
                                min: 0,
                                max: 100,
                                callback: function(label, index, labels) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
							},

				    },
                }
            });

        },
        renderData: function(){
            // have to add it as list, so we'll need to convert it back...
            let data = this.chart_data[0];

            if (data === undefined) {
                // nothing to show
                this.chart.data.labels = [];
                this.chart.data.datasets = [];
                this.chart.update();
                return;
            }

            let labels = Array();
            let chartdata = [];

            console.log(data);

            this.axis.forEach((ax) => {
                if (ax in data) {
                    labels.push(i18n.t("report." + ax));
                    chartdata.push(data[ax].pct_ok);
                }
            });

            this.chart.data.labels = labels;
            this.chart.data.datasets = [{
                data: chartdata,
                backgroundColor: this.color_scheme.primary_background,
                borderColor: this.color_scheme.primary_border,
                borderWidth: 1,
                lineTension: 0,
            }];

            this.chart.update();
        }
    }
});

// done: translations
// todo: add alt description of last values for usability. Is this needed?
// done: place different labels  (add info about date in image)
Vue.component('line-chart', {
    mixins: [chart_mixin],

    methods: {
        // let's see if we can do it even better.
        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'line',
                data: {
                    datasets: []
                },
                options: {
                    legend: {
                        display: false
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'OK / VS Not OK'
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            type: 'time',
                            distribution: 'linear',
                            time: {
                                unit: 'month'
                            },
                            scaleLabel: {
                                display: false,
                                labelString: 'Month'
                            }
                        }],
                        yAxes: [{
                            display: true,
                            stacked: true,
                            scaleLabel: {
                                display: false,
                                labelString: 'Value'
                            }
                        }]
                    }
                }
            });
        },

        renderData: function(){
            let data = this.chart_data;

            let labels = Array();
            let high = Array();
            let medium = Array();
            let low = Array();
            let ok = Array();
            let not_ok = Array();
            let pct_ok = Array();
            let pct_not_ok = Array();

            for(let i=0; i<data.length; i++){
                labels.push(data[i].date);
                high.push(data[i].high);
                medium.push(data[i].medium);
                low.push(data[i].low);
                ok.push(data[i].ok);
                not_ok.push(data[i].not_ok);
                pct_ok.push(data[i].pct_ok);
                pct_not_ok.push(data[i].pct_not_ok);
            }

            this.chart.data.labels = labels;
            this.chart.data.datasets = [
                {
                    label: '# OK',
                    data: ok,
                    backgroundColor: this.color_scheme.ok_background,
                    borderColor: this.color_scheme.ok_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('ok')
                },
                {
                    label: '# Not OK',
                    data: not_ok,
                    backgroundColor: this.color_scheme.high_background,
                    borderColor: this.color_scheme.high_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('not_ok')
                },
                {
                    label: '% OK',
                    data: pct_ok,
                    backgroundColor: this.color_scheme.primary_background,
                    borderColor: this.color_scheme.primary_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('pct_ok')
                },
                {
                    label: '% NOT OK',
                    data: pct_not_ok,
                    backgroundColor: this.color_scheme.high_background,
                    borderColor: this.color_scheme.high_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('pct_not_ok')
                },
            ];

            this.chart.update();
        }
    }
});
</script>
