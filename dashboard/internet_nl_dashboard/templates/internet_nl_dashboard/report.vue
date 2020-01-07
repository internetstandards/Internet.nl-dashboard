{% verbatim %}
<style>
    /*
    Todo: sticky columns. (and perhaps fewer data in https? or wider columns?)
    */
    #report-template {
        width: 100%;
        min-height: 500px;
    }

    /* Do print the whole table... */
    @media print {
        #report-template {
            min-height: 100% !important;
        }
    }

    /* Use fixed headers, and search. If you scroll down the headers stay visible. Looks good, even better than aggrid.
    Note that chrome has issues making thead and tr sticky. Therefore it is applied to td and th (because...). */
    #report-template .sticky-table-container {
        max-height: 80vh;
        overflow-x: scroll;
        overflow-y: scroll;
    }

    #report-template th {
        background-color: white;
    }

    #report-template th.sticky-header {
        position: sticky;
        top: 0px;

    }

    #report-template td.sticky_search {
        position: sticky;
        top: 206px;

        /* 100% background is needed to not mix content: this content is on top. */
        background-color: white;
    }

    #report-template tr.result_row {
        /* For testing purposes. */
        /* height: 200px; */
    }


    /* https://css-tricks.com/rotated-table-column-headers/*/
    /* It's not possible to dynamically resize the height of the TH or th container :( */
    div.rotate {
        white-space: nowrap;
        vertical-align: bottom;
        margin-top: 160px;
    }

    div.rotate {
      transform:
        rotate(315deg);
      width: 32px;  /*Fits the 100% value too.*/
    }
    div.rotate > span {
        padding: 5px 10px;
        z-index: 1000;
    }

    /* Why emulate bootstrap? */
    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 1rem;
        background-color: transparent;
    }

    .table-striped tbody tr:nth-of-type(2n+1) {
        background-color: rgba(0,0,0,.05);
    }

    .table td, .table th {
        padding: .75rem;
        vertical-align: top;
        border-top: 1px solid #dee2e6;
    }

    .direct_link_to_report{
        font-size: 0.8em;
    }

    .table .summaryrow {
        font-size: 0.8em;
    }


    #report-template .testresultcell span{
        background-size: 1.125em 1.125em;
        background-repeat: no-repeat;
        /**
        The reason we're not using padding-left 1.5em is that we want the results to be copy-pasteable.
        So there is invisible text on the icon that can be copied.
        */
        width: 20px;
        height: 20px;
        display: block;
        color: transparent;
    }

    #report-template .testresultcell span span {
        font-size: 1px;
    }

    /**
     Sortable Tables
     https://vuejs.org/v2/examples/grid-component.html
    */

    .arrow {
        transform: rotate(-315deg);
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin-left: 5px;
        opacity: 0.66;
        padding: 0px 0px !important;
    }

    .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid #00a0c6;
    }

    .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #00a0c6;
    }

    .arrow.unknown {
        border-left: 4px solid #00a0c6;
        border-right: 4px solid #00a0c6;
        border-top: 4px solid #00a0c6;
    }

    .select-deselect-category {
        font-size: 0.9em;
        display: block;
        width: 100%;
        text-align: right;
        padding-top: 5px;
        padding-bottom: 10px;
    }


    .tabs-component {
      margin: 1em 0;
    }

    .tabs-component-tabs {
      border: solid 1px #ddd;
      border-radius: 6px;
      margin-bottom: 5px;
    }

    @media (min-width: 700px) {
      .tabs-component-tabs {
        border: 0;
        align-items: stretch;
        display: flex;
        justify-content: flex-start;
        margin-bottom: -1px;
      }
    }

    .tabs-component-tab {
      color: #999;
      font-size: 14px;
      font-weight: 600;
      margin-right: 0;
      list-style: none;
    }

    .tabs-component-tab:not(:last-child) {
      border-bottom: dotted 1px #ddd;
    }

    .tabs-component-tab:hover {
      color: #666;
    }

    .tabs-component-tab.is-active {
      color: #000;
    }

    .tabs-component-tab.is-disabled * {
      color: #cdcdcd;
      cursor: not-allowed !important;
    }

    @media (min-width: 700px) {
      .tabs-component-tab {
        background-color: #fff;
        border: solid 1px #ddd;
        border-radius: 3px 3px 0 0;
        margin-right: .5em;
        transform: translateY(2px);
        transition: transform .3s ease;
      }

      .tabs-component-tab.is-active {
        border-bottom: solid 1px #fff;
        z-index: 2;
        transform: translateY(0);
      }
    }

    .tabs-component-tab-a {
      align-items: center;
      color: inherit;
      display: flex;
      padding: .75em 1em;
      text-decoration: none;
    }

    .tabs-component-panels {
      padding: 1em 0;
        margin-top: -22px;
    }

    @media (min-width: 700px) {
      .tabs-component-panels {
        border-top-left-radius: 0;
        background-color: #fff;
        border: solid 1px #ddd;
        border-radius: 0 6px 6px 6px;
        box-shadow: 0 0 10px rgba(0, 0, 0, .05);
        padding: 4em 2em;
          padding-top: 2em;
          padding-bottom: 2em;
          margin-top: -22px;
      }
    }
</style>

