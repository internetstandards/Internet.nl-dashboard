{% verbatim %}
<template type="x-template" id="report_template">
    <div style="width: 100%; min-height: 500px;">
        <div class="block fullwidth">
            <h1>{{ $t("report.header.title") }}</h1>
            <p>{{ $t("report.header.intro") }}</p>

            <!--
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
            -->
            <div aria-live="polite" style="margin-bottom: 30px;">
                <v-select
                        v-model="selected_report"
                        :options="filtered_recent_reports"
                        label="label"
                        :multiple="true"
                >
                    <slot name="no-options">{{ $t('report.header.no_options') }}</slot>

                </v-select>
            </div>

            <template v-if="reports.length && !is_loading">

                <div class="testresult faq-report">
                    <h2 style="font-size: 1.0em;"  class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("report.icon_legend.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <h3>{{ $t("report.icon_legend.test_title") }}</h3>
                        <ul>
                            <li><span class="faq-test category_passed"><span class="visuallyhidden">{{ $t("report.report.results.passed") }}</span>{{ $t("report.icon_legend.test_good") }}</span></li>
                            <li><span class="faq-test category_failed"><span class="visuallyhidden">{{ $t("report.report.results.failed") }}</span>{{ $t("report.icon_legend.test_bad") }}</span></li>
                            <li><span class="faq-test category_warning"><span class="visuallyhidden">{{ $t("report.report.results.warning") }}</span>{{ $t("report.icon_legend.test_warning") }}</span></li>
                        </ul>
                        <h3>{{ $t("report.icon_legend.subtest_title") }}</h3>
                        <ul>
                            <li><span class="faq-subtest passed"><span class="visuallyhidden">{{ $t("report.report.results.passed") }}</span>{{ $t("report.icon_legend.subtest_good") }}</span></li>
                            <li><span class="faq-subtest failed"><span class="visuallyhidden">{{ $t("report.report.results.failed") }}</span>{{ $t("report.icon_legend.subtest_bad") }}</span></li>
                            <li><span class="faq-subtest warning"><span class="visuallyhidden">{{ $t("report.report.results.warning") }}</span>{{ $t("report.icon_legend.subtest_warning") }}</span></li>
                            <li><span class="faq-subtest info"><span class="visuallyhidden">{{ $t("report.report.results.info") }}</span>{{ $t("report.icon_legend.subtest_info") }}</span></li>
                            <li><span class="faq-test not_applicable"><span class="visuallyhidden">{{ $t("report.report.results.not_applicable") }}</span>{{ $t("report.icon_legend.subtest_not_applicable") }}</span></li>
                            <li><span class="faq-test not_testable"><span class="visuallyhidden">{{ $t("report.report.results.not_testable") }}</span>{{ $t("report.icon_legend.subtest_not_testable") }}</span></li>
                        </ul>
                    </div>
                </div>

                <div class="testresult">
                    <h2 style="font-size: 1.0em;" class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("report.download.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <p>{{ $t("report.download.intro") }}</p>
                        <ul style="list-style: disc !important;">
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/xlsx/'">{{ $t("report.download.xlsx") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/ods/'">{{ $t("report.download.ods") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/csv/'">{{ $t("report.download.csv") }}</a></li>
                        </ul>
                    </div>
                </div>

                <div class="testresult">
                    <h2 style="font-size: 1.0em;" class="panel-title" >
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
                            <button @click="reset_issue_filters()">{{ $t("report.settings.buttons.reset") }}<span class="visuallyhidden"></span></button>
                            <button @click="save_issue_filters()">{{ $t("report.settings.buttons.save") }}<span class="visuallyhidden"></span></button>
                            <br>
                            <template v-if="issue_filters_response.success || issue_filters_response.error">
                                <div :class="'server-response-' + issue_filters_response.state">
                                    <span aria-live="assertive">{{ $t(issue_filters_response.message) }} on {{ humanize_date(issue_filters_response.timestamp) }}.</span>
                                </div>
                            </template>
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
                                                <template v-if="field.explanation">
                                                    <p>{{ $t("report." + field.name + "_explanation") }}</p>
                                                </template>
                                            </div>

                                            <template v-if="category.additional_fields.length">
                                                <div class="test-subsection">{{ $t("report.fields.additional_fields.label") }}</div>
                                                <div v-for="field in category.additional_fields" class="testresult">
                                                    <label :for="field.name + '_visible'">
                                                        <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                        {{ $t("report." + field.name) }}
                                                    </label>
                                                    <template v-if="field.explanation">
                                                        <p>{{ $t("report." + field.name + "_explanation") }}</p>
                                                    </template>
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

                <div style="overflow: auto; width: 100%">
                    <div class="chart-container" style="position: relative; height:300px; width:100%; min-width: 950px;">
                        <line-chart
                                :color_scheme="color_scheme"
                                :translation_key="'report.charts.adoption_timeline'"
                                :chart_data="issue_timeline_of_related_urllist"
                                :accessibility_text="$t('report.charts.adoption_timeline.accessibility_text')"
                                :axis="['average_internet_nl_score']">
                        </line-chart>

                        <div style="overflow-x: scroll; overflow-y: hidden;">
                            <table class="table table-striped">
                                <caption>{{ $t("report.charts.adoption_timeline.title") }}</caption>
                                <thead>
                                    <tr>
                                        <th style="width: 200px;">
                                            &nbsp;{{ $t("report.charts.adoption_timeline.xAxis_label") }}
                                        </th>
                                        <th>
                                             {{ $t("report.charts.adoption_timeline.yAxis_label") }}
                                        </th>
                                    </tr>
                                </thead>

                                <tbody class="gridtable">
                                    <tr v-for="stat in issue_timeline_of_related_urllist">
                                        <td>
                                            {{ humanize_date_date_only(stat.date) }}
                                        </td>
                                        <td>
                                            {{ stat.average_internet_nl_score }}%
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>


                    </div>
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

                        <div style="overflow: auto; width: 100%" v-if="fields_from_categories(scan_form).length">
                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                <percentage-bar-chart
                                        :title="graph_bar_chart_title"
                                        :translation_key="'report.charts.adoption_bar_chart'"
                                        :color_scheme="color_scheme"
                                        :chart_data="compare_charts"
                                        :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                        @bar_click="select_category"
                                        :show_dynamic_average="true"
                                        :only_show_dynamic_average="false"
                                        :axis="fields_from_categories(scan_form)">
                                </percentage-bar-chart>
                            </div>
                        </div>


                        <template v-for="category in scan_form.categories">
                            <template v-if="is_visible(category.key)">
                                <div class="testresult" v-if="fields_from_categories(category).length">
                                    <h3 class="panel-title">
                                        <a href="" aria-expanded="false">
                                            <span class="visuallyhidden">-:</span>
                                            {{ category.label }}
                                            <span class="pre-icon visuallyhidden"></span>
                                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                        </a>
                                    </h3>
                                    <div class="panel-content">
                                        <div style="overflow: auto; width: 100%">
                                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                <percentage-bar-chart
                                                        :title="graph_bar_chart_title"
                                                        :translation_key="'report.charts.adoption_bar_chart'"
                                                        :color_scheme="color_scheme"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                                        @bar_click="select_category"
                                                        :show_dynamic_average="true"
                                                        :only_show_dynamic_average="false"
                                                        :axis="fields_from_categories(category)">
                                                </percentage-bar-chart>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <template v-for="subcategory in category.categories">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div class="testresult" v-if="fields_from_self(subcategory)">
                                        <h4 class="panel-title">
                                            <a href="" aria-expanded="false">
                                                <span class="visuallyhidden">-:</span>
                                                {{ subcategory.label }}
                                                <span class="pre-icon visuallyhidden"></span>
                                                <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                            </a>
                                        </h4>
                                        <div class="panel-content">
                                            <div style="overflow: auto; width: 100%">
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <percentage-bar-chart
                                                            :title="graph_bar_chart_title"
                                                            :translation_key="'report.charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="true"
                                                            :only_show_dynamic_average="false"
                                                            :axis="fields_from_self(subcategory)">
                                                    </percentage-bar-chart>
                                                </div>
                                            </div>
                                            <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                            <div style="overflow: auto; width: 100%" v-if="subcategory.name === 'magazine'">
                                                <p>This shows the average for Forum Standardisation, it is not possible to
                                                show the average or to select what fields should be visible.</p>
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <percentage-bar-chart
                                                            :title="graph_bar_chart_title"
                                                            :translation_key="'report.charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="true"
                                                            :only_show_dynamic_average="true"
                                                            :axis="fields_from_self_and_do_not_filter(subcategory)">
                                                    </percentage-bar-chart>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </template>

                            </template>
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

                        <div style="overflow: auto; width: 100%" v-if="fields_from_categories(scan_form).length">
                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                <cumulative-percentage-bar-chart
                                        :title="$t('report.charts.cumulative_adoption_bar_chart.title', {
                                                        'number_of_reports': compare_charts.length})"
                                        :translation_key="'report.charts.adoption_bar_chart'"
                                        :color_scheme="color_scheme"
                                        :chart_data="compare_charts"
                                        :accessibility_text="$t('report.charts.cumulative_adoption_bar_chart.accessibility_text')"
                                        @bar_click="select_category"
                                        :show_dynamic_average="true"
                                        :only_show_dynamic_average="false"
                                        :axis="fields_from_categories(scan_form)">
                                </cumulative-percentage-bar-chart>
                            </div>
                        </div>

                        <template v-for="category in scan_form.categories">
                            <template v-if="is_visible(category.key)">
                                <div class="testresult" v-if="fields_from_categories(category).length">
                                    <h3 class="panel-title">
                                        <a href="" aria-expanded="false">
                                            <span class="visuallyhidden">-:</span>
                                            {{ category.label }}
                                            <span class="pre-icon visuallyhidden"></span>
                                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                        </a>
                                    </h3>
                                    <div class="panel-content">
                                        <div style="overflow: auto; width: 100%">
                                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                <cumulative-percentage-bar-chart
                                                        :title="$t('report.charts.cumulative_adoption_bar_chart.title', {
                                                            'number_of_reports': compare_charts.length})"
                                                        :translation_key="'report.charts.adoption_bar_chart'"
                                                        :color_scheme="color_scheme"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('report.charts.cumulative_adoption_bar_chart.accessibility_text')"
                                                        @bar_click="select_category"
                                                        :show_dynamic_average="true"
                                                        :only_show_dynamic_average="false"
                                                        :axis="fields_from_categories(category)">
                                                </cumulative-percentage-bar-chart>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <template v-for="subcategory in category.categories">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div class="testresult" v-if="fields_from_self(subcategory).length">
                                        <h4 class="panel-title">
                                            <a href="" aria-expanded="false">
                                                <span class="visuallyhidden">-:</span>
                                                {{ subcategory.label }}
                                                <span class="pre-icon visuallyhidden"></span>
                                                <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                            </a>
                                        </h4>
                                        <div class="panel-content">
                                            <div style="overflow: auto; width: 100%">
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <cumulative-percentage-bar-chart
                                                            :title="graph_bar_chart_title"
                                                            :translation_key="'report.charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="true"
                                                            :only_show_dynamic_average="false"
                                                            :axis="fields_from_self(subcategory)">
                                                    </cumulative-percentage-bar-chart>
                                                </div>
                                            </div>
                                            <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                            <div style="overflow: auto; width: 100%" v-if="subcategory.name === 'magazine'">
                                                <p>This shows the average for Forum Standardisation, it is not possible to
                                                show the average or to select what fields should be visible.</p>
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <cumulative-percentage-bar-chart
                                                            :title="graph_bar_chart_title"
                                                            :translation_key="'report.charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('report.charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="true"
                                                            :only_show_dynamic_average="true"
                                                            :axis="fields_from_self_and_do_not_filter(subcategory)">
                                                    </cumulative-percentage-bar-chart>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </template>


                            </template>
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
                                <tr class="summaryrow">
                                    <td>
                                        &nbsp;
                                    </td>
                                    <td v-for="category_name in relevant_categories_based_on_settings">
                                        <span v-if="category_name in reports[0].statistics_per_issue_type">
                                            {{reports[0].statistics_per_issue_type[category_name].pct_ok}}%</span>
                                    </td>
                                </tr>

                                <!-- Zoom buttons for accessibility -->
                                <tr class="summaryrow">
                                    <td>
                                        <label class="visuallyhidden" for="url_filter">{{ $t('report.report.url_filter') }}</label>
                                        <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.report.url_filter')">
                                        <p class="visuallyhidden">{{ $t('report.report.zoom.explanation') }}</p>
                                    </td>
                                    <template v-if="['web', 'mail'].includes(selected_category)">
                                        <td v-for="category_name in relevant_categories_based_on_settings">
                                            <button @click="select_category(category_name)">{{ $t("report.report.zoom.buttons.zoom") }}
                                            <span class="visuallyhidden">{{ $t("report.report.zoom.buttons.zoom_in_on", [$t("report." + category_name)]) }}</span>
                                            </button>
                                        </td>
                                    </template>
                                    <template v-if="!['web', 'mail'].includes(selected_category)">
                                        <td :colspan="relevant_categories_based_on_settings.length" style="text-align: center">
                                        {{ $t("report.report.zoom.zoomed_in_on") }} {{ $t("report." + selected_category) }}.
                                            <button @click="select_category(selected_report.urllist_scan_type)">
                                                <span role="img" :aria-label="$t('icons.remove_filter')">❌</span> {{ $t("report.report.zoom.buttons.remove_zoom") }}
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
                                        <span v-if="selected_report[0].type === 'web'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation, url.url)"></span>
                                        <span v-if="selected_report[0].type === 'mail'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation, url.url)"></span>
                                    </td>
                                    <td class="testresultcell" v-for="category_name in relevant_categories_based_on_settings">
                                        <template v-if="['web', 'mail'].includes(selected_category)">
                                            <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                                <!-- Currently the API just says True or False, we might be able to deduce the right label for a category, but that will take a day or two.
                                                At the next field update, we'll also make the categories follow the new format of requirement level and testresult so HTTP Security Headers
                                                 here is shown as optional, or info if failed. We can also add a field for baseline NL government then. -->
                                                <template v-if="url.endpoints[0].ratings_by_type[category_name].ok < 1">
                                                    <span v-if="category_name !== 'internet_nl_web_appsecpriv'" class="category_failed">
                                                        {{ $t('report.' + category_name + '_verdict_bad') }}
                                                    </span>
                                                    <span v-if="category_name === 'internet_nl_web_appsecpriv'" class="category_warning">
                                                        {{ $t('report.' + category_name + '_verdict_bad') }}
                                                    </span>
                                                </template>
                                                <span class="category_passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0">
                                                    {{ $t('report.' + category_name + '_verdict_good') }}
                                                </span>
                                            </template>
                                            <span class="" v-if="url.endpoints[0].ratings_by_type[category_name] === undefined">
                                                {{ $t("report.report.results.unknown") }}
                                            </span>
                                        </template>
                                        <template v-if="!['web', 'mail'].includes(selected_category)">

                                            <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                                <span class="not_applicable" v-if="url.endpoints[0].ratings_by_type[category_name].not_applicable > 0">
                                                    {{ $t("report.report.results.not_applicable") }}
                                                </span>
                                                <span class="not_testable" v-if="url.endpoints[0].ratings_by_type[category_name].not_testable > 0">
                                                    {{ $t("report.report.results.not_testable") }}
                                                </span>
                                                <span class="failed" v-if="url.endpoints[0].ratings_by_type[category_name].high > 0">
                                                    {{ $t("report.report.results.failed") }} {{ $t('report.' + category_name + '_verdict_bad') }}
                                                </span>
                                                <span class="warning" v-if="url.endpoints[0].ratings_by_type[category_name].medium > 0">
                                                    {{ $t("report.report.results.warning") }} {{ $t('report.' + category_name + '_verdict_bad') }}
                                                </span>
                                                <span class="info" v-if="url.endpoints[0].ratings_by_type[category_name].low > 0">
                                                    {{ $t("report.report.results.info") }} {{ $t('report.' + category_name + '_verdict_bad') }}
                                                </span>
                                                <span class="passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0
                                                && !url.endpoints[0].ratings_by_type[category_name].not_applicable
                                                && !url.endpoints[0].ratings_by_type[category_name].not_testable">
                                                    {{ $t("report.report.results.passed") }} {{ $t('report.' + category_name + '_verdict_good') }}
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
            'web_legacy': {'visible': false},
            'mail': {'visible': true},
            'mail_legacy': {'visible': false},
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

            'internet_nl_mail_legacy_dmarc': {'visible': false},
            'internet_nl_mail_legacy_dkim': {'visible': false},
            'internet_nl_mail_legacy_spf': {'visible': false},
            'internet_nl_mail_legacy_dmarc_policy': {'visible': false},
            'internet_nl_mail_legacy_spf_policy': {'visible': false},
            'internet_nl_mail_legacy_start_tls': {'visible': false},
            'internet_nl_mail_legacy_start_tls_ncsc': {'visible': false},
            'internet_nl_mail_legacy_dnssec_email_domain': {'visible': false},
            'internet_nl_mail_legacy_dnssec_mx': {'visible': false},
            'internet_nl_mail_legacy_dane': {'visible': false},
            'internet_nl_mail_legacy_ipv6_nameserver': {'visible': false},
            'internet_nl_mail_legacy_ipv6_mailserver': {'visible': false},

            'internet_nl_web_legacy_dnssec': {'visible': false},
            'internet_nl_web_legacy_tls_available': {'visible': false},
            'internet_nl_web_legacy_tls_ncsc_web': {'visible': false},
            'internet_nl_web_legacy_https_enforced': {'visible': false},
            'internet_nl_web_legacy_hsts': {'visible': false},
            'internet_nl_web_legacy_ipv6_nameserver': {'visible': false},
            'internet_nl_web_legacy_ipv6_webserver': {'visible': false},
            'internet_nl_web_legacy_dane': {'visible': false},

            // Fields added on the 24th of May 2019
            'internet_nl_mail_auth_dmarc_policy_only': {'visible': false},  // Added 24th of May 2019
            'internet_nl_mail_auth_dmarc_ext_destination': {'visible': false},  // Added 24th of May 2019

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

        issue_filters_response: {},

        // url_filter allows the filtering of names in the list of urls.
        url_filter: '',

        selected_category: '',

        // such basic functionality missing in vue, it even got removed.
        debounce_timer: 0,

        available_recent_reports: [],

        // the filtered set only shows the same type as the first scan shown. It's not possible to open
        // two reports of the same type, as the UI is not capable ofhandling that ... as all fields differ and there
        // is really no comparison possible.
        filtered_recent_reports: [],

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
            'ok_border': 'rgba(209, 63, 0, 1)',
            'addresses_background': 'rgba(0, 0, 0, 0.2)',
            'addresses_border': 'rgba(0,0,0,1)',
            'services_background': 'rgba(0, 40, 255, 0.2)',
            'services_border': 'rgba(0,40,255,1)',

            // https://github.com/ashiguruma/patternomaly/blob/master/assets/pattern-list.png
            // The first one can be defined without a pattern to give a consistent look/feel to all first graphs.
            incremental: [
                {background: 'rgba(255, 112, 50, 0.6)', border: 'rgba(209, 63, 0, 1)'},
                {background: pattern.draw('weave',  'rgba(21, 66, 115, 0.6)'), border: 'rgba(21, 66, 115, 1)'},
                {background: pattern.draw('dot',  'rgba(43, 151, 89, 0.6)'), border: 'rgb(28, 94, 56)'},
                {background: pattern.draw('dash',  'rgba(0, 255, 246, 0.6)'), border: 'rgb(0, 92, 89)'},
                {background: pattern.draw('ring',  'rgba(255, 0, 246, 0.6)'), border: 'rgb(158, 0, 153)'},
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

                // we already have the first report, so don't request it again.
                // note that when setting the first chart, the subsequent updates do not "point ot a new object"
                // so a state change doesn not happen automatically using a wathcer, you have to watch deep.
                console.log(`First compare chart set...`);
                this.$set(this.compare_charts, 0, this.reports[0]);
                // this.compare_charts.$set(0, );

                // new accordions are created, reduce their size.
                this.$nextTick(() => {accordinate(); this.$forceUpdate()});
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
                    this.issue_filters_response = server_response;
                }
            );
        },
        reset_issue_filters: function(){
            fetch(`/data/account/report_settings/get/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                if (!jQuery.isEmptyObject(data)) {
                    this.issue_filters = data.data;
                    this.issue_filters_response = data;
                }
            });
            this.load_issue_filters();

        },
        load_issue_filters: function(){
            fetch(`/data/account/report_settings/get/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                if (!jQuery.isEmptyObject(data.data)) {
                    this.issue_filters = data.data;

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
        compare_with: function(id, compare_chart_id){
            fetch(`/data/report/get/${id}/`, {credentials: 'include'}).then(response => response.json()).then(report => {

                if (!jQuery.isEmptyObject(report)) {
                    // this will work fine, as all the prior id's will be filled with reports too...
                    // js behaves unacceptably, but in this case it's fine.
                    // example: i = [];
                    // i[3] = "a"
                    // i is then Array(4) [ undefined, undefined, undefined, "a" ]...
                    // https://vuejs.org/2016/02/06/common-gotchas/#Why-isn%E2%80%99t-the-DOM-updating
                    // note that the documentation is plain wrong, as arr.$set is NOT a method on the array,
                    // but on the vm. And thus the syntax for using it differs from the docs.
                    console.log(`Compare chart ${compare_chart_id} set...`);
                    this.$set(this.compare_charts, compare_chart_id, report[0]);

                    // given the charts are on a fixed number in the array, vue doesn't pick up changes.
                    // and as the order matters, this is a solution that fixes that.
                    this.$nextTick(() => {accordinate(); this.$forceUpdate();});
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
                this.filtered_recent_reports = options;

                // if the page was requested with a page ID, start loading that report.
                // this supports: http://localhost:8000/reports/83/
                if (window.location.href.split('/').length > 3) {
                    get_id = window.location.href.split('/')[4];
                    // can we change the select2 to a certain value?

                    this.filtered_recent_reports.forEach((option) => {
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
        original_report_link_from_score: function(score, url){
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

            return `<a class='direct_link_to_report' href='${sc[1]}' target="_blank">
                        <img src="/static/images/vendor/internet_nl/favicon.png" style="height: 16px;" alt="${i18n.t('report.report.link_to_report', {'url': url})}"> ${sc[0]}%
                        <span class="visuallyhidden">${i18n.t('report.report.link_to_report', {'url': url})}</span>
                    </a>`
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
        fields_from_self(category){
            let fields = [];

            category.fields.forEach((field) => {
                fields.push(field.name);
            });
            category.additional_fields.forEach((field) => {
                fields.push(field.name);
            });

            let returned_fields = [];
            for(let i = 0; i<fields.length; i++){

                if(this.issue_filters[fields[i]].visible)
                    returned_fields.push(fields[i])
            }
            return returned_fields;
        },
        fields_from_self_and_do_not_filter(category){
            let fields = [];

            category.fields.forEach((field) => {
                fields.push(field.name);
            });
            category.additional_fields.forEach((field) => {
                fields.push(field.name);
            });
            return fields;
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

                // all reports are available again:
                this.filtered_recent_reports = this.available_recent_reports;

                this.reports=[];
                this.is_loading = false;
                return;
            }

            // when deleting any report, we will need to rebuild the compare charts...
            this.compare_charts = [];
            this.load(new_value[0].id);

            // filter reports on type:
            let filtered_reports = [];
            this.available_recent_reports.forEach((item) => {
                if (item.type === new_value[0].type){
                    filtered_reports.push(item);
                }
            });
            this.filtered_recent_reports = filtered_reports;

            // we already have the first chart, don't load that again.
            // the first chart is always loaded through the load method.
            for(let i=1; i<new_value.length; i++){
                // console.log(`Comparing with report ${new_value[i].id}`);
                // todo: this causes an extra load of the data, which is slow... At least it always works
                // without syncing issues etc...
                // i = the compare chart id, so even if the reports load asyncronous, the array order is
                // maintained in the compare charts, and thus in the graphs.
                this.compare_with(new_value[i].id, i);
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
                                    label: internet_nl_messages[language].internet_nl.test_sitednssec_label,
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
                                    name: 'Measurements on agreed security standards',
                                    label: i18n.t('report.fields.forum_standardistation.measurements_on_agreed_security_standards'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_dnssec',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_dnssec_explanation'},
                                        {name: 'internet_nl_web_legacy_tls_available',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_tls_available_explanation'},
                                        {name: 'internet_nl_web_legacy_tls_ncsc_web',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_tls_ncsc_web_explanation'},
                                        {name: 'internet_nl_web_legacy_https_enforced',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_https_enforced_explanation'},
                                        {name: 'internet_nl_web_legacy_hsts',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_hsts_explanation'},
                                        // {name: 'internet_nl_web_legacy_dane'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'IPv6 Monitor',
                                    label: i18n.t('report.fields.forum_standardistation.ipv6_monitor'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_ipv6_nameserver',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_web_legacy_ipv6_webserver',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_web_legacy_ipv6_webserver_explanation'},
                                        // {name: 'internet_nl_web_legacy_dane'},
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
                                    additional_fields: [
                                        {name: 'internet_nl_mail_server_configured'},
                                    ],
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

                            ],
                            categories: [
                                {
                                    name: 'DMARC',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_dmarc_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dmarc_exist'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy'},
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
                                    additional_fields: [
                                        {name: 'internet_nl_mail_non_sending_domain'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy_only'},
                                        {name: 'internet_nl_mail_auth_dmarc_ext_destination'},
                                    ],
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
                                        {name: 'internet_nl_mail_starttls_dane_ta'},
                                        {name: 'internet_nl_mail_servers_testable'},
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
                                    label: 'Measurements on agreed security standards',
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_dmarc',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_dmarc_explanation'},
                                        {name: 'internet_nl_mail_legacy_dkim',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_dkim_explanation'},
                                        {name: 'internet_nl_mail_legacy_spf',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_spf_explanation'},
                                        {name: 'internet_nl_mail_legacy_dmarc_policy',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_dmarc_policy_explanation'},
                                        {name: 'internet_nl_mail_legacy_spf_policy',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_spf_policy_explanation'},
                                        {name: 'internet_nl_mail_legacy_start_tls',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_start_tls_explanation'},
                                        {name: 'internet_nl_mail_legacy_start_tls_ncsc',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_start_tls_ncsc_explanation'},
                                        // {name: 'internet_nl_mail_legacy_dnssec_email_domain'},
                                        {name: 'internet_nl_mail_legacy_dnssec_mx',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_dnssec_mx_explanation'},
                                        {name: 'internet_nl_mail_legacy_dane',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_dane_explanation'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'IPv6 Monitor',
                                    // todo: translate label
                                    label: 'IPv6 Monitor',
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_ipv6_nameserver',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_mail_legacy_ipv6_mailserver',
                                        explanation: 'report.fields.forum_standardistation.internet_nl_mail_legacy_ipv6_mailserver_explanation'},
                                        // {name: 'internet_nl_mail_legacy_ipv6_mailserver'},
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
        translation_key: {type: String, required: false},
        accessibility_text: {type: String, required: true},
        show_dynamic_average: {type: Boolean, required: false},
        only_show_dynamic_average: {type: Boolean, required: false},
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
                    "aria-label": this.title
                },
            },
            [
                // Limited to a paragraph only. So give a hint where you can find more data.
                createElement('p', this.accessibility_text),
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
        chart_data: {

            // Note that you don’t need to do so to listen for Array mutations...
            deep: false,
            handler (new_value, old_value){
                console.log(`Chart data updated to ${new_value.length} items...`);
                this.renderData();
            }
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
                            display: 'auto',
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
            console.log("Rendering bar chart.");

            // prevent the grapsh from ever growing (it's called twice at first render)
            this.chart.data.axis_names = [];
            this.chart.data.labels = [];
            this.chart.data.datasets = [];

            for(let i=0; i < this.chart_data.length; i++){
                console.log(`Rendering set ${i}`);

                // it's possible the report data is not yet in, but the item in the array has been made.
                // so well:
                if (this.chart_data[i] === undefined)
                    return;

                let data = this.chart_data[i].statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    console.log('nothing to show, probably because not all reports in compare charts are in...');
                    this.chart.data.axis_names = [];
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                let axis_names = [];
                let labels = [];
                let chartdata = [];
                let average = 0;

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        if (!this.only_show_dynamic_average) {
                            labels.push(i18n.t("report." + ax));
                            axis_names.push(ax);
                            chartdata.push(data[ax].pct_ok);
                        }
                        average += parseFloat(data[ax].pct_ok);
                    }
                });

                // add the average of all these to the report, not as a line, but as an additional bar
                if ((labels.length > 1 && this.show_dynamic_average) || this.only_show_dynamic_average) {
                    chartdata.push(Math.round((average / this.axis.length) * 100) / 100);
                    labels.push(i18n.t(this.translation_key + '.average'));
                    axis_names.push("Average");
                }

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
                            display: 'auto',
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

                // it's possible the report data is not yet in, but the item in the array has been made.
                // so well:
                if (this.chart_data[i] === undefined)
                    return;

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
            let average = 0;

            this.axis.forEach((ax) => {
                if (ax in data) {
                    if (!this.only_show_dynamic_average) {
                        labels.push(i18n.t("report." + ax));
                        axis_names.push(ax);
                        chartdata.push((Math.round(cumulative_axis_data[ax] / this.chart_data.length * 100)) / 100);
                    }
                    // toFixed delivers some 81.32429999999999 results, which is total nonsense.
                    average += (Math.round(cumulative_axis_data[ax] / this.chart_data.length * 100)) / 100;
                }
            });

            // add the average of all these to the report, not as a line, but as an additional bar
            if ((labels.length > 1 && this.show_dynamic_average) || this.only_show_dynamic_average) {
                chartdata.push(Math.round((average / this.axis.length) * 100) / 100);
                labels.push(i18n.t(this.translation_key + '.average'));
                axis_names.push("Average");
            }

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

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});


// done: place different labels  (add info about date in image)
Vue.component('line-chart', {
    mixins: [chart_mixin],

    methods: {
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
                            display: 'auto',
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
                    layout: {
                        padding: {
                            left: 0,
                            right: 20,
                            top: 0,
                            bottom: 0
                        }
                    },
                    scales: {
                        xAxes: [{
                            barPercentage: 0.9,
                            categoryPercentage: 0.55,

                            display: true,
                            type: 'time',
                            distribution: 'linear',
                            time: {
                                unit: 'month'
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'Month'
                            }
                        }],
                        yAxes: [{
                            display: true,
                            stacked: false,
                            ticks: {
                                padding: 20,
                                min: 0,
                                max: 100,
                                callback: function(label, index, labels) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
								labelString: i18n.t(this.translation_key + '.yAxis_label'),
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
            let average_internet_nl_score = [];

            for(let i=0; i<data.length; i++){
                labels.push(data[i].date);
                high.push(data[i].high);
                medium.push(data[i].medium);
                low.push(data[i].low);
                ok.push(data[i].ok);
                not_ok.push(data[i].not_ok);
                pct_ok.push(data[i].pct_ok);
                pct_not_ok.push(data[i].pct_not_ok);
                average_internet_nl_score.push(data[i].average_internet_nl_score);
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
                    backgroundColor: this.color_scheme.incremental[1].background,
                    borderColor: this.color_scheme.incremental[1].border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('pct_ok')
                },
                {
                    label: i18n.t(this.translation_key + '.average_internet_nl_score'),
                    data: average_internet_nl_score,
                    backgroundColor: this.color_scheme.incremental[0].background,
                    borderColor: this.color_scheme.incremental[0].border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('average_internet_nl_score')
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
