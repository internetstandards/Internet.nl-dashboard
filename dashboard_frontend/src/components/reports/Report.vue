<style>

</style>

<template>
    <div id="report-template">
        <div class="block fullwidth do-not-print">
            <h1>{{ $t("header.title") }}</h1>
            <p>{{ $t("header.intro") }}</p>

            <div aria-live="polite" style="margin-bottom: 30px;">
                <v-select
                    v-model="selected_report"
                    :placeholder="$t('header.select_report')"
                    :options="filtered_recent_reports"
                    label="label"
                    :multiple="true"
                    :selectable="() => selected_report.length < 6"
                >
                    <slot name="no-options">{{ $t('header.no_options') }}</slot>

                </v-select>
            </div>

            <template v-if="reports.length && !is_loading">

                <collapse-panel :title='$t("download.title") ' class="do-not-print" v-if="selected_report.length < 2">
                    <div slot="content">
                        <p>{{ $t("download.intro") }}</p>
                        <ul style="list-style: disc !important; padding-left: 20px">
                            <li><a :href="make_downloadlink(reports[0].id, 'xlsx')">{{ $t("download.xlsx") }}</a></li>
                            <li><a :href="make_downloadlink(reports[0].id, 'ods')">{{ $t("download.ods") }}</a></li>
                            <li><a :href="make_downloadlink(reports[0].id, 'csv')">{{ $t("download.csv") }}</a></li>
                        </ul>
                    </div>
                </collapse-panel>

                <collapse-panel :title='$t("settings.title")' class="do-not-print">
                    <div slot="content">
                        <VisibleMetrics :scan_methods="scan_methods"
                                        :report_type="selected_report[0].type"></VisibleMetrics>
                    </div>
                </collapse-panel>

            </template>

        </div>

        <loading :loading="is_loading"></loading>

        <div v-if="reports.length && !is_loading">

            <div class="block fullwidth">
                <h2>
                    📊 #{{ selected_report[0].id }} - {{ selected_report[0].list_name }}</h2>
                <span>{{ $t("report_header.type_of_scan_performed") }}:
                    <img src="/static/images/vendor/internet_nl/icon-website-test.svg" style="height: 1em;"
                         v-if="selected_report[0].type === 'web'">
                    <img src="/static/images/vendor/internet_nl/icon-emailtest.svg" style="height: 1em;"
                         v-if="selected_report[0].type === 'mail'"> {{ selected_report[0].type }}<br>
                    {{ $t("report_header.number_of_domains") }}: {{
                        selected_report[0].number_of_urls
                    }}<br> {{ $t("report_header.data_from") }} {{ humanize_date(selected_report[0].at_when) }}<br>
                    📘 <router-link :to="{ name: 'numbered_lists', params: { list: selected_report[0].urllist_id }}">{{
                            selected_report[0].list_name
                        }}</router-link><br>
                </span><br>


                <template v-if="selected_report.length > 1">
                    <div v-for="report in selected_report" style="padding-left: 10px" :key="report.id">
                        <!-- Skip the first report -->
                        <template v-if="report.id !== selected_report[0].id">
                            <h3>{{ $t("report_header.compared_to") }}: #{{ report.id }} - {{ report.list_name }}</h3>
                            <span>
                            {{ $t("report_header.number_of_domains") }}: {{ report.number_of_urls }}<br>
                            {{ $t("report_header.data_from") }} {{ humanize_date(report.at_when) }}<br>
                            📘 <router-link :to="{ name: 'numbered_lists', params: { list: report.urllist_id }}">{{
                                    report.list_name
                                }}</router-link><br>
                        </span>
                        </template>
                    </div>
                </template>

                <template v-if="selected_report.length > 2">
                    <p style="padding-top: 1em;">⚠️ {{ $t("report_header.only_graphs") }}</p>
                </template>

            </div>

            <ReportCharts
                :selected_report="selected_report"
                :scan_methods="scan_methods"
                :compare_charts="compare_charts"
                :issue_filters="visible_metrics"
                :selected_report_ids="selected_report_ids"
                :field_name_to_category_names="field_name_to_category_names"
            >
            </ReportCharts>

            <!-- The table is only displayed with up to two reports (the first as the source of the table, the second as a comparison). -->
            <div v-if="original_urls !== undefined && selected_report.length < 3" class="block fullwidth"
                 style="page-break-before: always;">

                <ReportTable
                    :differences_compared_to_current_list="differences_compared_to_current_list"
                    :field_name_to_category_names="field_name_to_category_names"
                    :original_urls="original_urls"
                    :report_category="report_category"
                    :scan_methods="scan_methods"
                    :compare_charts="compare_charts"
                ></ReportTable>
            </div>

        </div>
        <!-- The dropdown with recent reports is updated automatically when scans finish. But if that page
         had never loaded, this is a fallback that still tries to get the recent report every ten minutes. -->
        <autorefresh :visible="false" :callback="get_recent_reports" :refresh_per_seconds="600"></autorefresh>
    </div>
