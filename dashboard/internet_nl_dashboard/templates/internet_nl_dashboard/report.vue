{% verbatim %}
<template type="x-template" id="report_template">
    <div style="width: 100%; min-height: 500px;">
        <div class="block fullwidth">
            <h1>{{ $t("report.header.title") }}</h1>
            <p>{{ $t("report.header.intro") }}</p>

            <multiselect
                    id="select_report"
                    v-model="selected_report"
                    :options="available_recent_reports"
                    label="label"
                    :multiple="true"
                    :track-by="'label'"
                    :placeholder="$t('report.header.select_report')">
            </multiselect>
        </div>

        <div v-if="selected_report && selected_report.length">
            <div class="block fullwidth">
                <div>
                <a class="anchorlink" href="#charts"><button role="button">{{ $t("report.buttons.charts") }}</button></a>
                <a class="anchorlink" href="#report"><button role="button">{{ $t("report.buttons.report") }}</button></a>
                <button @click="show_downloads = !show_downloads">{{ $t("report.buttons.download") }}</button>
                <button @click="show_settings = !show_settings">{{ $t("report.buttons.settings") }}</button>
                </div>
            </div>

            <div v-if="show_settings" class="block fullwidth">
                <h2>{{ $t("report.settings.title") }}</h2>
                <p>{{ $t("report.settings.intro") }}</p>
                <div>
                    <button @click="load_issue_filters()">{{ $t("report.settings.buttons.reset") }}</button>
                    <button @click="save_issue_filters()">{{ $t("report.settings.buttons.save") }}</button>
                </div>
                <div v-if="!this.selected_category">
                    <div v-for="(category_group, category_name, y) in categories" style="width: 49%; float: left;">
                        <div v-if="issue_filters[category_name]">
                            <h3><input type="checkbox" v-model='issue_filters[category_name].visible'> {{ $t("report." + category_name) }}</h3>
                            <span v-for="category_name in category_group">
                                <input type="checkbox" v-model='issue_filters[category_name].visible' :id="category_name + '_visible'">
                                <label :for="category_name + '_visible'">{{ $t("report." + category_name) }}</label><br />
                            </span>
                        </div>
                    </div>
                </div>
                <div v-if="this.selected_category">
                    <!-- Only shows mail or web settings if you're looking at that type of report. -->
                    <div v-for="(category_group, category_name, y) in categories" style="width: calc(33% - 1em); float: left;">
                        <div v-if="issue_filters[category_name] && categories[selected_category].includes(category_name)">
                            <h3><input type="checkbox" v-model='issue_filters[category_name].visible'> {{ $t("report." + category_name) }}</h3>
                            <span v-for="category_name in category_group">
                                <input type="checkbox" v-model='issue_filters[category_name].visible' :id="category_name + '_visible'">
                                <label :for="category_name + '_visible'">{{ $t("report." + category_name) }}</label><br />
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="show_downloads" class="block fullwidth">
                <h2>{{ $t("report.download.title") }}</h2>
                <p>{{ $t("report.download.intro") }}</p>
                <ul>
                    <li><a :href="'/data/download-spreadsheet/' + selected_report.report + '/xlsx/'">{{ $t("report.download.xlsx") }}</a></li>
                    <li><a :href="'/data/download-spreadsheet/' + selected_report.report + '/ods/'">{{ $t("report.download.ods") }}</a></li>
                    <li><a :href="'/data/download-spreadsheet/' + selected_report.report + '/csv/'">{{ $t("report.download.csv") }}</a></li>
                </ul>
            </div>

            <div class="block fullwidth">
                <h2>{{ $t("report.charts.adoption_timeline.annotation.title") }}</h2>
                <a class="anchor" name="charts"></a>
                <p>{{ $t("report.charts.adoption_timeline.annotation.intro") }}</p>

                <div class="chart-container" style="position: relative; height:300px; width:100%">
                    <line-chart
                            :color_scheme="color_scheme"
                            :translation_key="'report.charts.adoption_timeline'"
                            :chart_data="issue_timeline_of_related_urllist"
                            :axis="['pct_ok']">
                    </line-chart>
                </div>
            </div>

            <div class="block fullwidth">
                <h2>
                    {{ $t("report.charts.adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("report.charts.adoption_bar_chart.annotation.intro") }}</p>

                <!--
                Let's see if the compare with previous is still needed while it's possible to compare arbitrary reports...
                <div v-if="older_data_available">
                    <button @click="compare_with_previous()">Compare with previous (beta)</button>
                </div>
                <div v-if="!older_data_available">
                    <button disabled="disabled">Compare with previous (beta)</button>
                </div>
                -->
                <div v-if='reports.length && "statistics_per_issue_type" in reports[0]'>
                    <div class="chart-container" style="position: relative; height:500px; width:100%">
                        <percentage-bar-chart
                                :title="graph_bar_chart_title"
                                :translation_key="'report.charts.adoption_bar_chart'"
                                :color_scheme="color_scheme"
                                :chart_data="compare_charts"
                                @bar_click="select_category"
                                :axis="relevant_categories_based_on_settings()">
                        </percentage-bar-chart>
                    </div>

                    <!--
                    The radar is just another way of expressing the same data. It's nice, but not as good as the bar chart.
                    Code left here in case a graph demo is needed.
                    <div class="chart-container" style="position: relative; height:500px; width:100%">
                        <radar-chart
                                :title="graph_radar_chart_title"
                                :translation_key="'charts.report_radar_chart'"
                                :color_scheme="color_scheme"
                                :chart_data="compare_charts"
                                :axis="relevant_categories_based_on_settings()">
                        </radar-chart>
                    </div>
                    -->

                </div>
            </div>

            <div v-if="filtered_urls !== undefined" class="block fullwidth">
                <h2>{{ $t("report.report.title") }}</h2>
                <a class="anchor" name="report"></a>
                <p>{{ $t("report.report.intro") }}</p>

                <div style="overflow-x: scroll; overflow-y: hidden;">
                    <table class="table table-striped">
                        <thead>

                            <tr>
                                <th style="width: 300px; min-width: 300px; border: 0">
                                    &nbsp;
                                </th>
                                <th style="border: 0" class="rotate" v-for="category in relevant_categories_based_on_settings()">
                                    <div>
                                        <span @click="select_category(category)">{{ $t("report." + category) }}</span>
                                    </div>
                                </th>
                            </tr>

                            <!-- Zoom buttons for accessibility -->
                            <tr v-if="reports.length" class="summaryrow">
                                <template v-if="['web', 'mail'].includes(selected_category)">
                                    <td>

                                    </td>
                                    <td v-for="category_name in relevant_categories_based_on_settings()">
                                        <button @click="select_category(category_name)">{{ $t("report.report.zoom.buttons.zoom") }}</button>
                                    </td>
                                </template>
                                <template v-if="!['web', 'mail'].includes(selected_category)">
                                    <td></td>
                                    <td :colspan="relevant_categories_based_on_settings().length" style="text-align: center">
                                    {{ $t("report.report.zoom.zoomed_in_on") }} {{ $t("report." + selected_category) }}.
                                        <button @click="select_category(selected_report.urllist_scan_type)">
                                            ❌ {{ $t("report.report.zoom.buttons.remove_zoom") }}
                                        </button>
                                    </td>
                                </template>
                            </tr>

                            <!-- Summary row, same data as bar chart, but then in numbers.-->
                            <tr v-if="reports.length" class="summaryrow">
                                <td>
                                    <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.report.url_filter')">
                                </td>
                                <td v-for="category_name in relevant_categories_based_on_settings()" @click="select_category(category_name)">
                                    <span v-if="category_name in reports[0].statistics_per_issue_type">
                                        {{reports[0].statistics_per_issue_type[category_name].pct_ok}}%</span>
                                </td>
                            </tr>


                        </thead>
                        <tbody v-if="filtered_urls.length" class="gridtable">
                            <tr v-for="url in filtered_urls" v-if="url.endpoints.length">
                                <td>{{url.url}}
                                    <span v-if="selected_report.type === 'web'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation)"></span>
                                    <span v-if="selected_report.type === 'mail'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation)"></span>
                                </td>
                                <td class="testresultcell" v-for="category_name in relevant_categories_based_on_settings()" @click="select_category(category_name)">
                                    <template v-if="['web', 'mail'].includes(selected_category)">
                                        <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                            <!-- Currently the API just says True or False, we might be able to deduce the right label for a category, but that will take a day or two.
                                            At the next field update, we'll also make the categories follow the new format of requirement level and testresult so HTTP Security Headers
                                             here is shown as optional, or info if failed. We can also add a field for baseline NL government then. -->
                                            <template v-if="url.endpoints[0].ratings_by_type[category_name].ok < 1">
                                                <span v-if="category_name !== 'internet_nl_web_appsecpriv'" class="category_failed"  :title="$t('report.' + category_name + '_verdict_bad')">
                                                    {{ $t("report.report.results.failed") }}
                                                </span>
                                                <span v-if="category_name === 'internet_nl_web_appsecpriv'" class="category_warning" :title="$t('report.' + category_name + '_verdict_bad')">
                                                    {{ $t("report.report.results.warning") }}
                                                </span>
                                            </template>
                                            <span class="category_passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0" :title="$t('report.' + category_name + '_verdict_good')">
                                                {{ $t("report.report.results.passed") }}
                                            </span>
                                        </template>
                                        <span class="" v-if="url.endpoints[0].ratings_by_type[category_name] === undefined">
                                            {{ $t("report.report.results.unknown") }}
                                        </span>
                                    </template>
                                    <template v-if="!['web', 'mail'].includes(selected_category)">
                                        <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                            <span class="not_applicable" v-if="url.endpoints[0].ratings_by_type[category_name].not_applicable > 0" :title="$t('report.not_applicable')">
                                                {{ $t("report.report.results.not_applicable") }}
                                            </span>
                                            <span class="not_testable" v-if="url.endpoints[0].ratings_by_type[category_name].not_testable > 0" :title="$t('report.not_testable')">
                                                {{ $t("report.report.results.not_testable") }}
                                            </span>
                                            <span class="failed" v-if="url.endpoints[0].ratings_by_type[category_name].high > 0" :title="$t('report.' + category_name + '_verdict_bad')">
                                                {{ $t("report.report.results.failed") }}
                                            </span>
                                            <span class="warning" v-if="url.endpoints[0].ratings_by_type[category_name].medium > 0" :title="$t('report.' + category_name + '_verdict_bad')">
                                                {{ $t("report.report.results.warning") }}
                                            </span>
                                            <span class="info" v-if="url.endpoints[0].ratings_by_type[category_name].low > 0" :title="$t('report.' + category_name + '_verdict_bad')">
                                                {{ $t("report.report.results.info") }}
                                            </span>
                                            <span class="passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0
                                            && !url.endpoints[0].ratings_by_type[category_name].not_applicable
                                            && !url.endpoints[0].ratings_by_type[category_name].not_testable" :title="$t('report.' + category_name + '_verdict_good')">
                                                {{ $t("report.report.results.passed") }}
                                            </span>
                                        </template>
                                        <span class="" v-if="url.endpoints[0].ratings_by_type[category_name] === undefined">
                                            {{ $t("report.report.results.unknown") }}
                                        </span>
                                    </template>
                                </td>
                            </tr>

                        </tbody>
                        <tbody v-if="!filtered_urls.length">
                            <tr>
                               <td :colspan="relevant_categories_based_on_settings().length + 1" style="text-align: center;">😱 {{ $t("report.report.empty_report") }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
        <autorefresh :visible="false" :callback="get_recent_reports"></autorefresh>
    </div>
</template>
{% endverbatim %}

<script>
// Done: order of the fields, and possible sub sub categories
// Done: allow filtering on what results to show
// Done: store filter options for reports (as generic or per report? or as a re-applicable set?) Per user account.
// Done: how to add a item for legacy views?
// Done: how to translate graphs?
vueReport = new Vue({
    i18n,
    name: 'report',
    el: '#report',
    template: '#report_template',
    mixins: [humanize_mixin, http_mixin],
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
                'internet_nl_web_ipv6',
                'internet_nl_web_dnssec',
                'internet_nl_web_tls',
                'internet_nl_web_appsecpriv',  // Added 24 May 2019
                'web_legacy'
            ],

            'internet_nl_web_ipv6': [
                'internet_nl_web_ipv6_ns_address',
                'internet_nl_web_ipv6_ns_reach',

                'internet_nl_web_ipv6_ws_address',
                'internet_nl_web_ipv6_ws_reach',
                'internet_nl_web_ipv6_ws_similar',
            ],

            'internet_nl_web_dnssec': [
                'internet_nl_web_dnssec_exist',
                'internet_nl_web_dnssec_valid',
            ],

            'internet_nl_web_tls': [
                // HTTP
                'internet_nl_web_https_http_available',
                'internet_nl_web_https_http_redirect',
                'internet_nl_web_https_http_compress',
                'internet_nl_web_https_http_hsts',

                // TLS
                'internet_nl_web_https_tls_version',
                'internet_nl_web_https_tls_ciphers',
                'internet_nl_web_https_tls_keyexchange',
                'internet_nl_web_https_tls_compress',
                'internet_nl_web_https_tls_secreneg',
                'internet_nl_web_https_tls_clientreneg',

                // Certificate
                'internet_nl_web_https_cert_chain',
                'internet_nl_web_https_cert_pubkey',
                'internet_nl_web_https_cert_sig',
                'internet_nl_web_https_cert_domain',

                // DANE
                'internet_nl_web_https_dane_exist',
                'internet_nl_web_https_dane_valid',
            ],

            // Added 24 May 2019
            'internet_nl_web_appsecpriv': [
                'internet_nl_web_appsecpriv_x_frame_options',
                'internet_nl_web_appsecpriv_x_content_type_options',
                'internet_nl_web_appsecpriv_x_xss_protection',
                'internet_nl_web_appsecpriv_csp',
                'internet_nl_web_appsecpriv_referrer_policy',
            ],

            // order as in the magazine
            'web_legacy': [
                'internet_nl_web_legacy_dnssec',
                'internet_nl_web_legacy_tls_available',
                'internet_nl_web_legacy_tls_ncsc_web',
                'internet_nl_web_legacy_https_enforced',
                'internet_nl_web_legacy_hsts',
                'internet_nl_web_legacy_ipv6_nameserver',
                'internet_nl_web_legacy_ipv6_webserver',
                'internet_nl_web_legacy_dane',
            ],

            'mail': [
                'internet_nl_mail_dashboard_ipv6',
                'internet_nl_mail_dashboard_dnssec',
                'internet_nl_mail_dashboard_auth',
                'internet_nl_mail_dashboard_tls',
                'mail_legacy'
            ],

            'internet_nl_mail_dashboard_ipv6': [
                // name servers
                'internet_nl_mail_ipv6_ns_address',
                'internet_nl_mail_ipv6_ns_reach',

                // mail server(s)
                'internet_nl_mail_ipv6_mx_address',
                'internet_nl_mail_ipv6_mx_reach',
            ],

            'internet_nl_mail_dashboard_dnssec': [
                // email address domain
                'internet_nl_mail_dnssec_mailto_exist',
                'internet_nl_mail_dnssec_mailto_valid',

                // mail server domain(s)
                'internet_nl_mail_dnssec_mx_exist',
                'internet_nl_mail_dnssec_mx_valid',
            ],

            'internet_nl_mail_dashboard_auth': [
                // DMARC
                'internet_nl_mail_auth_dmarc_exist',
                'internet_nl_mail_auth_dmarc_policy',
                'internet_nl_mail_auth_dmarc_policy_only',  // Added 24th of May 2019
                'internet_nl_mail_auth_dmarc_ext_destination',  // Added 24th of May 2019

                // DKIM
                'internet_nl_mail_auth_dkim_exist',

                // SPF
                'internet_nl_mail_auth_spf_exist',
                'internet_nl_mail_auth_spf_policy',
            ],

            'internet_nl_mail_dashboard_tls': [
                // TLS
                'internet_nl_mail_starttls_tls_available',
                'internet_nl_mail_starttls_tls_version',
                'internet_nl_mail_starttls_tls_ciphers',
                'internet_nl_mail_starttls_tls_keyexchange',
                'internet_nl_mail_starttls_tls_compress',
                'internet_nl_mail_starttls_tls_secreneg',
                'internet_nl_mail_starttls_tls_clientreneg',

                // Certificate
                'internet_nl_mail_starttls_cert_chain',
                'internet_nl_mail_starttls_cert_pubkey',
                'internet_nl_mail_starttls_cert_sig',
                'internet_nl_mail_starttls_cert_domain',

                // DANE
                'internet_nl_mail_starttls_dane_exist',
                'internet_nl_mail_starttls_dane_valid',
                'internet_nl_mail_starttls_dane_rollover',
            ],

            'mail_legacy': [
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
                'internet_nl_mail_legacy_ipv6_nameserver',
                'internet_nl_mail_legacy_ipv6_mailserver',
            ],
        },

        // settings
        show_settings: false,
        issue_filters: {
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

            'internet_nl_mail_legacy_dmarc': {'visible': true},
            'internet_nl_mail_legacy_dkim': {'visible': true},
            'internet_nl_mail_legacy_spf': {'visible': true},
            'internet_nl_mail_legacy_dmarc_policy': {'visible': true},
            'internet_nl_mail_legacy_spf_policy': {'visible': true},
            'internet_nl_mail_legacy_start_tls': {'visible': true},
            'internet_nl_mail_legacy_start_tls_ncsc': {'visible': true},
            'internet_nl_mail_legacy_dnssec_email_domain': {'visible': true},
            'internet_nl_mail_legacy_dnssec_mx': {'visible': true},
            'internet_nl_mail_legacy_dane': {'visible': true},
            'internet_nl_mail_legacy_ipv6_nameserver': {'visible': true},
            'internet_nl_mail_legacy_ipv6_mailserver': {'visible': true},

            'internet_nl_web_legacy_dnssec': {'visible': true},
            'internet_nl_web_legacy_tls_available': {'visible': true},
            'internet_nl_web_legacy_tls_ncsc_web': {'visible': true},
            'internet_nl_web_legacy_https_enforced': {'visible': true},
            'internet_nl_web_legacy_hsts': {'visible': true},
            'internet_nl_web_legacy_ipv6_nameserver': {'visible': true},
            'internet_nl_web_legacy_ipv6_webserver': {'visible': true},
            'internet_nl_web_legacy_dane': {'visible': true},

            // Fields added on the 24th of May 2019
            'internet_nl_mail_auth_dmarc_policy_only': {'visible': true},  // Added 24th of May 2019
            'internet_nl_mail_auth_dmarc_ext_destination': {'visible': true},  // Added 24th of May 2019

            // no feature flags in report
            //'internet_nl_mail_non_sending_domain': {'visible': true},  // Added 24th of May 2019
            //'internet_nl_mail_server_configured': {'visible': true},  // Added 24th of May 2019
            //'internet_nl_mail_servers_testable': {'visible': true},   // Added 24th of May 2019
            //'internet_nl_mail_starttls_dane_ta': {'visible': true},  // Added 24th of May 2019

            'internet_nl_web_appsecpriv': {'visible': true},  // Added 24th of May 2019
            'internet_nl_web_appsecpriv_csp': {'visible': true},  // Added 24th of May 2019
            'internet_nl_web_appsecpriv_referrer_policy': {'visible': true},  // Added 24th of May 2019
            'internet_nl_web_appsecpriv_x_content_type_options': {'visible': true},  // Added 24th of May 2019
            'internet_nl_web_appsecpriv_x_frame_options': {'visible': true},  // Added 24th of May 2019
            'internet_nl_web_appsecpriv_x_xss_protection': {'visible': true},  // Added 24th of May 2019

        },

        issue_filters_save_response: null,

        // url_filter allows the filtering of names in the list of urls.
        url_filter: '',

        selected_category: '',

        // such basic functionality missing in vue, it even got removed.
        debounce_timer: 0,

        available_recent_reports: [],
        selected_report: null,

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
            incremental: [
                {background: 'rgba(255, 112, 50, 0.6)', border: 'rgba(255, 112, 50, 1)'},
                {background: 'rgba(21, 66, 115, 0.6)', border: 'rgba(21, 66, 115, 1)'},
                {background: 'rgba(255, 246, 0, 0.6)', border: 'rgba(255, 246, 0, 1)'},
                {background: 'rgba(0, 255, 246, 0.6)', border: 'rgba(0, 255, 246, 1)'},
                {background: 'rgba(255, 0, 246, 0.6)', border: 'rgba(255, 0, 246, 1)'},
                ]
        },
        compare_charts: [],
        compare_oldest_data: "",
        older_data_available: true,

        show_downloads: false,

    },
    mounted: function(){
        this.load_issue_filters();
        this.get_recent_reports();
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
            fetch(`/data/report/get/${report_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.reports = data;
                // remove implicit behavior
                // this.reset_comparison_charts(this.reports[0]);

                this.selected_category = this.selected_report[0].urllist_scan_type;

                this.original_urls = data[0].calculation.urls.sort(this.alphabet_sorting);
                this.older_data_available = true;

                // sort urls alphabetically
                // we'll probably just need a table control that does sorting, filtering and such instead of coding it ourselves.
                this.filtered_urls = data[0].calculation.urls.sort(this.alphabet_sorting);
                this.get_timeline();
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        save_issue_filters: function(){
            /*
            * This overrides the account level issue filters. Filters are saved per account and this is done by
            * design. This prevents the 'having to reset for each report or for each user' dilemma, which results
            * in some kind of hierarchical settings mess that results in incomparable reports over several users.
            * And then the users need to sync the settings and so on. Knowing this limitation would probably remove
            * a lot of time of development while end users can still have an organization wide consistent experience
            * on what they are focussing on. Humans > tech.
            * */
            this.asynchronous_json_post(
                '/data/account/report_settings/save/', {'filters': this.issue_filters}, (server_response) => {
                    this.issue_filters_save_response = server_response;
                }
            );
        },
        load_issue_filters: function(){
            fetch(`/data/account/report_settings/get/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                if (!jQuery.isEmptyObject(data)) {
                    this.issue_filters = data;
                }
            });
        },
        alphabet_sorting: function(a, b){
            // i already mis sorted()
            if (a.url < b.url) {
                return -1;
            }
            if (a.url > b.url) {
                return 1;
            }
            return 0;
        },
        reset_comparison_charts: function(report){
            this.compare_charts = [report];
            this.compare_oldest_data = report.at_when;
        },
        compare_with_previous: function(){
            // can be clicked on as long as there are previous reports. Which we don't know in advance.

            fetch(`/data/report/get_previous/${this.selected_report[0].urllist_id}/${this.compare_oldest_data}/`, {credentials: 'include'}).then(response => response.json()).then(report => {

                if (!jQuery.isEmptyObject(report)) {
                    this.compare_charts.push(report);
                    this.compare_oldest_data = report.at_when;
                } else {
                    this.older_data_available = false;
                }

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});


        },
        compare_with: function(id){
            fetch(`/data/report/get/${id}/`, {credentials: 'include'}).then(response => response.json()).then(report => {

                if (!jQuery.isEmptyObject(report)) {
                    this.compare_charts.push(report[0]);
                }

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        get_recent_reports: function(){
            fetch(`/data/report/recent/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].label = `#${data[i].id} - ${data[i].list_name} - type: ${data[i].type} - from: ${this.humanize_date(data[i].at_when)}`;
                    options.push(data[i])
                }
                this.available_recent_reports = options;

                // if the page was requested with a page ID, start loading that report.
                // this supports: http://localhost:8000/reports/83/
                if (window.location.href.split('/').length > 3) {
                    get_id = window.location.href.split('/')[4];
                    // can we change the select2 to a certain value?

                    this.available_recent_reports.forEach((option) => {
                       if (option.id + "" === get_id){
                           // also re-create label
                           option.label = `#${option.id} - ${option.list_name} - type: ${option.type} - from: ${this.humanize_date(option.at_when)}`;
                           this.selected_report = [option];
                       }
                    });
                } else {
                    // focus on report selection
                    // $('select_report').focus();
                }

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        relevant_categories_based_on_settings: function(){
            let preferred_fields = this.categories[this.selected_category];
            let returned_fields = [];
            for(let i = 0; i<preferred_fields.length; i++){

                // When new fields are introduced, the list filters will be outdated and contain missing fields.
                // todo: fix
                if(this.issue_filters[preferred_fields[i]].visible)
                    returned_fields.push(preferred_fields[i])
            }
            return returned_fields;
        },
        select_category: function(category_name){
            if (Object.keys(this.categories).includes(category_name))
                this.selected_category = category_name;
            else
                this.selected_category = this.selected_report[0].urllist_scan_type;
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

            if (this.selected_report[0].urllist_id === 0) {
                return;
            }

            fetch(`/data/report/urllist_report_graph_data/${this.selected_report[0].urllist_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.issue_timeline_of_related_urllist = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});

        },
        original_report_link_from_score: function(score){
            if (!score){
                return ""
            }

            // score = 66 https://batch.internet.nl/site/dev2.internet.nl/664025/
            let sc = score.split(" ");

            if (sc.length < 1){
                return ""
            }

            if (!sc[1].startsWith('http')){
                return ""
            }

            return `<a class='direct_link_to_report' href='${sc[1]}' target="_blank">${sc[0]}%</a>`
        }
    },
    watch: {
        selected_report: function (new_value, old_value) {
            console.log(`New value: ${new_value}`);
            console.log(`Old value: ${old_value}`);

            // totally empty list, list was emptied by clicking the crosshair everywhere.
            if (new_value[0] === undefined){
                console.log('List was emptied');
                this.reports=[];
                return;
            }

            this.load(new_value[0].id);
            this.compare_charts = [];
            for(let i=0; i<new_value.length; i++){
                console.log(`Comparing with report ${new_value[i].id}`);
                this.compare_with(new_value[i].id);
            }
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
            return i18n.t('report.charts.adoption_radar_chart.title', {
                'list_information': this.selected_report[0].list_name,
                'number_of_domains': this.original_urls.length
            });
        },

        graph_bar_chart_title: function(){
            return i18n.t('report.charts.adoption_bar_chart.title', {
                'list_information': this.selected_report[0].list_name,
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
                ref: 'canvas',

                // Improve accessibility: https://www.chartjs.org/docs/latest/general/accessibility.html
                // Using createElement features: https://vuejs.org/v2/guide/render-function.html#createElement-Arguments
                attrs: {
                    role: "img",
                    'aria-label': this.title
                },
                // todo: add child element with title, probably not updateable with data in graph
            },
            [
                createElement('p', this.title),
            ]
        )
    },
    mounted: function () {
        this.buildChart();
        this.renderData();
    },
    methods: {
        arraysEqual: function (a, b) {
            // One does not simply array1 === array2, which is a missed opportunity, as (some of the) the most optimized implementation should ship to anyone.
            if (a === b) return true;
            if (a == null || b == null) return false;

            // intended type coercion
            if (a.length != b.length) return false;

            // If you don't care about the order of the elements inside
            // the array, you should sort both arrays here.
            // Please note that calling sort on an array will modify that array.
            // you might want to clone your array first.

            for (let i = 0; i < a.length; ++i) {
                if (a[i] !== b[i]) return false;
            }
            return true;
        }
    },
    watch: {
        chart_data: function(new_value, old_value){
            this.renderData();
        },
        axis: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },

        title: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderTitle();
            }
        },

        // Supports changing the colors of this graph ad-hoc.
        // charts.js is not reactive.
        color_scheme: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },
    }
};

// this prevents the legend being written over the 100% scores
Chart.Legend.prototype.afterFit = function() {
    this.height = this.height + 20;
};

Vue.component('percentage-bar-chart', {
    i18n,
    mixins: [chart_mixin, humanize_mixin],

    methods: {

        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'bar',
                data: {},
                options: {

                    // can prevent data falling off the chart.
                    layout: {
                        padding: {
                            left: 0,
                            right: 0,
                            top: 0,
                            bottom: 0
                        }
                    },
                    plugins:{
                        datalabels: {
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
                        display: true,
                        position: 'top',
                        labels: {
                            padding: 15,
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        position: 'top',
                        display: true,
                        text: this.title,
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
                    onClick: (event, item) => {
                        if (item[0] === undefined) {
                            return;
                        }

                        if (item[0]._chart.tooltip._lastActive[0] === undefined){
                            return;
                        }

                        // todo: handle zooming, this is optional / a nice to have.
                        let localChart = item[0]._chart;
                        let activeIndex = localChart.tooltip._lastActive[0]._index;
                        let clickCoordinates = Chart.helpers.getRelativePosition(event, localChart.chart);
                        if (clickCoordinates.y >= 0) { //custom value, depends on chart style,size, etc
                            this.$emit('bar_click', localChart.data.axis_names[activeIndex]);
                            // console.log("clicked on " + localChart.data.labels[activeIndex]);
                        }
                    }
                }
            });
        },
        renderData: function(){
            // prevent the grapsh from ever growing (it's called twice at first render)
            this.chart.data.axis_names = [];
            this.chart.data.labels = [];
            this.chart.data.datasets = [];

            for(let i=0; i < this.chart_data.length; i++){

                let data = this.chart_data[i].statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    this.chart.data.axis_names = [];
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                let axis_names = [];
                let labels = [];
                let chartdata = [];

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        labels.push(i18n.t("report." + ax));
                        axis_names.push(ax);
                        chartdata.push(data[ax].pct_ok);
                    }
                });

                this.chart.data.axis_names = axis_names;
                this.chart.data.labels = labels;
                this.chart.data.datasets.push({
                    data: chartdata,
                    backgroundColor: this.color_scheme.incremental[i].background,
                    borderColor: this.color_scheme.incremental[i].border,
                    borderWidth: 1,
                    lineTension: 0,
                    label: `${this.chart_data[i].calculation.name} ${moment(this.chart_data[i].at_when).format('LL')}`,
                });

            }

            // the ordering is from important to none important, and we want to reverse it so the reader sees that
            // the right most value is the most important instead of the left one.
            this.chart.data.datasets.reverse();
            // the same goes for colors
            // this.chart.data.labels.reverse();


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
                    plugins:{
                        datalabels: {
                            // todo: when the value > 50, the label should be placed on the inside to not overlap labels
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
                        display: true,
                        position: 'top',
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
                                    // not needed anymore, but code kept as reference if datalabels breaks
                                    return '';
                                    // return label + '%';
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

            this.chart.data.labels = [];
            this.chart.data.datasets = [];

            for(let i=0; i < this.chart_data.length; i++){

                let data = this.chart_data[i].statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                let labels = Array();
                let chartdata = [];

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        labels.push(i18n.t("report." + ax));
                        chartdata.push(data[ax].pct_ok);
                    }
                });

                this.chart.data.labels = labels;
                this.chart.data.datasets.push({
                    data: chartdata,
                    backgroundColor: this.color_scheme.incremental[i].background,
                    borderColor: this.color_scheme.incremental[i].border,
                    borderWidth: 1,
                    lineTension: 0,
                    label: `${moment(this.chart_data[i].at_when).format('LL')}`,
                });

            }

            // the ordering is from important to none important, and we want to reverse it so the reader sees that
            // the right most value is the most important instead of the left one.
            this.chart.data.datasets.reverse();
            // the same goes for colors
            // this.chart.data.labels.reverse();

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
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
                    plugins:{
                        datalabels: {
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
                        text: i18n.t(this.translation_key + '.title')
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
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});
</script>