<template type="x-template" id="report_template">
    <div id="report-template">
        <div class="block fullwidth">
            <h1>{{ $t("header.title") }}</h1>
            <p>{{ $t("header.intro") }}</p>

            <div aria-live="polite" style="margin-bottom: 30px;">
                <!-- limit not yet supported, nov 2019: https://github.com/sagalbot/vue-select/issues/60 -->
                <v-select
                        v-model="selected_report"
                        :placeholder="$t('header.select_report')"
                        :options="filtered_recent_reports"
                        label="label"
                        :multiple="true"
                >
                    <slot name="no-options">{{ $t('header.no_options') }}</slot>

                </v-select>
            </div>

            <div class="testresult_without_icon faq-report">
                <h2 style="font-size: 1.0em;"  class="panel-title" >
                    <a href="" aria-expanded="false">
                        <span class="visuallyhidden">-:</span>
                        {{ $t("icon_legend.title") }}
                        <span class="pre-icon visuallyhidden"></span>
                        <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                    </a>
                </h2>
                <div class="panel-content">
                    <h3>{{ $t("icon_legend.test_title") }}</h3>
                    <ul>
                        <li><span class="faq-test category_passed"><span class="visuallyhidden">{{ $t("report.results.passed") }}</span>{{ $t("icon_legend.test_good") }}</span></li>
                        <li><span class="faq-test category_failed"><span class="visuallyhidden">{{ $t("report.results.failed") }}</span>{{ $t("icon_legend.test_bad") }}</span></li>
                        <li><span class="faq-test category_warning"><span class="visuallyhidden">{{ $t("report.results.warning") }}</span>{{ $t("icon_legend.test_warning") }}</span></li>
                    </ul>
                    <h3>{{ $t("icon_legend.subtest_title") }}</h3>
                    <ul>
                        <li><span class="faq-subtest passed"><span class="visuallyhidden">{{ $t("report.results.passed") }}</span>{{ $t("icon_legend.subtest_good") }}</span></li>
                        <li><span class="faq-subtest failed"><span class="visuallyhidden">{{ $t("report.results.failed") }}</span>{{ $t("icon_legend.subtest_bad") }}</span></li>
                        <li><span class="faq-subtest warning"><span class="visuallyhidden">{{ $t("report.results.warning") }}</span>{{ $t("icon_legend.subtest_warning") }}</span></li>
                        <li><span class="faq-subtest info"><span class="visuallyhidden">{{ $t("report.results.info") }}</span>{{ $t("icon_legend.subtest_info") }}</span></li>
                        <li><span class="faq-test not_applicable"><span class="visuallyhidden">{{ $t("report.results.not_applicable") }}</span>{{ $t("icon_legend.subtest_not_applicable") }}</span></li>
                        <li><span class="faq-test not_testable"><span class="visuallyhidden">{{ $t("report.results.not_testable") }}</span>{{ $t("icon_legend.subtest_not_testable") }}</span></li>
                    </ul>
                </div>
            </div>

            <template v-if="reports.length && !is_loading">

                <div class="testresult_without_icon">
                    <h2 style="font-size: 1.0em;" class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("download.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <p>{{ $t("download.intro") }}</p>
                        <ul style="list-style: disc !important; padding-left: 20px">
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/xlsx/'">{{ $t("download.xlsx") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/ods/'">{{ $t("download.ods") }}</a></li>
                            <li><a :href="'/data/download-spreadsheet/' + reports[0].id + '/csv/'">{{ $t("download.csv") }}</a></li>
                        </ul>
                    </div>
                </div>

                <div class="testresult_without_icon">
                    <h2 style="font-size: 1.0em;" class="panel-title" >
                        <a href="" aria-expanded="false">
                            <span class="visuallyhidden">-:</span>
                            {{ $t("settings.title") }}
                            <span class="pre-icon visuallyhidden"></span>
                            <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                        </a>
                    </h2>
                    <div class="panel-content">
                        <p>{{ $t("settings.intro") }}</p>
                        <template v-for="scan_form in scan_methods">
                            <template v-if="scan_form.name === selected_report[0].type">

                                <tabs :options="{ useUrlFragment: false }">
                                    <tab :name="$t('chart_info.adoption_bar_chart.annotation.title')">
                                        <h3>{{ $t("chart_info.adoption_bar_chart.annotation.title") }}</h3>
                                        <br>
                                        <p>
                                            <label :for="scan_form.name + '_show_dynamic_average'">
                                                <input type="checkbox" v-model="issue_filters[scan_form.name].show_dynamic_average" :id="scan_form.name + '_show_dynamic_average'">
                                                {{ $t("settings.show_dynamic_average") }}
                                            </label><br>
                                            <!-- disabled as per #107
                                            <label :for="scan_form.name + '_only_show_dynamic_average'">
                                                <input type="checkbox"
                                                       v-model="issue_filters[scan_form.name].only_show_dynamic_average"
                                                       :id="scan_form.name + '_only_show_dynamic_average'"
                                                        :disabled="!issue_filters[scan_form.name].show_dynamic_average">
                                                {{ $t("settings.only_show_dynamic_average") }}
                                            </label>
                                            -->

                                            <template v-if="scan_form.additional_fields.length">
                                                <div class="test-subsection">{{ $t("fields.additional_fields.label") }}</div>
                                                <div v-for="field in scan_form.additional_fields" class="testresult_without_icon">
                                                <label :for="field.name + '_visible'">
                                                    <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                    {{ $t(field.name) }}
                                                </label>
                                                </div>
                                            </template>
                                        </p>

                                        <div>
                                                <button @click="reset_issue_filters()">{{ $t("settings.buttons.reset") }}<span class="visuallyhidden"></span></button>
                                                <button @click="save_issue_filters()">{{ $t("settings.buttons.save") }}<span class="visuallyhidden"></span></button>
                                                <br>
                                                <template v-if="issue_filters_response.success || issue_filters_response.error">
                                                    <div :class="'server-response-' + issue_filters_response.state">
                                                        <span>{{ $t(issue_filters_response.message) }} on {{ humanize_date(issue_filters_response.timestamp) }}.</span>
                                                    </div>
                                                </template>
                                            </div>

                                    </tab>

                                <tab v-for="category in scan_form.categories" :name="category.label" :key="category.label">
                                    <section class="test-header">
                                        <div class="test-title">
                                            <h3>{{category.label}}</h3>
                                            <br>
                                            <p>
                                                <template v-for="field in category.fields">

                                                    <label :for="field.name + '_show_dynamic_average'">
                                                        <input type="checkbox" v-model="issue_filters[field.name].show_dynamic_average" :id="field.name + '_show_dynamic_average'">
                                                        {{ $t("settings.show_dynamic_average") }}
                                                    </label><br>
                                                    <!-- Disabled as per #107
                                                    <label :for="field.name + '_only_show_dynamic_average'">
                                                        <input type="checkbox"
                                                               v-model="issue_filters[field.name].only_show_dynamic_average"
                                                               :id="field.name + '_only_show_dynamic_average'"
                                                                :disabled="!issue_filters[field.name].show_dynamic_average">
                                                        {{ $t("settings.only_show_dynamic_average") }}
                                                    </label>
                                                    -->
                                                </template>
                                            </p>

                                        </div>
                                    </section>
                                    <section class="testresults">
                                        <span class="select-deselect-category"><a @click="check_fields(all_fields_from_categories(category))">{{ $t("check") }}</a> / <a @click="uncheck_fields(all_fields_from_categories(category))">{{ $t("uncheck") }}</a></span>

                                        <template v-for="category in category.categories">
                                            <div class="test-subsection">{{ category.label }}<br></div>
                                            <div v-for="field in category.fields" class="testresult_without_icon">
                                                <label :for="field.name + '_visible'">
                                                    <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                    {{ $t(field.name) }}
                                                </label>
                                                <template v-if="field.explanation">
                                                    <p>{{ $t(field.name + "_explanation") }}</p>
                                                </template>
                                            </div>

                                            <template v-if="category.additional_fields.length">
                                                <div class="test-subsection">{{ $t("fields.additional_fields.label") }}</div>
                                                <div v-for="field in category.additional_fields" class="testresult_without_icon">
                                                    <label :for="field.name + '_visible'">
                                                        <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                        {{ $t(field.name) }}
                                                    </label>
                                                    <template v-if="field.explanation">
                                                        <p>{{ $t(field.name + "_explanation") }}</p>
                                                    </template>
                                                </div>
                                            </template>

                                        </template>
                                    </section>


                                    <div>
                                        <button @click="reset_issue_filters()">{{ $t("settings.buttons.reset") }}<span class="visuallyhidden"></span></button>
                                        <button @click="save_issue_filters()">{{ $t("settings.buttons.save") }}<span class="visuallyhidden"></span></button>
                                        <br>
                                        <template v-if="issue_filters_response.success || issue_filters_response.error">
                                            <div :class="'server-response-' + issue_filters_response.state">
                                                <span>{{ $t(issue_filters_response.message) }} on {{ humanize_date(issue_filters_response.timestamp) }}.</span>
                                            </div>
                                        </template>
                                    </div>

                                </tab>
                            </tabs>

                            </template>
                        </template>
                    </div>
                </div>
            </template>

        </div>

        <loading :loading="is_loading"></loading>

        <div v-if="reports.length && !is_loading" style="page-break-before: always;">

            <div class="block fullwidth">
                <h2>{{ $t("chart_info.adoption_timeline.annotation.title") }}</h2>
                <a class="anchor" name="charts"></a>
                <p>{{ $t("chart_info.adoption_timeline.annotation.intro") }}</p>

                <div style="overflow: auto; width: 100%;">
                    <div class="chart-container" style="position: relative; height:300px; width:100%; min-width: 950px;">
                        <line-chart
                                :color_scheme="color_scheme"
                                :translation_key="'charts.adoption_timeline'"
                                :chart_data="issue_timeline_of_related_urllist"
                                :accessibility_text="$t('charts.adoption_timeline.accessibility_text')"
                                :axis="['average_internet_nl_score']">
                        </line-chart>

                        <div style="overflow-x: scroll; overflow-y: hidden;">
                            <table class="table table-striped">
                                <caption>{{ $t("charts.adoption_timeline.title") }}</caption>
                                <thead>
                                    <tr>
                                        <th style="width: 200px;">
                                            &nbsp;{{ $t("charts.adoption_timeline.xAxis_label") }}
                                        </th>
                                        <th>
                                             {{ $t("charts.adoption_timeline.yAxis_label") }}
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

            <div class="block fullwidth" style="page-break-before: always;" v-if='reports.length && "statistics_per_issue_type" in reports[0]'>
                <!-- Accessible alternative for the data is available in the table below. -->
                <h2>
                    {{ $t("chart_info.adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("chart_info.adoption_bar_chart.annotation.intro") }}</p>

                <template v-for="scan_form in scan_methods">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div style="overflow: auto; width: 100%" v-if="visible_fields_from_scan_form(scan_form).length > 0">
                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                <percentage-bar-chart
                                        :title="graph_bar_chart_title"
                                        :translation_key="'charts.adoption_bar_chart'"
                                        :color_scheme="color_scheme"
                                        :chart_data="compare_charts"
                                        :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                        @bar_click="select_category"
                                        :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                        :only_show_dynamic_average="false"
                                        :axis="visible_fields_from_scan_form(scan_form)">
                                </percentage-bar-chart>
                            </div>
                        </div>

                        <template v-for="category in scan_form.categories">
                            <template v-if="category_is_visible(category.key)">
                                <div class="testresult" style="page-break-inside: avoid;" v-if="visible_fields_from_categories(category).length > 0">
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
                                                        :translation_key="'charts.adoption_bar_chart'"
                                                        :color_scheme="color_scheme"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                        @bar_click="select_category"
                                                        :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                        :only_show_dynamic_average="false"
                                                        :axis="visible_fields_from_categories(category)">
                                                </percentage-bar-chart>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <template v-for="subcategory in category.categories">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div class="testresult" style="page-break-inside: avoid;" v-if="fields_from_self(subcategory).length > 0">
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
                                                            :translation_key="'charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                            :only_show_dynamic_average="false"
                                                            :axis="fields_from_self(subcategory)">
                                                    </percentage-bar-chart>
                                                </div>
                                            </div>
                                            <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                            <div style="overflow: auto; width: 100%" v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                                <p>{{ $t("chart_info.magazine.intro") }}</p>
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <percentage-bar-chart
                                                            :title="graph_bar_chart_title"
                                                            :translation_key="'charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
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

            <div class="block fullwidth" style="page-break-before: always;" aria-hidden="true" v-if='compare_charts.length > 1 && "statistics_per_issue_type" in reports[0]'>
                <!-- Todo: there is no cumulative view in the table below, so cumulative data is not (yet) accessible :( -->
                <h2>
                    {{ $t("chart_info.cumulative_adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("chart_info.cumulative_adoption_bar_chart.annotation.intro") }}</p>

                <template v-for="scan_form in scan_methods">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div style="overflow: auto; width: 100%" v-if="visible_fields_from_categories(scan_form).length > 0">
                            <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;" v-if="visible_fields_from_scan_form(scan_form).length > 0">
                                <cumulative-percentage-bar-chart
                                        :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                        'number_of_reports': compare_charts.length})"
                                        :translation_key="'charts.adoption_bar_chart'"
                                        :color_scheme="color_scheme"
                                        :chart_data="compare_charts"
                                        :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
                                        @bar_click="select_category"
                                        :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                        :only_show_dynamic_average="false"
                                        :axis="visible_fields_from_scan_form(scan_form)">
                                </cumulative-percentage-bar-chart>
                            </div>
                        </div>

                        <template v-for="category in scan_form.categories">
                            <template v-if="category_is_visible(category.key)">
                                <div class="testresult" style="page-break-inside: avoid;" v-if="visible_fields_from_categories(category).length > 0">
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
                                                        :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                            'number_of_reports': compare_charts.length})"
                                                        :translation_key="'charts.adoption_bar_chart'"
                                                        :color_scheme="color_scheme"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
                                                        @bar_click="select_category"
                                                        :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                        :only_show_dynamic_average="false"
                                                        :axis="visible_fields_from_categories(category)">
                                                </cumulative-percentage-bar-chart>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <template v-for="subcategory in category.categories">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div class="testresult" style="page-break-inside: avoid;" v-if="fields_from_self(subcategory).length > 0">
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
                                                            :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                            'number_of_reports': compare_charts.length})"
                                                            :translation_key="'charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                            :show_dynamic_average="issue_filters[subcategory.key].show_dynamic_average"
                                                            :only_show_dynamic_average="false"
                                                            :axis="fields_from_self(subcategory)">
                                                    </cumulative-percentage-bar-chart>
                                                </div>
                                            </div>
                                            <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                            <div style="overflow: auto; width: 100%" v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                                <p>This shows the average for Forum Standardisation, it is not possible to
                                                show the average or to select what fields should be visible.</p>
                                                <div class="chart-container" style="position: relative; height:500px; width:100%; min-width: 950px;">
                                                    <cumulative-percentage-bar-chart
                                                            :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                            'number_of_reports': compare_charts.length})"
                                                            :translation_key="'charts.adoption_bar_chart'"
                                                            :color_scheme="color_scheme"
                                                            :chart_data="compare_charts"
                                                            :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
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

            <div v-if="filtered_urls !== undefined" class="block fullwidth" style="page-break-before: always;">
                <h2>{{ $t("report.title") }}</h2>
                <a class="anchor" name="report"></a>
                <p>{{ $t("report.intro") }}</p>

                <div class="sticky-table-container">
                    <table class="table table-striped">
                        <thead class="sticky_labels">

                            <tr class="sticky_labels">
                                <th style="width: 75px; min-width: 75px; border: 0" class="sticky-header">
                                    <div class="rotate">
                                        <span class="arrow" :class="sortOrders['score'] === -1 ? 'dsc' : (sortOrders['score'] === 1 ? 'asc' : 'unknown')"></span>
                                        <span @click="sortBy('score')">{{ $t("score") }}</span>
                                    </div>
                                </th>
                                <th style="width: 225px; min-width: 225px; border: 0" class="sticky-header">
                                    <div class="rotate">
                                        <span class="arrow" :class="sortOrders['url'] === -1 ? 'dsc' : (sortOrders['url'] === 1 ? 'asc' : 'unknown')"></span>
                                        <span @click="sortBy('url')">{{ $t("domain") }}</span>
                                    </div>
                                </th>
                                <th style="border: 0" class="sticky-header" v-for="category in relevant_categories_based_on_settings">
                                    <div class="rotate">
                                        <span class="arrow" :class="sortOrders[category] === -1 ? 'dsc' : (sortOrders[category] === 1 ? 'asc' : 'unknown')"></span>
                                        <span @click="sortBy(category)">{{ $t("" + category) }}</span>
                                    </div>
                                </th>
                            </tr>

                        </thead>

                        <tbody class="gridtable">
                            <template>
                                <!-- Summary row, same data as bar chart, but then in numbers.-->
                                <tr class="summaryrow">
                                    <td colspan="2">
                                        &nbsp;
                                    </td>
                                    <td v-for="category_name in relevant_categories_based_on_settings">
                                        <span v-if="category_name in reports[0].statistics_per_issue_type">
                                            {{reports[0].statistics_per_issue_type[category_name].pct_ok}}%</span>
                                    </td>
                                </tr>

                                <!-- Zoom buttons for accessibility -->
                                <tr class="summaryrow">
                                    <td colspan="2" class="sticky_search">
                                        <label class="visuallyhidden" for="url_filter">{{ $t('report.url_filter') }}</label>
                                        <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.url_filter')">
                                        <p class="visuallyhidden">{{ $t('report.zoom.explanation') }}</p>
                                    </td>
                                    <template v-if="['web', 'mail'].includes(selected_category)">
                                        <td v-for="category_name in relevant_categories_based_on_settings" class="sticky_search">
                                            <button @click="select_category(category_name)">{{ $t("report.zoom.buttons.zoom") }}
                                            <span class="visuallyhidden">{{ $t("report.zoom.buttons.zoom_in_on", [$t("" + category_name)]) }}</span>
                                            </button>
                                        </td>
                                    </template>
                                    <template v-if="!['web', 'mail'].includes(selected_category)">
                                        <td :colspan="relevant_categories_based_on_settings.length" style="text-align: center" class="sticky_search">
                                        {{ $t("report.zoom.zoomed_in_on") }} {{ $t("" + selected_category) }}.
                                            <button @click="select_category(selected_report.urllist_scan_type)">
                                                <span role="img" :aria-label="$t('icons.remove_filter')">❌</span> {{ $t("report.zoom.buttons.remove_zoom") }}
                                            </button>
                                        </td>
                                    </template>
                                </tr>
                            </template>

                            <template v-if="!filtered_urls.length">
                                <tr>
                                    <td :colspan="relevant_categories_based_on_settings.length + 2" style="text-align: center;">😱 {{ $t("report.empty_report") }}</td>
                                </tr>
                            </template>

                            <template v-if="filtered_urls.length">

                                <tr v-for="url in filtered_urls" class="result_row">
                                    <template v-if="!url.endpoints.length">
                                        <td>
                                            -
                                        </td>
                                        <td>{{url.url}}</td>
                                        <td colspan="200">
                                            <small>{{ $t('report.not_eligeble_for_scanning') }}</small>
                                        </td>
                                    </template>
                                    <template v-if="url.endpoints.length">
                                        <td>
                                            <span v-if="selected_report[0].type === 'web'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation, url.url)"></span>
                                            <span v-if="selected_report[0].type === 'mail'" v-html="original_report_link_from_score(url.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation, url.url)"></span>
                                        </td>
                                        <td>{{url.url}}</td>
                                        <td class="testresultcell" v-for="category_name in relevant_categories_based_on_settings">
                                            <template v-if="['web', 'mail'].includes(selected_category)">
                                                <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                                    <!-- Currently the API just says True or False, we might be able to deduce the right label for a category, but that will take a day or two.
                                                    At the next field update, we'll also make the categories follow the new format of requirement level and testresult so HTTP Security Headers
                                                     here is shown as optional, or info if failed. We can also add a field for baseline NL government then. -->
                                                    <template v-if="url.endpoints[0].ratings_by_type[category_name].ok < 1">
                                                        <span v-if="category_name !== 'internet_nl_web_appsecpriv'" class="category_failed">
                                                            <span>{{ $t('' + category_name + '_verdict_bad') }}</span>
                                                        </span>
                                                        <span v-if="category_name === 'internet_nl_web_appsecpriv'" class="category_warning">
                                                            <span>{{ $t('' + category_name + '_verdict_bad') }}</span>
                                                        </span>
                                                    </template>
                                                    <span class="category_passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0">
                                                        <span>{{ $t('' + category_name + '_verdict_good') }}</span>
                                                    </span>
                                                </template>
                                                <span class="" v-if="url.endpoints[0].ratings_by_type[category_name] === undefined">
                                                    {{ $t("report.results.unknown") }}
                                                </span>
                                            </template>
                                            <template v-if="!['web', 'mail'].includes(selected_category)">

                                                <template v-if="category_name in url.endpoints[0].ratings_by_type">
                                                    <span class="not_applicable" v-if="url.endpoints[0].ratings_by_type[category_name].not_applicable > 0">
                                                        <span>{{ $t("report.results.not_applicable") }}</span>
                                                    </span>
                                                    <span class="not_testable" v-if="url.endpoints[0].ratings_by_type[category_name].not_testable > 0">
                                                        <span>{{ $t("report.results.not_testable") }}</span>
                                                    </span>
                                                    <span class="failed" v-if="url.endpoints[0].ratings_by_type[category_name].high > 0">
                                                        <span>{{ $t("report.results.failed") }} {{ $t('' + category_name + '_verdict_bad') }}</span>
                                                    </span>
                                                    <span class="warning" v-if="url.endpoints[0].ratings_by_type[category_name].medium > 0">
                                                        <span>{{ $t("report.results.warning") }} {{ $t('' + category_name + '_verdict_bad') }}</span>
                                                    </span>
                                                    <span class="info" v-if="url.endpoints[0].ratings_by_type[category_name].low > 0">
                                                        <span>{{ $t("report.results.info") }} {{ $t('' + category_name + '_verdict_bad') }}</span>
                                                    </span>
                                                    <span class="passed" v-if="url.endpoints[0].ratings_by_type[category_name].ok > 0
                                                    && !url.endpoints[0].ratings_by_type[category_name].not_applicable
                                                    && !url.endpoints[0].ratings_by_type[category_name].not_testable">
                                                        <span>{{ $t("report.results.passed") }} {{ $t('' + category_name + '_verdict_good') }}</span>
                                                    </span>
                                                </template>
                                                <span class="" v-if="url.endpoints[0].ratings_by_type[category_name] === undefined">
                                                    <span>{{ $t("report.results.unknown") }}</span>
                                                </span>
                                            </template>
                                        </td>
                                    </template>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
        <!-- This keeps the dropdown up to date? Does it really... it doesn't. Or should we just refresh on open? -->
        <autorefresh :visible="false" :callback="get_recent_reports" :refresh_per_seconds="60"></autorefresh>
    </div>
