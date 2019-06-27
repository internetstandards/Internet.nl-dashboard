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
                    :limit="5"
                    :maxElements="$t('report.header.max_elements')"
                    :noOptions="$t('report.header.no_options')"
                    :placeholder="$t('report.header.select_report')">
            </multiselect>

            &nbsp;<br>

            <template v-if="reports.length && !is_loading">

                <div class="testresult">
                    <h2 class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("report.download.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <p>{{ $t("report.download.intro") }}</p>
                        <ul>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/xlsx/'">{{ $t("report.download.xlsx") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/ods/'">{{ $t("report.download.ods") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/csv/'">{{ $t("report.download.csv") }}</a></li>
                        </ul>
                    </div>
                </div>

                <div class="testresult">
                    <h2 class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("report.settings.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <p>{{ $t("report.settings.intro") }}</p>
                        <div>
                            <button @click="load_issue_filters()">{{ $t("report.settings.buttons.reset") }}</button>
                            <button @click="save_issue_filters()">{{ $t("report.settings.buttons.save") }}</button>
                        </div>
                        <template v-for="scan_form in scan_methods">
                            <template v-if="scan_form.name === selected_report[0].type">

                                <h3 style="font-size: 2em; margin-top: 20px; margin-bottom: 10px;">{{ scan_form.label }}</h3>

                                <template v-if="scan_form.additional_fields.length">
                                    <div class="test-subsection">{{ $t("report.fields.additional_fields.label") }}</div>
                                    <div v-for="field in scan_form.additional_fields" class="testresult">
                                    <label :for="field.name + '_visible'">
                                        <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                        {{ $t("report." + field.name) }}
                                    </label>
                                    </div>
                                </template>

                                <template v-for="category in scan_form.categories">
                                    <section class="test-header">
                                        <hr>
                                        <div class="test-title">
                                            <h4 style="font-size: 1.6em; margin-top: 20px; margin-bottom: 10px;">{{ category.label }}</h4>
                                            <p>
                                                <template v-for="field in category.fields">
                                                    <label :for="field.name + '_visible'">
                                                        <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                        View this category
                                                    </label>
                                                </template>

                                                <template v-if="category.additional_fields.length">
                                                    <div class="test-subsection">{{ $t("report.fields.additional_fields.label") }}</div>
                                                    <div v-for="field in category.additional_fields" class="testresult">
                                                    <label :for="field.name + '_visible'">
                                                        <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                        {{ $t("report." + field.name) }}
                                                    </label>
                                                    </div>
                                                </template>

                                            </p>
                                        </div>
                                    </section>
                                    <section class="testresults">
                                        <br>
                                        <template v-for="category in category.categories">
                                            <div class="test-subsection">{{ category.label }}</div>

                                            <div v-for="field in category.fields" class="testresult">
                                                <label :for="field.name + '_visible'">
                                                    <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                    {{ $t("report." + field.name) }}
                                                </label>
                                            </div>

                                            <template v-if="category.additional_fields.length">
                                                <div class="test-subsection">{{ $t("report.fields.additional_fields.label") }}</div>
                                                <div v-for="field in category.additional_fields" class="testresult">
                                                <label :for="field.name + '_visible'">
                                                    <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                    {{ $t("report." + field.name) }}
                                                </label>
                                                </div>
                                            </template>

                                        </template>
                                    </section>
                                </template>
                            </template>
                        </template>
                    </div>
                </div>
            </template>

        </div>

        <loading :loading="is_loading"></loading>

        <div v-if="reports.length && !is_loading">

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

            <div class="block fullwidth" v-if='reports.length && "statistics_per_issue_type" in reports[0]'>
                <!-- Accessible alternative for the data is available in the table below. -->
                <h2>
                    {{ $t("report.charts.adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("report.charts.adoption_bar_chart.annotation.intro") }}</p>

                <template v-for="scan_form in scan_methods">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 500px;">
                            <percentage-bar-chart
                                    :title="graph_bar_chart_title"
                                    :translation_key="'report.charts.adoption_bar_chart'"
                                    :color_scheme="color_scheme"
                                    :chart_data="compare_charts"
                                    @bar_click="select_category"
                                    :axis="fields_from_categories(scan_form)">
                            </percentage-bar-chart>
                        </div>


                        <template v-for="category in scan_form.categories">
                            <div class="testresult" v-if="is_visible(category.key)">
                                <h3 class="panel-title">
                                    <a href="" aria-expanded="false">
                                        <span class="visuallyhidden">-:</span>
                                        {{ category.label }}
                                        <span class="pre-icon visuallyhidden"></span>
                                        <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                    </a>
                                </h3>
                                <div class="panel-content">
                                    <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 500px;">
                                        <percentage-bar-chart
                                                :title="graph_bar_chart_title"
                                                :translation_key="'report.charts.adoption_bar_chart'"
                                                :color_scheme="color_scheme"
                                                :chart_data="compare_charts"
                                                @bar_click="select_category"
                                                :axis="fields_from_categories(category)">
                                        </percentage-bar-chart>
                                    </div>
                                </div>
                            </div>
                        </template>

                    </template>
                </template>
            </div>

            <div class="block fullwidth" aria-hidden="true" v-if='compare_charts.length > 1 && "statistics_per_issue_type" in reports[0]'>
                <!-- Todo: there is no cumulative view in the table below, so cumulative data is not (yet) accessible :( -->
                <h2>
                    {{ $t("report.charts.cumulative_adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("report.charts.cumulative_adoption_bar_chart.annotation.intro") }}</p>

                <template v-for="scan_form in scan_methods">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 500px;">
                            <cumulative-percentage-bar-chart
                                    :title="$t('report.charts.cumulative_adoption_bar_chart.title', {
                                                    'number_of_reports': compare_charts.length})"
                                    :translation_key="'report.charts.adoption_bar_chart'"
                                    :color_scheme="color_scheme"
                                    :chart_data="compare_charts"
                                    @bar_click="select_category"
                                    :axis="fields_from_categories(scan_form)">
                            </cumulative-percentage-bar-chart>
                        </div>

                        <template v-for="category in scan_form.categories">
                            <div class="testresult" v-if="is_visible(category.key)">
                                <h3 class="panel-title">
                                    <a href="" aria-expanded="false">
                                        <span class="visuallyhidden">-:</span>
                                        {{ category.label }}
                                        <span class="pre-icon visuallyhidden"></span>
                                        <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                    </a>
                                </h3>
                                <div class="panel-content">
                                    <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 500px;">
                                        <cumulative-percentage-bar-chart
                                                :title="$t('report.charts.cumulative_adoption_bar_chart.title', {
                                                    'number_of_reports': compare_charts.length})"
                                                :translation_key="'report.charts.adoption_bar_chart'"
                                                :color_scheme="color_scheme"
                                                :chart_data="compare_charts"
                                                @bar_click="select_category"
                                                :axis="fields_from_categories(category)">
                                        </cumulative-percentage-bar-chart>
                                    </div>
                                </div>
                            </div>
                        </template>

                    </template>
                </template>
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
                                <th style="border: 0" class="rotate" v-for="category in relevant_categories_based_on_settings">
                                    <div>
                                        <span @click="select_category(category)">{{ $t("report." + category) }}</span>
                                    </div>
                                </th>
                            </tr>

                        </thead>

                        <tbody class="gridtable">
                            <template>
                                <!-- Summary row, same data as bar chart, but then in numbers.-->
                                <tr v-if="reports.length" class="summaryrow">
                                    <td>
                                        &nbsp;
                                    </td>
                                    <td v-for="category_name in relevant_categories_based_on_settings" @click="select_category(category_name)">
                                        <span v-if="category_name in reports[0].statistics_per_issue_type">
                                            {{reports[0].statistics_per_issue_type[category_name].pct_ok}}%</span>
                                    </td>
                                </tr>

                                <!-- Zoom buttons for accessibility -->
                                <tr v-if="reports.length" class="summaryrow">
                                    <template v-if="['web', 'mail'].includes(selected_category)">
                                        <td>
                                            <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.report.url_filter')">
                                        </td>
                                        <td v-for="category_name in relevant_categories_based_on_settings">
                                            <button @click="select_category(category_name)">{{ $t("report.report.zoom.buttons.zoom") }}</button>
                                        </td>
                                    </template>
                                    <template v-if="!['web', 'mail'].includes(selected_category)">
                                        <td>
                                            <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.report.url_filter')">
                                        </td>
                                        <td :colspan="relevant_categories_based_on_settings.length" style="text-align: center">
                                        {{ $t("report.report.zoom.zoomed_in_on") }} {{ $t("report." + selected_category) }}.
                                            <button @click="select_category(selected_report.urllist_scan_type)">
                                                ❌ {{ $t("report.report.zoom.buttons.remove_zoom") }}
                                            </button>
                                        </td>
                                    </template>
                                </tr>
                            </template>

                            <template v-if="!filtered_urls.length">
                                <tr>
                                    <td :colspan="relevant_categories_based_on_settings.length + 1" style="text-align: center;">😱 {{ $t("report.report.empty_report") }}</td>
                                </tr>
                            </template>

                            <template v-if="filtered_urls.length">

                                <tr v-for="url in filtered_urls" v-if="url.endpoints.length">
                                    <td>{{url.url}}
                                        <span v-if="selected_report[0].type === 'web'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation)"></span>
                                        <span v-if="selected_report[0].type === 'mail'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation)"></span>
                                    </td>
                                    <td class="testresultcell" v-for="category_name in relevant_categories_based_on_settings" @click="select_category(category_name)">
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
                            </template>
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
        is_loading: false,

        // Supporting multiple reports at the same time is hard to understand. Don't know how / if we can do
        // comparisons.
        reports: [],

        // instead we support one report with one set of urls. This is the source set of urls that can be copied at will
        original_urls: [],

        // this is the set of urls where filters are applied.
        filtered_urls:[],

        // todo: this could/should be computed.
        categories: {
            // fallback category
            '': [],
            'web': [],
            'internet_nl_web_ipv6': [],
            'internet_nl_web_dnssec': [],
            'internet_nl_web_tls': [],
            'internet_nl_web_appsecpriv': [],
            'web_legacy': [],
            'mail': [],
            'internet_nl_mail_dashboard_ipv6': [],
            'internet_nl_mail_dashboard_dnssec': [],
            'internet_nl_mail_dashboard_auth': [],
            'internet_nl_mail_dashboard_tls': [],
            'mail_legacy': [],
        },

        // settings
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
            'internet_nl_mail_non_sending_domain': {'visible': false},  // Added 24th of May 2019
            'internet_nl_mail_server_configured': {'visible': false},  // Added 24th of May 2019
            'internet_nl_mail_servers_testable': {'visible': false},   // Added 24th of May 2019
            'internet_nl_mail_starttls_dane_ta': {'visible': false},  // Added 24th of May 2019

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
            // https://github.com/ashiguruma/patternomaly/blob/master/assets/pattern-list.png
            incremental: [
                {background: pattern.draw('weave',  'rgba(255, 112, 50, 0.6)'), border: 'rgba(255, 112, 50, 1)'},
                {background: pattern.draw('dot',  'rgba(21, 66, 115, 0.6)'), border: 'rgba(21, 66, 115, 1)'},
                {background: pattern.draw('ring',  'rgba(43, 151, 89, 0.6)'), border: 'rgba(43, 151, 89, 1)'},
                {background: pattern.draw('dash',  'rgba(0, 255, 246, 0.6)'), border: 'rgba(0, 255, 246, 1)'},
                {background: pattern.draw('triangle',  'rgba(255, 0, 246, 0.6)'), border: 'rgba(255, 0, 246, 1)'},
                ]
        },
        compare_charts: [],
        compare_oldest_data: "",
        older_data_available: true,

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

        get_issue_filter_data(key){
            try {
                return this.issue_filters[key];
            } catch(err) {
                this.issue_filters[key] = {'visible': true};
                console.log(`Issue filter for ${key} does not exist. Created it.`)
            }
        },

        get_report_data: function(report_id){
            this.is_loading = true;
            fetch(`/data/report/get/${report_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.reports = data;

                this.selected_category = this.selected_report[0].urllist_scan_type;

                this.original_urls = data[0].calculation.urls.sort(this.alphabet_sorting);
                this.older_data_available = true;

                // sort urls alphabetically
                // we'll probably just need a table control that does sorting, filtering and such instead of coding it ourselves.
                this.filtered_urls = data[0].calculation.urls.sort(this.alphabet_sorting);
                this.get_timeline();
                this.is_loading = false;

                // new accordions are created, reduce their size.
                this.$nextTick(() => accordinate());
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

                    // upgrade existing issue filters with new fields:
                    this.upgrade_issue_filter_with_new_field('internet_nl_mail_non_sending_domain');
                    this.upgrade_issue_filter_with_new_field('internet_nl_mail_server_configured');
                    this.upgrade_issue_filter_with_new_field('internet_nl_mail_servers_testable');
                    this.upgrade_issue_filter_with_new_field('internet_nl_mail_starttls_dane_ta');
                }
            });
        },

        upgrade_issue_filter_with_new_field: function(field_name){
            if (!Object.keys(this.issue_filters).includes(field_name))
                        this.issue_filters[field_name] = {'visible': false}
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
        compare_with: function(id){
            fetch(`/data/report/get/${id}/`, {credentials: 'include'}).then(response => response.json()).then(report => {

                if (!jQuery.isEmptyObject(report)) {
                    this.compare_charts.push(report[0]);
                    this.$nextTick(() => accordinate());
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
        },
        fields_from_categories(categories){
            let fields = [];

            categories.categories.forEach((category) => {

                category.fields.forEach((field) => {
                    fields.push(field.name);
                });
                category.additional_fields.forEach((field) => {
                    fields.push(field.name);
                });

            });

            let returned_fields = [];
            for(let i = 0; i<fields.length; i++){

                if(this.issue_filters[fields[i]].visible)
                    returned_fields.push(fields[i])
            }
            return returned_fields;
        },
        is_visible(field_name){
            try {
                return this.issue_filters[field_name].visible;
            } catch(e) {
                return false;
            }
        }
    },
    watch: {
        selected_report: function (new_value, old_value) {
            // console.log(`New value: ${new_value}`);
            // console.log(`Old value: ${old_value}`);

            // totally empty list, list was emptied by clicking the crosshair everywhere.
            if (new_value[0] === undefined){
                // console.log('List was emptied');
                this.reports=[];
                this.is_loading = false;
                return;
            }

            this.load(new_value[0].id);
            this.compare_charts = [];
            for(let i=0; i<new_value.length; i++){
                // console.log(`Comparing with report ${new_value[i].id}`);
                // todo: this causes an extra load of the data, which is slow... At least it always works
                // without syncing issues etc...
                this.compare_with(new_value[i].id);
            }
        },
        url_filter: function(newValue, oldValue){
            this.filter_urls(newValue);
            // aside from debouncing not working, as it doesn't understand the vue context, it is not needed
            // up until 400 + items in the list.
            // this.debounce(function() {this.methods.filter_urls(newValue);});
        },
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

        scan_methods: function() {

            let language = get_cookie('dashboard_language');
            if (language === undefined || language.length > 3){
                language = "en"
            }

            return [
                {
                    name: 'web',
                    fields: [],
                    additional_fields: [],
                    label: internet_nl_messages[language].internet_nl.base_test_website_label,
                    categories: [
                        {
                            name: 'ipv6',
                            label: internet_nl_messages[language].internet_nl.test_siteipv6_label,
                            // key is being used by selected categories to not iterate through fields.
                            key: 'internet_nl_web_ipv6',
                            fields: [
                                {name: 'internet_nl_web_ipv6'}
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'name_servers',
                                    // there is NO translations for web, only for mail.
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_ipv6_name_servers_label,
                                    fields: [
                                        {name: 'internet_nl_web_ipv6_ns_address'},
                                        {name: 'internet_nl_web_ipv6_ns_reach'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'web_server',
                                    label: internet_nl_messages[language].internet_nl.results_domain_ipv6_web_server_label,
                                    fields: [
                                        {name: 'internet_nl_web_ipv6_ws_address'},
                                        {name: 'internet_nl_web_ipv6_ws_reach'},
                                        {name: 'internet_nl_web_ipv6_ws_similar'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        },
                        {
                            name: 'dnssec',
                            label: internet_nl_messages[language].internet_nl.test_sitednssec_label,
                            key: 'internet_nl_web_dnssec',
                            fields: [
                                {name: 'internet_nl_web_dnssec'}
                            ],
                            additional_fields: [],
                            categories: [
                                {
                                    // the exception to the rule
                                    name: '',
                                    label: '',
                                    fields: [
                                        {name: 'internet_nl_web_dnssec_exist'},
                                        {name: 'internet_nl_web_dnssec_valid'},
                                    ],
                                    additional_fields: [],
                                },
                            ]
                        },
                        {
                            name: 'tls',
                            label: internet_nl_messages[language].internet_nl.test_sitetls_label,
                            key: 'internet_nl_web_tls',
                            fields: [
                                {name: 'internet_nl_web_tls'},
                            ],
                            additional_fields: [],
                            categories: [
                                {
                                    name: 'http',
                                    label: internet_nl_messages[language].internet_nl.results_domain_tls_https_label,
                                    fields: [
                                        {name: 'internet_nl_web_https_http_available'},
                                        {name: 'internet_nl_web_https_http_redirect'},
                                        {name: 'internet_nl_web_https_http_compress'},
                                        {name: 'internet_nl_web_https_http_hsts'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'tls',
                                    label: internet_nl_messages[language].internet_nl.results_domain_tls_tls_label,
                                    fields: [
                                        {name: 'internet_nl_web_https_tls_version'},
                                        {name: 'internet_nl_web_https_tls_ciphers'},
                                        {name: 'internet_nl_web_https_tls_keyexchange'},
                                        {name: 'internet_nl_web_https_tls_compress'},
                                        {name: 'internet_nl_web_https_tls_secreneg'},
                                        {name: 'internet_nl_web_https_tls_clientreneg'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'certificate',
                                    // mail is being reused as there is no alternative translation (!)
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_tls_certificate_label,
                                    fields: [
                                        {name: 'internet_nl_web_https_cert_chain'},
                                        {name: 'internet_nl_web_https_cert_pubkey'},
                                        {name: 'internet_nl_web_https_cert_sig'},
                                        {name: 'internet_nl_web_https_cert_domain'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'dane',
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_tls_dane_label,
                                    fields: [
                                        {name: 'internet_nl_web_https_dane_exist'},
                                        {name: 'internet_nl_web_https_dane_valid'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        },
                        {
                            name: 'security_options',
                            label: internet_nl_messages[language].internet_nl.test_siteappsecpriv_label,
                            key: 'internet_nl_web_appsecpriv',
                            fields: [
                                {name: 'internet_nl_web_appsecpriv'},
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'HTTP security headers',
                                    label: internet_nl_messages[language].internet_nl.results_domain_appsecpriv_http_headers_label,
                                    fields: [
                                        {name: 'internet_nl_web_appsecpriv_x_frame_options'},
                                        {name: 'internet_nl_web_appsecpriv_x_content_type_options'},
                                        {name: 'internet_nl_web_appsecpriv_x_xss_protection'},
                                        {name: 'internet_nl_web_appsecpriv_csp'},
                                        {name: 'internet_nl_web_appsecpriv_referrer_policy'},
                                    ],
                                    additional_fields: [],
                                }
                            ]

                        },
                        {
                            name: 'forum_standardisation',
                            label: i18n.t('report.fields.forum_standardistation.category_label'),
                            key: 'web_legacy',
                            fields: [
                                {name: 'web_legacy'},
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'magazine',
                                    label: i18n.t('report.fields.forum_standardistation.subcategory_label'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_dnssec'},
                                        {name: 'internet_nl_web_legacy_tls_available'},
                                        {name: 'internet_nl_web_legacy_tls_ncsc_web'},
                                        {name: 'internet_nl_web_legacy_https_enforced'},
                                        {name: 'internet_nl_web_legacy_hsts'},
                                        {name: 'internet_nl_web_legacy_ipv6_nameserver'},
                                        {name: 'internet_nl_web_legacy_ipv6_webserver'},
                                        {name: 'internet_nl_web_legacy_dane'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        }
                    ]
                },
                {
                    name: 'mail',
                    fields: [],
                    additional_fields: [
                        {name: 'internet_nl_mail_server_configured'},
                    ],

                    label: internet_nl_messages[language].internet_nl.base_test_mail_label,
                    categories: [
                        {
                            name: 'IPv6',
                            label: internet_nl_messages[language].internet_nl.test_mailipv6_label,
                            key: 'internet_nl_mail_dashboard_ipv6',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_ipv6'}
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'Name servers',
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_ipv6_name_servers_label,
                                    fields: [
                                        {name: 'internet_nl_mail_ipv6_ns_address'},
                                        {name: 'internet_nl_mail_ipv6_ns_reach'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'Mail server(s)',
                                    label: internet_nl_messages[language].internet_nl.results_mail_ipv6_mail_servers_label,
                                    fields: [
                                        {name: 'internet_nl_mail_ipv6_mx_address'},
                                        {name: 'internet_nl_mail_ipv6_mx_reach'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        },
                        {
                            name: 'DNSSEC',
                            label: internet_nl_messages[language].internet_nl.test_maildnssec_label,
                            key: 'internet_nl_mail_dashboard_dnssec',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_dnssec',}
                            ],
                            additional_fields: [],
                            categories: [
                                {
                                    name: 'email address domain',
                                    label: internet_nl_messages[language].internet_nl.results_mail_dnssec_domain_label,
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mailto_exist'},
                                        {name: 'internet_nl_mail_dnssec_mailto_valid'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'mail server domain(s)',
                                    label: internet_nl_messages[language].internet_nl.results_mail_dnssec_mail_servers_label,
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mx_exist'},
                                        {name: 'internet_nl_mail_dnssec_mx_valid'},
                                    ],
                                    additional_fields: [],
                                },
                            ]
                        },
                        {
                            name: 'DMARC, DKIM and SPF',
                            label: internet_nl_messages[language].internet_nl.test_mailauth_label,
                            key: 'internet_nl_mail_dashboard_auth',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_auth'}
                            ],
                            additional_fields: [
                                {name: 'internet_nl_mail_non_sending_domain'}
                            ],
                            categories: [
                                {
                                    name: 'DMARC',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_dmarc_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dmarc_exist'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy_only'},
                                        {name: 'internet_nl_mail_auth_dmarc_ext_destination'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'DKIM',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_dkim_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dkim_exist'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'SPF',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_spf_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_spf_exist'},
                                        {name: 'internet_nl_mail_auth_spf_policy'},
                                    ],
                                    additional_fields: [],
                                },
                            ]
                        },
                        {
                            name: 'STARTTLS and DANE',
                            label: internet_nl_messages[language].internet_nl.test_mailtls_label,
                            key: 'internet_nl_mail_dashboard_tls',
                            fields: [
                                {name: 'internet_nl_mail_dashboard_tls'},
                            ],
                            additional_fields: [
                                {name: 'internet_nl_mail_servers_testable'},
                            ],
                            categories: [
                                {
                                    name: 'TLS',
                                    label: internet_nl_messages[language].internet_nl.results_mail_tls_starttls_label,
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_tls_available'},
                                        {name: 'internet_nl_mail_starttls_tls_version'},
                                        {name: 'internet_nl_mail_starttls_tls_ciphers'},
                                        {name: 'internet_nl_mail_starttls_tls_keyexchange'},
                                        {name: 'internet_nl_mail_starttls_tls_compress'},
                                        {name: 'internet_nl_mail_starttls_tls_secreneg'},
                                        {name: 'internet_nl_mail_starttls_tls_clientreneg'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'Certificate',
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_tls_certificate_label,
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_cert_chain'},
                                        {name: 'internet_nl_mail_starttls_cert_pubkey'},
                                        {name: 'internet_nl_mail_starttls_cert_sig'},
                                        {name: 'internet_nl_mail_starttls_cert_domain'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'DANE',
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_tls_dane_label,
                                    fields: [
                                        {name: 'internet_nl_mail_starttls_dane_exist'},
                                        {name: 'internet_nl_mail_starttls_dane_valid'},
                                        {name: 'internet_nl_mail_starttls_dane_rollover'},
                                    ],
                                    additional_fields: [
                                        {name: 'internet_nl_mail_starttls_dane_ta'}
                                    ],
                                },
                            ]
                        },
                        {
                            name: 'forum_standardisation',
                            label: i18n.t('report.fields.forum_standardistation.category_label'),
                            key: 'mail_legacy',
                            fields: [
                                {
                                    name: 'mail_legacy',
                                },
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'magazine',
                                    label: i18n.t('report.fields.forum_standardistation.subcategory_label'),
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_dmarc'},
                                        {name: 'internet_nl_mail_legacy_dkim'},
                                        {name: 'internet_nl_mail_legacy_spf'},
                                        {name: 'internet_nl_mail_legacy_dmarc_policy'},
                                        {name: 'internet_nl_mail_legacy_spf_policy'},
                                        {name: 'internet_nl_mail_legacy_start_tls'},
                                        {name: 'internet_nl_mail_legacy_start_tls_ncsc'},
                                        {name: 'internet_nl_mail_legacy_dnssec_email_domain'},
                                        {name: 'internet_nl_mail_legacy_dnssec_mx'},
                                        {name: 'internet_nl_mail_legacy_dane'},
                                        {name: 'internet_nl_mail_legacy_ipv6_nameserver'},
                                        {name: 'internet_nl_mail_legacy_ipv6_mailserver'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        }
                    ]
                }
            ];
        },

        relevant_categories_based_on_settings: function(){
            let preferred_fields = [];  // this.categories[this.selected_category];

            console.log(`Selected category: ${this.selected_category}`);

            this.scan_methods.forEach((scan_method) => {
                console.log("scan_method " + scan_method.name);
                if (['web', 'mail'].includes(scan_method.name) && scan_method.name === this.selected_category){

                    scan_method.categories.forEach((category) => {

                        category.fields.forEach((field) => {
                            preferred_fields.push(field.name);
                        });
                        category.additional_fields.forEach((field) => {
                            preferred_fields.push(field.name);
                        });

                    });

                } else {
                    // subcategories, dirty fix using the 'key' field to save a lot of iteration.
                    scan_method.categories.forEach((category) => {
                        console.log("category " + category.name);
                        // Get the fields of the highest level
                        if (category.key === this.selected_category) {
                            category.categories.forEach((subcategory) => {
                                subcategory.fields.forEach((field) => {
                                    preferred_fields.push(field.name);
                                });
                                subcategory.additional_fields.forEach((field) => {
                                    preferred_fields.push(field.name);
                                });
                            });
                        }
                    });
                }
            });

            console.log(`Preferred fields: ${preferred_fields}`);

            // now determine for each field if they should be visible or not. Perhaps this should be in
            // the new_categories
            let returned_fields = [];
            for(let i = 0; i<preferred_fields.length; i++){

                if(this.issue_filters[preferred_fields[i]].visible)
                    returned_fields.push(preferred_fields[i])
            }
            return returned_fields;
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


Vue.component('cumulative-percentage-bar-chart', {
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
                        display: false,
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

            let cumulative_axis_data = {};

            for(let i=0; i < this.chart_data.length; i++) {

                let data = this.chart_data[i].statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    this.chart.data.axis_names = [];
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        if (!Object.keys(cumulative_axis_data).includes(ax)) {
                            cumulative_axis_data[ax] = 0
                        }
                        cumulative_axis_data[ax] += data[ax].pct_ok
                    }
                });

            }

            let data = this.chart_data[0].statistics_per_issue_type;
            let axis_names = [];
            let labels = [];
            let chartdata = [];

            this.axis.forEach((ax) => {
                if (ax in data) {
                    labels.push(i18n.t("report." + ax));
                    axis_names.push(ax);

                    // toFixed delivers some 81.32429999999999 results, which is total nonsense.
                    chartdata.push((Math.round(cumulative_axis_data[ax] * 100) / this.chart_data.length) / 100);
                }
            });

            this.chart.data.axis_names = axis_names;
            this.chart.data.labels = labels;
            this.chart.data.datasets.push({
                data: chartdata,
                backgroundColor: this.color_scheme.incremental[0].background,
                borderColor: this.color_scheme.incremental[0].border,
                borderWidth: 1,
                lineTension: 0,
                label: `${this.chart_data[0].calculation.name} ${moment(this.chart_data[0].at_when).format('LL')}`,
            });



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