</template>

<script>
// Done: order of the fields, and possible sub sub categories
// Done: allow filtering on what results to show
// Done: store filter options for reports (as generic or per report? or as a re-applicable set?) Per user account.
// Done: how to add a item for legacy views?
// Done: how to translate graphs?
import field_translations from './../field_translations'

import ReportCharts from './ReportCharts'
import VisibleMetrics from './VisibleMetrics'
import ReportTable from './ReportTable'


export default {
    components: {
        ReportCharts,
        VisibleMetrics,
        ReportTable
    },
    i18n: {
        sharedMessages: field_translations,
        messages: {
            en: {
                mail: 'E-Mail',
                web: 'Web',
                settings: {
                    title: "Select visible metrics",
                },
                header: {
                    title: 'Reports',
                    intro: 'It is possible to select one or multiple reports. Selecting a single report shows all data of that report, ' +
                        'including graphs and a table with detailed results. Selecting two reports, a comparison is made between these reports in the graphs and detailed result. ' +
                        'Selecting more than two reports, only graphs are shown.',
                    select_report: 'Select report...',
                    max_elements: 'Maximum number of reports selected.',
                    no_options: 'No reports available.',
                },
                download: {
                    title: 'Download metrics as a spreadsheet',
                    intro: 'Report data is available in the following formats:',
                    xlsx: 'Excel Spreadsheet (Microsoft Office), .xlsx',
                    ods: 'Open Document Spreadsheet (Libre Office), .ods',
                    csv: 'Comma Separated (for programmers), .csv',
                },
                // These fields do not have a hierarchical translation, this is how they are in websecmap.
                // they are not 1-1 with the frontend. So have their own label for greater consistency.
                // Test results
                not_testable: 'Not testable',
                not_applicable: 'Not applicable',
                error_in_test: "Test error",
                report_header: {
                    type_of_scan_performed: "Type of scan performed",
                    compared_to: "Compared to",
                    number_of_domains: "Number of domains",
                    data_from: "Data from",
                    only_graphs: "Only showing the timeline and graphs because there are more than two reports selected.",
                }
            },
            nl: {
                mail: 'E-Mail',
                web: 'Web',
                settings: {
                    title: "Selecteer zichtbare meetwaarden",
                },
                header: {
                    title: 'Rapporten',
                    intro: 'Het is mogelijk om meerdere rapporten te selecteren. Bij het selecteren van een enkel rapport wordt alle relevante informatie hierover getoond. ' +
                        'Bij het selecteren van twee rapporten wordt een vergelijking gemaakt: zowel in de grafieken als in de detail tabel. Bij het selecteren van ' +
                        'meer dan twee rapporten zijn alleen de grafieken zichtbaar.',
                    select_report: 'Selecteer rapport...',
                    max_elements: 'Maximum aantal rapporten geselecteerd.',
                    no_options: 'Geen rapporten beschikbaar.',
                },
                download: {
                    title: 'Downloaden',
                    intro: 'De data in dit rapport is beschikbaar in de volgende formaten:',
                    xlsx: 'Excel Spreadsheet (voor o.a. Microsoft Office), .xlsx',
                    ods: 'Open Document Spreadsheet (voor o.a. Libre Office), .ods',
                    csv: 'Comma Separated (voor programmeurs), .csv',
                },
                report_header: {
                    type_of_scan_performed: "Uitgevoerde scan",
                    compared_to: "Vergeleken met",
                    number_of_domains: "Aantal domeinen",
                    data_from: "Rapportage van",
                    only_graphs: "Enkel de tijdlijn en grafieken worden getoond omdat er meer dan twee rapporten zijn geselecteerd.",
                }
            }
        }
    },
    name: 'report',
    data: function () {
        return {

            is_loading: false,

            // Supporting multiple reports at the same time is hard to understand. Don't know how / if we can do
            // comparisons.
            reports: [],

            // The first report is displayed in the table, it is desired to see if there are different with the
            // current list.
            differences_compared_to_current_list: {},

            // instead we support one report with one set of urls. This is the source set of urls that can be copied at will
            original_urls: [],

            // settings
            report_category: '',

            available_recent_reports: [],

            // the filtered set only shows the same type as the first scan shown. It's not possible to open
            // two reports of the same type, as the UI is not capable ofhandling that ... as all fields differ and there
            // is really no comparison possible.
            filtered_recent_reports: [],

            // a list of reports...
            selected_report: [],

            // a list used to highlight certain reports in the timeline graph.
            selected_report_ids: [],

            // show category headers in table only when there is a change of category:
            previous_category: "",

            compare_charts: [],
            compare_oldest_data: "",
        }
    },
    mounted: function () {
        this.load_visible_metrics();

        this.get_recent_reports();
        // this supports: http://localhost:8000/reports/83/
        // todo: this can be replaced by $route.params.report, which is much more readable.

        // why is this not done at nextTick?
        // because the report selection has not been loaded yet, so move this to the result of get latest reports...
        // and you only want to do this at load of the page, not every time latest report is called.
        setTimeout(() => {
            if (window.location.href.split('/').length > 3) {
                let primary_report_id = window.location.href.split('/')[6];
                let secondary_report_id = window.location.href.split('/')[7];
                // can we change the select2 to a certain value?

                this.filtered_recent_reports.forEach((option) => {
                    // Create label
                    option.label = `#${option.id} - ${option.list_name} - type: ${option.type} - from: ${this.humanize_date(option.at_when)}`;
                });

                let reports_to_select = [];
                // The primary report
                this.filtered_recent_reports.forEach((option) => {
                    if (option.id + "" === primary_report_id) {
                        reports_to_select.push(option);
                    }
                });

                // loop again, so we're sure the first report is the primary report,
                // and a compared report is compared:
                this.filtered_recent_reports.forEach((option) => {
                    if (option.id + "" === secondary_report_id) {
                        reports_to_select.push(option);
                    }
                });

                this.selected_report = reports_to_select;
            }
        }, 1500)
    },

    methods: {

        make_downloadlink: function (report_id, filetype) {
            return `${this.$store.state.dashboard_endpoint}/data/download-spreadsheet/${report_id}/${filetype}/`
        },

        load: function (report_id) {
            this.get_report_data(report_id);
        },

        get_report_data: function (report_id) {
            this.is_loading = true;
            // You'll notice a load time at a random point in this function, this means Vue is processing the response.
            fetch(`${this.$store.state.dashboard_endpoint}/data/report/get/${report_id}/`, {credentials: 'include'})
                .then(response => response.json()).then(data => {
                this.reports = data;
                this.report_category = this.selected_report[0].urllist_scan_type;
                this.original_urls = data[0].calculation.urls.sort(this.alphabet_sorting);

                // we already have the first report, so don't request it again.
                // note that when setting the first chart, the subsequent updates do not "point ot a new object"
                // so a state change doesn not happen automatically using a wathcer, you have to watch deep.
                // console.log(`First compare chart set...`);
                this.$set(this.compare_charts, 0, data[0]);
                // this.compare_charts.$set(0, );

                this.is_loading = false;
                // new accordions are created, reduce their size.
                this.$nextTick(() => {
                    this.$forceUpdate()
                });
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });

            fetch(`${this.$store.state.dashboard_endpoint}/data/report/differences_compared_to_current_list/${report_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.differences_compared_to_current_list = data;
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

        alphabet_sorting: function (a, b) {
            // i already mis sorted()
            if (a.url < b.url) {
                return -1;
            }
            if (a.url > b.url) {
                return 1;
            }
            return 0;
        },

        compare_with: function (id, compare_chart_id) {
            fetch(`${this.$store.state.dashboard_endpoint}/data/report/get/${id}/`, {credentials: 'include'}).then(response => response.json()).then(report => {

                if (!this.isEmptyObject(report)) {
                    // The comparison report require direct data access to urls to be able to compare
                    // by simply reading data directly without scanning the table.
                    report[0].calculation.urls_by_url = {};
                    report[0].calculation.urls.forEach((url) => {
                        report[0].calculation.urls_by_url[url.url] = url;
                    });

                    // this will work fine, as all the prior id's will be filled with reports too...
                    // js behaves unacceptably, but in this case it's fine.
                    // example: i = [];
                    // i[3] = "a"
                    // i is then Array(4) [ undefined, undefined, undefined, "a" ]...
                    // https://vuejs.org/2016/02/06/common-gotchas/#Why-isn%E2%80%99t-the-DOM-updating
                    // note that the documentation is plain wrong, as arr.$set is NOT a method on the array,
                    // but on the vm. And thus the syntax for using it differs from the docs.
                    // console.log(`Compare chart ${compare_chart_id} set...`);
                    this.$set(this.compare_charts, compare_chart_id, report[0]);

                    // given the charts are on a fixed number in the array, vue doesn't pick up changes.
                    // and as the order matters, this is a solution that fixes that.
                    this.$nextTick(() => {
                        this.$forceUpdate();
                    });
                }

            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

        get_recent_reports: function () {
            // reload the select
            fetch(`${this.$store.state.dashboard_endpoint}/data/report/recent/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                // console.log("Get recent reports");
                let options = [];
                for (let i = 0; i < data.length; i++) {
                    data[i].label = `#${data[i].id} - ${data[i].list_name} - type: ${data[i].type} - from: ${this.humanize_date(data[i].at_when)}`;
                    options.push(data[i]);
                }
                this.available_recent_reports = options;
                this.filtered_recent_reports = options;
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

    },
    watch: {

        // support keep alive routing
        $route: function (to) {
            // https://router.vuejs.org/guide/essentials/dynamic-matching.html
            if (undefined !== to.params.report) {
                // See if we can find a report to mach. Has to updated in 1 go due to the watch.
                let reports_to_select = [];

                // The primary report
                this.available_recent_reports.forEach((item) => {
                    if (item.id === to.params.report) {
                        reports_to_select.push(item);
                    }
                });

                // loop again, so we're sure the first report is the primary report,
                // and a compared report is compared:
                this.available_recent_reports.forEach((item) => {
                    if (item.id === to.params.compare_with) {
                        reports_to_select.push(item);
                    }
                });

                this.selected_report = reports_to_select;
            }
        },

        selected_report: function (new_value) {
            // when multiple items are selected, the old value is always 1 item, the new one is always 2 items.
            // as such it is not possible to determine reload without trickery safely...

            // totally empty list, list was emptied by clicking the crosshair everywhere.
            if (new_value[0] === undefined) {
                // console.log('List was emptied');

                // all reports are available again:
                this.filtered_recent_reports = this.available_recent_reports;

                this.reports = [];
                this.selected_report_ids = [];
                this.is_loading = false;
                return;
            } else {
                this.selected_report_ids = [];
                for (let i = 0; i < new_value.length; i++) {
                    this.selected_report_ids.push(new_value[i].id);
                }
            }

            // Always update the URL to reflect the latest report, so it can be easily shared and the page reloaded
            if (new_value.length > 1) {
                history.pushState(
                    {},
                    null,
                    '/spa/#/report/' + new_value[0].id + '/' + new_value[1].id
                );
            } else {
                history.pushState(
                    {},
                    null,
                    '/spa/#/report/' + new_value[0].id
                );
            }

            // when deleting any report, we will need to rebuild the compare charts...
            this.compare_charts = [];
            this.load(new_value[0].id);

            // to test this:
            // this.compare_with(new_value[0].id, 1);
            // this.compare_with(new_value[0].id, 2);

            // filter reports on type:
            let filtered_reports = [];
            this.available_recent_reports.forEach((item) => {
                if (item.type === new_value[0].type) {
                    filtered_reports.push(item);
                }
            });
            this.filtered_recent_reports = filtered_reports;

            // we already have the first chart, don't load that again.
            // the first chart is always loaded through the load method.
            for (let i = 1; i < new_value.length; i++) {
                // console.log(`Comparing with report ${new_value[i].id}`);
                // todo: this causes an extra load of the data, which is slow... At least it always works
                // without syncing issues etc...
                // i = the compare chart id, so even if the reports load asyncronous, the array order is
                // maintained in the compare charts, and thus in the graphs.
                this.compare_with(new_value[i].id, i);
            }
        },
        amount_of_finished_scans: function (new_value, old_value) {
            // If there are more scans finished, this list is updated.
            if (new_value === old_value)
                return;

            this.get_recent_reports();
        },

    },
    computed: {
        visible_metrics: function () {
            return this.$store.state.visible_metrics;
        },
        scan_methods: function () {
            /*
            * This is a hierarchy that makes sense in representing the large amount of metrics.
            * This hierarchy is shared in all reports parts and visible metric configuration.
            * */
            return [
                {
                    name: 'web',
                    fields: [],

                    label: this.$i18n.t('web'),
                    categories: [
                        {
                            name: 'ipv6',
                            label: this.$i18n.t('internet_nl_web_ipv6'),
                            // key is being used by selected categories to not iterate through fields.
                            key: 'internet_nl_web_ipv6',
                            fields: [
                                {name: 'internet_nl_web_ipv6'}
                            ],


                            categories: [
                                {
                                    name: 'Name servers',
                                    key: 'category_web_ipv6_name_server',
                                    // there is NO translations for web, only for mail.
                                    label: this.$i18n.t('category_web_ipv6_name_server'),
                                    fields: [
                                        {name: 'internet_nl_web_ipv6_ns_address'},
                                        {name: 'internet_nl_web_ipv6_ns_reach'},
                                    ],

                                },
                                {
                                    name: 'Web server',
                                    key: 'category_web_ipv6_web_server',
                                    label: this.$i18n.t('category_web_ipv6_web_server'),
                                    fields: [
                                        {name: 'internet_nl_web_ipv6_ws_address'},
                                        {name: 'internet_nl_web_ipv6_ws_reach'},
                                        {name: 'internet_nl_web_ipv6_ws_similar'},
                                    ],

                                }
                            ]
                        },
                        {
                            name: 'dnssec',
                            label: this.$i18n.t('internet_nl_web_dnssec'),
                            key: 'internet_nl_web_dnssec',
                            fields: [
                                {name: 'internet_nl_web_dnssec'}
                            ],

                            categories: [
                                {
                                    // the exception to the rule
                                    name: 'DNSSEC',
                                    key: 'category_web_dnssec_dnssec',
                                    label: this.$i18n.t('category_web_dnssec_dnssec'),
                                    fields: [
                                        {name: 'internet_nl_web_dnssec_exist'},
                                        {name: 'internet_nl_web_dnssec_valid'},
                                    ],

                                },
                            ]
                        },
                        {
                            name: 'tls',
                            label: this.$i18n.t('internet_nl_web_tls'),
                            key: 'internet_nl_web_tls',
                            fields: [
                                {name: 'internet_nl_web_tls'},
                            ],

                            categories: [
                                {
                                    name: 'HTTP',
                                    key: 'category_web_tls_http',
                                    label: this.$i18n.t('category_web_tls_http'),
                                    fields: [
                                        {name: 'internet_nl_web_https_http_available'},
                                        {name: 'internet_nl_web_https_http_redirect'},
                                        {name: 'internet_nl_web_https_http_compress'},
                                        {name: 'internet_nl_web_https_http_hsts'},
                                    ],

                                },
                                {
                                    name: 'TLS',
                                    key: 'category_web_tls_tls',
                                    label: this.$i18n.t('category_web_tls_tls'),
                                    fields: [
                                        {name: 'internet_nl_web_https_tls_version'},
                                        {name: 'internet_nl_web_https_tls_ciphers'},
                                        {name: 'internet_nl_web_https_tls_cipherorder'},
                                        {name: 'internet_nl_web_https_tls_keyexchange'},
                                        {name: 'internet_nl_web_https_tls_keyexchangehash'},
                                        {name: 'internet_nl_web_https_tls_compress'},
                                        {name: 'internet_nl_web_https_tls_secreneg'},
                                        {name: 'internet_nl_web_https_tls_clientreneg'},
                                        {name: 'internet_nl_web_https_tls_0rtt'},
                                        {name: 'internet_nl_web_https_tls_ocsp'},
                                    ],
                                },
                                {
                                    name: 'Certificate',
                                    key: 'category_web_tls_certificate',
                                    // mail is being reused as there is no alternative translation (!)
                                    label: this.$i18n.t('category_web_tls_certificate'),
                                    fields: [
                                        {name: 'internet_nl_web_https_cert_chain'},
                                        {name: 'internet_nl_web_https_cert_pubkey'},
                                        {name: 'internet_nl_web_https_cert_sig'},
                                        {name: 'internet_nl_web_https_cert_domain'},
                                    ],

                                },
                                {
                                    name: 'DANE',
                                    key: 'category_web_tls_dane',
                                    label: this.$i18n.t('category_web_tls_dane'),
                                    fields: [
                                        {name: 'internet_nl_web_https_dane_exist'},
                                        {name: 'internet_nl_web_https_dane_valid'},
                                    ],

                                }
                            ]
                        },
                        {
                            name: 'security_options',
                            label: this.$i18n.t('internet_nl_web_appsecpriv'),
                            key: 'internet_nl_web_appsecpriv',
                            fields: [
                                {name: 'internet_nl_web_appsecpriv'},
                            ],


                            categories: [
                                {
                                    name: 'HTTP security headers',
                                    key: 'category_web_security_options_appsecpriv',
                                    label: this.$i18n.t('category_web_security_options_appsecpriv'),
                                    fields: [
                                        {name: 'internet_nl_web_appsecpriv_x_frame_options'},
                                        {name: 'internet_nl_web_appsecpriv_x_content_type_options'},
                                        {name: 'internet_nl_web_appsecpriv_csp'},
                                        {name: 'internet_nl_web_appsecpriv_referrer_policy'},
                                    ],

                                }
                            ]

                        },
                        {
                            name: 'forum_standardisation',
                            label: this.$i18n.t('web_legacy'),
                            key: 'web_legacy',
                            fields: [
                                {name: 'web_legacy'},
                            ],


                            categories: [
                                {
                                    name: 'Baseline NL Government',
                                    key: 'category_web_forum_standardisation_magazine',
                                    label: 'Baseline NL Government',
                                    fields: [
                                        {
                                            name: 'internet_nl_web_legacy_dnssec',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_dnssec_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_tls_available',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_available_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_tls_ncsc_web',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_ncsc_web_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_https_enforced',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_https_enforced_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_hsts',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_hsts_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_category_ipv6',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_ipv6_nameserver',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'
                                        },
                                        {
                                            name: 'internet_nl_web_legacy_ipv6_webserver',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_webserver_explanation'
                                        },
                                    ],

                                },
                                {
                                    name: 'Status Fields',
                                    key: 'category_web_forum_standardisation_status_fields',
                                    label: this.$i18n.t('fields.forum_standardistation.status_fields'),
                                    fields: [
                                        {
                                            name: 'internet_nl_web_legacy_tls_1_3',
                                            explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_1_3_explanation'
                                        },
                                    ],

                                }
                            ]
                        }
                    ]
                },
                {
                    name: 'mail',
                    fields: [],
                    label: this.$i18n.t('mail'),
                    categories: [
                        {
                            name: 'IPv6',
                            label: this.$i18n.t('internet_nl_mail_dashboard_ipv6'),
                            key: 'internet_nl_mail_dashboard_ipv6',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_ipv6'}
                            ],


                            categories: [
                                {
                                    name: 'Name servers',
                                    key: 'category_mail_ipv6_name_servers',
                                    label: this.$i18n.t('category_mail_ipv6_name_servers'),
                                    fields: [
                                        {name: 'internet_nl_mail_ipv6_ns_address'},
                                        {name: 'internet_nl_mail_ipv6_ns_reach'},
                                    ],

                                },
                                {
                                    name: 'Mail server(s)',
                                    key: 'category_mail_ipv6_mail_servers',
                                    label: this.$i18n.t('category_mail_ipv6_mail_servers'),
                                    fields: [
                                        {name: 'internet_nl_mail_ipv6_mx_address'},
                                        {name: 'internet_nl_mail_ipv6_mx_reach'},
                                    ],

                                }
                            ]
                        },
                        {
                            name: 'DNSSEC',
                            label: this.$i18n.t('internet_nl_mail_dashboard_dnssec'),
                            key: 'internet_nl_mail_dashboard_dnssec',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_dnssec',}
                            ],

                            categories: [
                                {
                                    name: 'Email address domain',
                                    key: 'category_mail_dnssec_email_address_domain',
                                    label: this.$i18n.t('category_mail_dnssec_email_address_domain'),
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mailto_exist'},
                                        {name: 'internet_nl_mail_dnssec_mailto_valid'},
                                    ],

                                },
                                {
                                    name: 'Mail server domain(s)',
                                    key: 'category_mail_dnssec_mail_server_domain',
                                    label: this.$i18n.t('category_mail_dnssec_mail_server_domain'),
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mx_exist'},
                                        {name: 'internet_nl_mail_dnssec_mx_valid'},
                                    ],
                                },
                            ]
                        },
                        {
                            name: 'DMARC, DKIM and SPF',
                            label: this.$i18n.t('internet_nl_mail_dashboard_auth'),
                            key: 'internet_nl_mail_dashboard_auth',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_auth'}
                            ],

                            categories: [
                                {
                                    name: 'DMARC',
                                    key: 'category_mail_dashboard_auth_dmarc',
                                    label: this.$i18n.t('category_mail_dashboard_auth_dmarc'),
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dmarc_exist'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy'},
                                    ],

                                },
                                {
                                    name: 'DKIM',
                                    key: 'category_mail_dashboard_aut_dkim',
                                    label: this.$i18n.t('category_mail_dashboard_aut_dkim'),
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dkim_exist'},
                                    ],

                                },
                                {
                                    name: 'SPF',
                                    key: 'category_mail_dashboard_aut_spf',
                                    label: this.$i18n.t('category_mail_dashboard_aut_spf'),
                                    fields: [
                                        {name: 'internet_nl_mail_auth_spf_exist'},
                                        {name: 'internet_nl_mail_auth_spf_policy'},
                                    ],

                                },
                            ]
                        },
                        {
                            name: 'STARTTLS and DANE',
                            label: this.$i18n.t('internet_nl_mail_dashboard_tls'),
                            key: 'internet_nl_mail_dashboard_tls',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_tls'},
                            ],

                            categories: [
                                {
                                    name: 'TLS',
                                    key: 'category_mail_starttls_tls',
                                    label: this.$i18n.t('category_mail_starttls_tls'),
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_tls_available'},
                                        {name: 'internet_nl_mail_starttls_tls_version'},
                                        {name: 'internet_nl_mail_starttls_tls_ciphers'},
                                        {name: 'internet_nl_mail_starttls_tls_cipherorder'},
                                        {name: 'internet_nl_mail_starttls_tls_keyexchange'},
                                        {name: 'internet_nl_mail_starttls_tls_keyexchangehash'},
                                        {name: 'internet_nl_mail_starttls_tls_compress'},
                                        {name: 'internet_nl_mail_starttls_tls_secreneg'},
                                        {name: 'internet_nl_mail_starttls_tls_clientreneg'},
                                        {name: 'internet_nl_mail_starttls_tls_0rtt'},
                                    ],

                                },
                                {
                                    name: 'Certificate',
                                    key: 'category_mail_starttls_certificate',
                                    label: this.$i18n.t('category_mail_starttls_certificate'),
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_cert_chain'},
                                        {name: 'internet_nl_mail_starttls_cert_pubkey'},
                                        {name: 'internet_nl_mail_starttls_cert_sig'},
                                        {name: 'internet_nl_mail_starttls_cert_domain'},
                                    ],

                                },
                                {
                                    name: 'DANE',
                                    key: 'category_mail_starttls_dane',
                                    label: this.$i18n.t('category_mail_starttls_dane'),
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_dane_exist'},
                                        {name: 'internet_nl_mail_starttls_dane_valid'},
                                        {name: 'internet_nl_mail_starttls_dane_rollover'},
                                    ],


                                },
                            ]
                        },
                        {
                            name: 'forum_standardisation',
                            label: this.$i18n.t('mail_legacy'),
                            key: 'mail_legacy',
                            fields: [
                                {
                                    name: 'mail_legacy',
                                },
                            ],


                            categories: [
                                {
                                    name: 'Baseline NL Government',
                                    label: 'Baseline NL Government',
                                    key: 'category_mail_forum_standardisation_magazine',
                                    fields: [
                                        {
                                            name: 'internet_nl_mail_legacy_dmarc',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dmarc_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_dkim',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dkim_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_spf',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_spf_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_dmarc_policy',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dmarc_policy_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_spf_policy',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_spf_policy_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_start_tls',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_start_tls_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_start_tls_ncsc',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_start_tls_ncsc_explanation'
                                        },
                                        // {name: 'internet_nl_mail_legacy_dnssec_email_domain'},
                                        {
                                            name: 'internet_nl_mail_legacy_dnssec_mx',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dnssec_mx_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_dane',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dane_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_category_ipv6',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_category_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_ipv6_nameserver',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_nameserver_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_ipv6_mailserver',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_mailserver_explanation'
                                        },

                                    ],

                                },

                                {
                                    name: 'Status Fields',
                                    key: 'category_web_forum_standardisation_status_fields',
                                    label: this.$i18n.t('fields.forum_standardistation.status_fields'),
                                    fields: [
                                        {
                                            name: 'internet_nl_mail_legacy_tls_1_3',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_tls_1_3_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_domain_has_mx',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_domain_has_mx_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_mail_server_reachable',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_server_reachable_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_mail_server_testable',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_server_testable_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_mail_non_sending_domain',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_non_sending_domain_explanation'
                                        },
                                        {
                                            name: 'internet_nl_mail_legacy_mail_sending_domain',
                                            explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_sending_domain_explanation'
                                        },
                                    ],

                                }
                            ]
                        }
                    ]
                }
            ];
        },

        field_name_to_category_names: function () {
            /** Based on the scan methods, the names of the categories is 1-1 associated with a category name.
             * This can be used to generate "category" headers in the result table. This helps to distinguish
             * several chapter headings for a set of scans. This is useful for mail dnssec scans, as the
             * name of the dnssec tests is identical and very confusing to see what is what. */

            let fields_mapping = {};

            // 0 = web, 1 = mail, ugly.
            this.scan_methods[0].categories.forEach((category) => {

                category.categories.forEach((subcategory) => {
                    subcategory.fields.forEach((field) => {
                        fields_mapping[field.name] = subcategory.name;
                    });
                });
            });

            this.scan_methods[1].categories.forEach((category) => {

                category.categories.forEach((subcategory) => {
                    subcategory.fields.forEach((field) => {
                        fields_mapping[field.name] = subcategory.name;
                    });
                });
            });

            return fields_mapping;
        },

        amount_of_finished_scans: function () {
            // this helps auto-reloading the list of available reports

            // In the case no scans
            if (this.$store.state.scan_monitor_data.length === 0)
                return 0;

            let finished = 0;
            // the first scan-monitor record where list_id is the same, is the one with the most recent state
            for (let i = 0; i < this.$store.state.scan_monitor_data.length; i++) {
                if (this.$store.state.scan_monitor_data[i].state === "finished") {
                    finished++;
                }
            }
            return finished;
        }
    }
}
</script>