</template>
{% endverbatim %}

<script>
// Done: order of the fields, and possible sub sub categories
// Done: allow filtering on what results to show
// Done: store filter options for reports (as generic or per report? or as a re-applicable set?) Per user account.
// Done: how to add a item for legacy views?
// Done: how to translate graphs?
const Report = Vue.component('report', {
    i18n: {
        messages: {
            en: {
                mail: 'E-Mail',
                web: 'Web',

                score: "Score",
                domain: "Domain",

                check: "Select all",
                uncheck: "Deselect all",

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
                    subtest_not_applicable: "Not applicable ⇒ no score impact",
                    subtest_not_testable: "Not testable ⇒ no score impact",
                },

                header: {
                    title: 'Reports',
                    intro: 'Select one or multiple reports, these will be displayed below.',
                    select_report: 'Select report...',
                    max_elements: 'Maximum number of reports selected.',
                    no_options: 'No reports available.',
                },

                chart_info: {
                    adoption_timeline: {
                        annotation: {
                            title: 'Adoption of standards over time',
                            intro: 'This graph compares various measurements of the same list over time. ' +
                                'This provides a visual indication of the progress of standards adoption. A table with the ' +
                                'same values is avaiable below. This graph shows the average score of internet.nl. Note that ' +
                                'only the values of the first selected report are shown.'
                        },
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
                    },
                    cumulative_adoption_bar_chart: {
                        annotation: {
                            title: 'Average adoption of standards over multiple reports',
                            intro: 'This graph shows the average adoption per standard averaged over multiple reports.',
                        },
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
                    show_dynamic_average: "Show the average of selected fields",
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
            },
            nl: {
                mail: 'E-Mail',
                web: 'Web',

                score: "Score",
                domain: "Domein",

                check: "Selecteer alle",
                uncheck: "Deselecteer alle",

                chart_info: {
                    adoption_timeline: {
                        annotation: {
                            title: 'Adoptie van standaarden over tijd.',
                            intro: 'Deze grafiek toont verschillende metingen van dezelfde lijst over tijd. ' +
                                'Dit geeft zicht over de voortgang van de adoptie van standaarden. Het toont de gemiddelde score van internet.nl. ' +
                                'Deze grafiek toont alleen de gemiddelden van het eerst geselecteerde rapport.'
                        },
                    },
                    magazine: {
                        intro: "Onderstaande grafiek toont het gemiddelde van alle magazine velden. Deze grafiek kan niet worden aangepast, ook niet door de zichtbaarheid van velden aan te passen.",
                    },
                    adoption_bar_chart: {
                        annotation: {
                            title: 'Adoptie van standaarden',
                            intro: 'Deze grafiek toont het percentage adoptie per categorie en onderliggende metingen.',
                        },
                    },
                    cumulative_adoption_bar_chart: {
                        annotation: {
                            title: 'Gemiddelde adoptie, waarbij rapporten bij elkaar worden opgeteld',
                            intro: 'In deze grafiek worden de geselecteerde rapporten bij elkaar opgeteld, en daar het gemiddelde van getoond.',
                        },
                    }
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
                    intro: 'Rapporten gemaakt op basis van scans van lijsten.',
                    select_report: 'Selecteer rapport...',
                    max_elements: 'Maximum aantal rapporten geselecteerd.',
                    no_options: 'Geen rapporten beschikbaar.',
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
                    show_dynamic_average: "Toon het gemiddelde van de geselecteerde velden",
                    only_show_dynamic_average: "Toon alleen het dynamisch berekende gemiddelde",
                },

                // legacy values
                mail_legacy: 'Measurements on agreed security standards + IPv6 Monitor',
                web_legacy: 'Measurements on agreed security standards + IPv6 Monitor',
            }
        }
    },
    name: 'report',
    template: '#report_template',
    mixins: [humanize_mixin, http_mixin],
    data: function() {
        return {
            is_loading: false,

            // Supporting multiple reports at the same time is hard to understand. Don't know how / if we can do
            // comparisons.
            reports: [],

            // instead we support one report with one set of urls. This is the source set of urls that can be copied at will
            original_urls: [],

            // this is the set of urls where filters are applied.
            filtered_urls: [],

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
                web: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                web_legacy: {visible: false, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_web_tls: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_web_dnssec: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_web_ipv6: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_web_appsecpriv: {
                    visible: true,
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },  // Added 24th of May 2019

                mail: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                mail_legacy: {visible: false, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_mail_dashboard_tls: {
                    visible: true,
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                internet_nl_mail_dashboard_auth: {
                    visible: true,
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                internet_nl_mail_dashboard_dnssec: {
                    visible: true,
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                internet_nl_mail_dashboard_ipv6: {
                    visible: true,
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },

                // a request was made to enable/disable dynamic averages on every graph. For this each graph
                // needed an identifier, which became "category" -> thing. In this, values are stored.
                // todo: make sure the values are initialized properly if they don't exist.
                category_web_ipv6_name_server: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_ipv6_web_server: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_dnssec_dnssec: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_tls_http: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_tls_tls: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_tls_certificate: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_tls_dane: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_security_options_appsecpriv: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                category_web_forum_standardisation_magazine: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                category_web_forum_standardisation_ipv6_monitor: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },

                category_mail_ipv6_name_servers: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_ipv6_mail_servers: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dnssec_email_address_domain: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                category_mail_dnssec_mail_server_domain: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_auth_dmarc: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_aut_dkim: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_aut_spf: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_tls: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_certificate: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_dane: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_forum_standardisation_magazine: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },
                category_mail_forum_standardisation_ipv6_monitor: {
                    show_dynamic_average: true,
                    only_show_dynamic_average: false
                },


                internet_nl_web_https_cert_domain: {visible: true},
                internet_nl_web_https_http_redirect: {visible: true},
                internet_nl_web_https_cert_chain: {visible: true},
                internet_nl_web_https_tls_version: {visible: true},
                internet_nl_web_https_tls_clientreneg: {visible: true},
                internet_nl_web_https_tls_ciphers: {visible: true},
                internet_nl_web_https_http_available: {visible: true},
                internet_nl_web_https_dane_exist: {visible: true},
                internet_nl_web_https_http_compress: {visible: true},
                internet_nl_web_https_http_hsts: {visible: true},
                internet_nl_web_https_tls_secreneg: {visible: true},
                internet_nl_web_https_dane_valid: {visible: true},
                internet_nl_web_https_cert_pubkey: {visible: true},
                internet_nl_web_https_cert_sig: {visible: true},
                internet_nl_web_https_tls_compress: {visible: true},
                internet_nl_web_https_tls_keyexchange: {visible: true},
                internet_nl_web_dnssec_valid: {visible: true},
                internet_nl_web_dnssec_exist: {visible: true},
                internet_nl_web_ipv6_ws_similar: {visible: true},
                internet_nl_web_ipv6_ws_address: {visible: true},
                internet_nl_web_ipv6_ns_reach: {visible: true},
                internet_nl_web_ipv6_ws_reach: {visible: true},
                internet_nl_web_ipv6_ns_address: {visible: true},
                internet_nl_mail_starttls_cert_domain: {visible: true},
                internet_nl_mail_starttls_tls_version: {visible: true},
                internet_nl_mail_starttls_cert_chain: {visible: true},
                internet_nl_mail_starttls_tls_available: {visible: true},
                internet_nl_mail_starttls_tls_clientreneg: {visible: true},
                internet_nl_mail_starttls_tls_ciphers: {visible: true},
                internet_nl_mail_starttls_dane_valid: {visible: true},
                internet_nl_mail_starttls_dane_exist: {visible: true},
                internet_nl_mail_starttls_tls_secreneg: {visible: true},
                internet_nl_mail_starttls_dane_rollover: {visible: true},
                internet_nl_mail_starttls_cert_pubkey: {visible: true},
                internet_nl_mail_starttls_cert_sig: {visible: true},
                internet_nl_mail_starttls_tls_compress: {visible: true},
                internet_nl_mail_starttls_tls_keyexchange: {visible: true},
                internet_nl_mail_auth_dmarc_policy: {visible: true},
                internet_nl_mail_auth_dmarc_exist: {visible: true},
                internet_nl_mail_auth_spf_policy: {visible: true},
                internet_nl_mail_auth_dkim_exist: {visible: true},
                internet_nl_mail_auth_spf_exist: {visible: true},
                internet_nl_mail_dnssec_mailto_exist: {visible: true},
                internet_nl_mail_dnssec_mailto_valid: {visible: true},
                internet_nl_mail_dnssec_mx_valid: {visible: true},
                internet_nl_mail_dnssec_mx_exist: {visible: true},
                internet_nl_mail_ipv6_mx_address: {visible: true},
                internet_nl_mail_ipv6_mx_reach: {visible: true},
                internet_nl_mail_ipv6_ns_reach: {visible: true},
                internet_nl_mail_ipv6_ns_address: {visible: true},

                internet_nl_mail_legacy_dmarc: {visible: false},
                internet_nl_mail_legacy_dkim: {visible: false},
                internet_nl_mail_legacy_spf: {visible: false},
                internet_nl_mail_legacy_dmarc_policy: {visible: false},
                internet_nl_mail_legacy_spf_policy: {visible: false},
                internet_nl_mail_legacy_start_tls: {visible: false},
                internet_nl_mail_legacy_start_tls_ncsc: {visible: false},
                internet_nl_mail_legacy_dnssec_email_domain: {visible: false},
                internet_nl_mail_legacy_dnssec_mx: {visible: false},
                internet_nl_mail_legacy_dane: {visible: false},
                internet_nl_mail_legacy_ipv6_nameserver: {visible: false},
                internet_nl_mail_legacy_ipv6_mailserver: {visible: false},

                internet_nl_web_legacy_dnssec: {visible: false},
                internet_nl_web_legacy_tls_available: {visible: false},
                internet_nl_web_legacy_tls_ncsc_web: {visible: false},
                internet_nl_web_legacy_https_enforced: {visible: false},
                internet_nl_web_legacy_hsts: {visible: false},
                internet_nl_web_legacy_ipv6_nameserver: {visible: false},
                internet_nl_web_legacy_ipv6_webserver: {visible: false},
                internet_nl_web_legacy_dane: {visible: false},

                // Fields added on the 24th of May 2019
                internet_nl_mail_auth_dmarc_policy_only: {visible: false},  // Added 24th of May 2019
                internet_nl_mail_auth_dmarc_ext_destination: {visible: false},  // Added 24th of May 2019

                // no feature flags in report
                internet_nl_mail_non_sending_domain: {visible: false},  // Added 24th of May 2019
                internet_nl_mail_server_configured: {visible: false},  // Added 24th of May 2019
                internet_nl_mail_servers_testable: {visible: false},   // Added 24th of May 2019
                internet_nl_mail_starttls_dane_ta: {visible: false},  // Added 24th of May 2019

                internet_nl_web_appsecpriv_csp: {visible: true},  // Added 24th of May 2019
                internet_nl_web_appsecpriv_referrer_policy: {visible: true},  // Added 24th of May 2019
                internet_nl_web_appsecpriv_x_content_type_options: {visible: true},  // Added 24th of May 2019
                internet_nl_web_appsecpriv_x_frame_options: {visible: true},  // Added 24th of May 2019
                internet_nl_web_appsecpriv_x_xss_protection: {visible: true},  // Added 24th of May 2019
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

            // a list of reports...
            selected_report: null,

            // graphs:
            issue_timeline_of_related_urllist: [],

            // https://github.com/ashiguruma/patternomaly/blob/master/assets/pattern-list.png
            possible_chart_patterns: ['weave', 'dot', 'ring', 'dash', 'plus', 'zigzag', 'square', 'diagonal', 'disc', 'zigzag-vertical', 'triangle', 'line', 'cross-dash', 'diamond'],
            // See #18 for the primary sources of these colors.
            // this can help to explain the colors: https://www.canva.com/colors/color-wheel/
            // blue #154273, orange #E17000, green #39870C, red #731542, gray #7e7d82
            possible_chart_colors: ['rgba(225, 112, 0, 1)', 'rgba(57, 135, 12, 1)', 'rgba(115, 21, 66, 1)', 'rgb(89, 88, 92)', 'rgba(21, 66, 115, 1)',],
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

                // a long list of possible colors and patterns, this is autogenerated on load
                incremental: [],
            },
            compare_charts: [],
            compare_oldest_data: "",
            older_data_available: true,

            // simple sorting a la bootstrapvue.
            sortKey: 'url',
            sortOrders: {'url': 1},
        }
    },
    mounted: function(){
        this.color_scheme.incremental = this.generate_color_increments(10);
        this.load_issue_filters();
        this.get_recent_reports();
        // this supports: http://localhost:8000/reports/83/
        // todo: this can be replaced by $route.params.report, which is much more readable.
        setTimeout(() => {
            if (window.location.href.split('/').length > 3) {
                let get_id = window.location.href.split('/')[6];
                // can we change the select2 to a certain value?

                this.filtered_recent_reports.forEach((option) => {
                   if (option.id + "" === get_id){
                       // also re-create label
                       option.label = `#${option.id} - ${option.list_name} - type: ${option.type} - from: ${this.humanize_date(option.at_when)}`;
                       this.selected_report = [option];
                   }
                });
            }
        }, 1000)
        this.$nextTick(() => {accordinate();});
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

        sortBy: function (key) {
            // console.log(`Sorting by ${key}.`);
            this.sortKey = key;

            // dynamically populate the orders
            if (!(key in this.sortOrders)){
                // console.log('autopopulating sortOrder');
                this.sortOrders[key] = 1;
            }

            this.sortOrders[key] = this.sortOrders[key] * -1;
            this.filtered_urls = this.order_urls(this.filtered_urls);
        },

        generate_color_increments: function(number){
            // Generate n colors for charts, rotating over the available options. Returns a list with css properties.
            // The first item is always the same in a single color to give a consistent look/feel to all first graphs
            let colors = [{background: 'rgba(21, 66, 115, 1)', border: 'rgba(21, 66, 115, 1)'},];
            for(let i=0; i<number; i++){
                // make sure we never run out of options.
                let my_pattern = this.possible_chart_patterns.shift();
                this.possible_chart_patterns.push(my_pattern);
                let my_color = this.possible_chart_colors.shift();
                this.possible_chart_colors.push(my_color);

                colors.push({background: pattern.draw(my_pattern, my_color), border: my_color})
            }

            return colors;
        },

        get_issue_filter_data(key){
            try {
                return this.issue_filters[key];
            } catch(err) {
                this.issue_filters[key] = {'visible': true};
                // console.log(`Issue filter for ${key} does not exist. Created it.`)
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
                this.filtered_urls = this.order_urls(data[0].calculation.urls);
                this.get_timeline();
                this.is_loading = false;

                // we already have the first report, so don't request it again.
                // note that when setting the first chart, the subsequent updates do not "point ot a new object"
                // so a state change doesn not happen automatically using a wathcer, you have to watch deep.
                // console.log(`First compare chart set...`);
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

                    this.upgrade_issue_filter_with_new_field('category_web_ipv6_name_server');
                    this.upgrade_issue_filter_with_new_field('category_web_ipv6_web_server');
                    this.upgrade_issue_filter_with_new_field('category_web_dnssec_dnssec');
                    this.upgrade_issue_filter_with_new_field('category_web_tls_http');
                    this.upgrade_issue_filter_with_new_field('category_web_tls_tls');
                    this.upgrade_issue_filter_with_new_field('category_web_tls_certificate');
                    this.upgrade_issue_filter_with_new_field('category_web_tls_dane');
                    this.upgrade_issue_filter_with_new_field('category_web_security_options_appsecpriv');
                    this.upgrade_issue_filter_with_new_field('category_web_forum_standardisation_magazine');
                    this.upgrade_issue_filter_with_new_field('category_web_forum_standardisation_ipv6_monitor');
                    this.upgrade_issue_filter_with_new_field('category_mail_ipv6_name_servers');
                    this.upgrade_issue_filter_with_new_field('category_mail_ipv6_mail_servers');
                    this.upgrade_issue_filter_with_new_field('category_mail_dnssec_email_address_domain');
                    this.upgrade_issue_filter_with_new_field('category_mail_dnssec_mail_server_domain');
                    this.upgrade_issue_filter_with_new_field('category_mail_dashboard_auth_dmarc');
                    this.upgrade_issue_filter_with_new_field('category_mail_dashboard_aut_dkim');
                    this.upgrade_issue_filter_with_new_field('category_mail_dashboard_aut_spf');
                    this.upgrade_issue_filter_with_new_field('category_mail_starttls_tls');
                    this.upgrade_issue_filter_with_new_field('category_mail_starttls_certificate');
                    this.upgrade_issue_filter_with_new_field('category_mail_starttls_dane');
                    this.upgrade_issue_filter_with_new_field('category_mail_forum_standardisation_magazine');
                    this.upgrade_issue_filter_with_new_field('category_mail_forum_standardisation_ipv6_monitor');
                }
            });
        },


        upgrade_issue_filter_with_new_field: function(field_name){
            if (!Object.keys(this.issue_filters).includes(field_name))
                        this.issue_filters[field_name] = {visible: false, show_dynamic_average: true, only_show_dynamic_average: false}
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
                    // console.log(`Compare chart ${compare_chart_id} set...`);
                    this.$set(this.compare_charts, compare_chart_id, report[0]);

                    // given the charts are on a fixed number in the array, vue doesn't pick up changes.
                    // and as the order matters, this is a solution that fixes that.
                    this.$nextTick(() => {accordinate(); this.$forceUpdate();});
                }

            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },

        get_recent_reports: function(){
            fetch(`/data/report/recent/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                // console.log("Get recent reports");
                let options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].label = `#${data[i].id} - ${data[i].list_name} - type: ${data[i].type} - from: ${this.humanize_date(data[i].at_when)}`;
                    options.push(data[i]);
                }
                this.available_recent_reports = options;
                this.filtered_recent_reports = options;
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

            // keep the search order, use a correctly ordered set of original urls:
            let tmp_urls = this.order_urls(this.original_urls);
            tmp_urls.forEach(function(value) {
                if (value.url.includes(keyword))
                    urls.push(value)
            });
            this.filtered_urls = this.order_urls(urls);

        },
        order_urls: function(data){
            // todo: add sorting icons :)
            // todo: transform this to a component too, move translations here.
            // https://alligator.io/vuejs/grid-component/
            let sortKey = this.sortKey;
            if (!sortKey){
                return data;
            }

            let order = this.sortOrders[sortKey] || 1;

            // The ordering keys are in different places in the data. See websecmap for the structure of the data.
            // So filter based on this structure.
            if (sortKey === "url"){
                data = data.slice().sort(function (a, b) {
                    // for everything that is not the url name itself, is neatly tucked away.
                    a = a[sortKey];
                    b = b[sortKey];
                    return (a === b ? 0 : a > b ? 1 : -1) * order
                });

                return data;
            }
            if (sortKey === "score"){
                // todo: determine web or mail, split the scores etc, not very fast.
                data = data.slice().sort(function (a, b) {
                    // for everything that is not the url name itself, is neatly tucked away. Only filter on high? Or on what kind of structure?
                    if (this.selected_category === 'mail'){
                        a = parseInt(a.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation.split(" ")[0]);
                        b = parseInt(b.endpoints[0].ratings_by_type['internet_nl_mail_dashboard_overall_score'].explanation.split(" ")[0]);
                    } else {
                        a = parseInt(a.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation.split(" ")[0]);
                        b = parseInt(b.endpoints[0].ratings_by_type['internet_nl_web_overall_score'].explanation.split(" ")[0]);
                    }
                    return (a === b ? 0 : a > b ? 1 : -1) * order
                });
                return data;
            }
            data = data.slice().sort(function (a, b) {
                // for everything that is not the url name itself, is neatly tucked away. Only filter on high? Or on what kind of structure?
                let aref = a.endpoints[0].ratings_by_type[sortKey];
                let bref = b.endpoints[0].ratings_by_type[sortKey];
                a = `${aref.high} ${aref.medium} ${aref.low} ${aref.not_applicable}  ${aref.not_testable} ${aref.ok}`;
                b = `${bref.high} ${bref.medium} ${bref.low} ${bref.not_applicable}  ${bref.not_testable} ${bref.ok}`;
                return (a === b ? 0 : a > b ? 1 : -1) * order
            });

            return data;
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
                        <img src="/static/images/vendor/internet_nl/favicon.png" style="height: 16px;" alt="${this.$i18n.t('report.link_to_report', {'url': url})}"> ${sc[0]}%
                        <span class="visuallyhidden">${this.$i18n.t('report.link_to_report', {'url': url})}</span>
                    </a>`
        },
        visible_fields_from_scan_form(scan_form){
            // see if any of the underlaying categories is visible. If so, include the category.
            let fields = [];

            scan_form.categories.forEach((category) => {
                // console.log(category.key);
                if (this.category_is_visible(category.key)){
                        category.fields.forEach((field) => {
                        fields.push(field.name);
                    });
                    category.additional_fields.forEach((field) => {
                        fields.push(field.name);
                    });
                }
            });

            // console.log(`Visible from scan_form: ${fields}`);

            return fields;
        },
        all_fields_from_categories(categories){
            let fields = [];

            categories.categories.forEach((category) => {

                category.fields.forEach((field) => {
                    fields.push(field.name);
                });
                category.additional_fields.forEach((field) => {
                    fields.push(field.name);
                });

            });

            return fields;
        },
        // should be named: visible fields from categories
        visible_fields_from_categories(categories){
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
        category_is_visible: function (category_key){

            // See #6. If any of the subcategory fields
            return this.visible_fields_from_categories(this.get_category_by_name(category_key)).length > 0;
        },
        get_category_by_name: function(category_key){
            let found = null;
            this.scan_methods.forEach((scan_method) => {
                scan_method.categories.forEach((category) => {
                    if (category.key === category_key){
                        found = category;
                    }
                });

            });
            if (!found) {
                throw `Category ${category_key} does not exist.`;
            } else {
                return found;
            }
        },

        check_fields: function(list_of_fields){
            list_of_fields.forEach((field) => {
                this.issue_filters[field].visible = true;
            })
        },

        uncheck_fields: function(list_of_fields){
            list_of_fields.forEach((field) => {
                this.issue_filters[field].visible = false;
            })
        }

    },
    watch: {

        // support keep alive routing
        $route: function(to, from){
            // https://router.vuejs.org/guide/essentials/dynamic-matching.html
            if (undefined !== to.params.report){
                // See if we can find a report to mach:
                this.available_recent_reports.forEach((item) => {
                    if (item.id === to.params.report){
                        this.selected_report = [item];
                    }
                });
            }
        },

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

            // Always update the URL to reflect the latest report, so it can be easily shared and the page reloaded
            history.pushState(
                {},
                null,
                '/spa/#/report/' + new_value[0].id
              );

            // when deleting any report, we will need to rebuild the compare charts...
            this.compare_charts = [];
            this.load(new_value[0].id);

            // to test this:
            // this.compare_with(new_value[0].id, 1);
            // this.compare_with(new_value[0].id, 2);

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
            return i18n.t('charts.adoption_radar_chart.title', {
                'list_information': this.selected_report[0].list_name,
                'number_of_domains': this.original_urls.length
            });
        },

        graph_bar_chart_title: function(){
            // fixing https://github.com/internetstandards/Internet.nl-dashboard/issues/65
            // 1 report:
            if (this.selected_report.length === 1) {
                return i18n.t('charts.adoption_bar_chart.title_single', {
                    'list_information': this.selected_report[0].list_name,
                    'number_of_domains': this.original_urls.length
                });
            } else {
                return i18n.t('charts.adoption_bar_chart.title_multiple', {
                    'number_of_reports': this.selected_report.length,
                });
            }
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
                                    key: 'category_web_ipv6_name_server',
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
                                    key: 'category_web_ipv6_web_server',
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
                                    key: 'category_web_dnssec_dnssec',
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
                                    key: 'category_web_tls_http',
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
                                    key: 'category_web_tls_tls',
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
                                    key: 'category_web_tls_certificate',
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
                                    key: 'category_web_tls_dane',
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
                                    key: 'category_web_security_options_appsecpriv',
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
                            label: i18n.t('fields.forum_standardistation.category_label'),
                            key: 'web_legacy',
                            fields: [
                                {name: 'web_legacy'},
                            ],
                            additional_fields: [],

                            categories: [
                                {
                                    name: 'Measurements on agreed security standards',
                                    key: 'category_web_forum_standardisation_magazine',
                                    label: i18n.t('fields.forum_standardistation.measurements_on_agreed_security_standards'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_dnssec',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_dnssec_explanation'},
                                        {name: 'internet_nl_web_legacy_tls_available',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_available_explanation'},
                                        {name: 'internet_nl_web_legacy_tls_ncsc_web',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_ncsc_web_explanation'},
                                        {name: 'internet_nl_web_legacy_https_enforced',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_https_enforced_explanation'},
                                        {name: 'internet_nl_web_legacy_hsts',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_hsts_explanation'},
                                        // {name: 'internet_nl_web_legacy_dane'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'IPv6 Monitor',
                                    key: 'category_web_forum_standardisation_ipv6_monitor',
                                    label: i18n.t('fields.forum_standardistation.ipv6_monitor'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_ipv6_nameserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_web_legacy_ipv6_webserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_webserver_explanation'},
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
                                    key: 'category_mail_ipv6_name_servers',
                                    label: internet_nl_messages[language].internet_nl.results_domain_mail_ipv6_name_servers_label,
                                    fields: [
                                        {name: 'internet_nl_mail_ipv6_ns_address'},
                                        {name: 'internet_nl_mail_ipv6_ns_reach'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'Mail server(s)',
                                    key: 'category_mail_ipv6_mail_servers',
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
                                    key: 'category_mail_dnssec_email_address_domain',
                                    label: internet_nl_messages[language].internet_nl.results_mail_dnssec_domain_label,
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mailto_exist'},
                                        {name: 'internet_nl_mail_dnssec_mailto_valid'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'mail server domain(s)',
                                    key: 'category_mail_dnssec_mail_server_domain',
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
                                    key: 'category_mail_dashboard_auth_dmarc',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_dmarc_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dmarc_exist'},
                                        {name: 'internet_nl_mail_auth_dmarc_policy'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'DKIM',
                                    key: 'category_mail_dashboard_aut_dkim',
                                    label: internet_nl_messages[language].internet_nl.results_mail_auth_dkim_label,
                                    fields: [
                                        {name: 'internet_nl_mail_auth_dkim_exist'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'SPF',
                                    key: 'category_mail_dashboard_aut_spf',
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
                                    key: 'category_mail_starttls_tls',
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
                                    key: 'category_mail_starttls_certificate',
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
                                    key: 'category_mail_starttls_dane',
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
                            label: i18n.t('fields.forum_standardistation.category_label'),
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
                                    key: 'category_mail_forum_standardisation_magazine',
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_dmarc',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dmarc_explanation'},
                                        {name: 'internet_nl_mail_legacy_dkim',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dkim_explanation'},
                                        {name: 'internet_nl_mail_legacy_spf',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_spf_explanation'},
                                        {name: 'internet_nl_mail_legacy_dmarc_policy',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dmarc_policy_explanation'},
                                        {name: 'internet_nl_mail_legacy_spf_policy',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_spf_policy_explanation'},
                                        {name: 'internet_nl_mail_legacy_start_tls',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_start_tls_explanation'},
                                        {name: 'internet_nl_mail_legacy_start_tls_ncsc',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_start_tls_ncsc_explanation'},
                                        // {name: 'internet_nl_mail_legacy_dnssec_email_domain'},
                                        {name: 'internet_nl_mail_legacy_dnssec_mx',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dnssec_mx_explanation'},
                                        {name: 'internet_nl_mail_legacy_dane',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_dane_explanation'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'IPv6 Monitor',
                                    // todo: translate label
                                    label: 'IPv6 Monitor',
                                    key: 'category_mail_forum_standardisation_ipv6_monitor',
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_ipv6_nameserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_mail_legacy_ipv6_mailserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_mailserver_explanation'},
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

            // console.log(`Selected category: ${this.selected_category}`);

            this.scan_methods.forEach((scan_method) => {
                // console.log("scan_method " + scan_method.name);
                // todo: also get relevant column for scan_methods, just like with graphs. But given large refactor,
                // we'll do that later.
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
                        // console.log("category " + category.name);
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

            // console.log(`Preferred fields: ${preferred_fields}`);

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
</script>
