{% verbatim %}
<style>
    #report-template {
        width: 100%;
        min-height: 500px;
    }

    /* Do print the whole table... */
    @media print {
        body {
            background-color: red;
        }
        #report-template {
            min-height: 100% !important;
        }

        /* When printing, the table should fill several pages */
        #report-template .sticky-table-container {
            max-height: none !important;
            overflow-x: inherit;
            overflow-y: inherit;
        }

        /* Allow printing of graphs, make sure they don't go wider than the page width... */
        /* https://stackoverflow.com/questions/41674976/resize-chart-js-canvas-for-printing */
        /* We'll resize the image to fit plain a4 paper, otherwise the aspect ratios are distorted.*/
        canvas.graph-image {
            height: 60% !important;
            width: 60% !important;
        }

        /* Also remove the superfluous container sizes during print, as the image is a bit smaller now: */
        .chart-container {
            height: 100% !important;
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

    /* Make the header stay up with a white background. */
    #report-template thead {
        position: sticky;
        top: 0;
        background-color: white;
    }

    #horrible-chrome-td-sticky-white-background-fix {
        /* Chrome white sticky headers overlap, causing text to disappear, firefox does render it correctly.
        This fix creates a white background behind the text labels. */
        width: 100%;
        height: 210px;
        position: absolute;
        top: 0px;
        background: white;
    }

    #report-template th {
        /* Firefox does not need this set to white, chrome does, otherwise the background will bleed through... */
        /* background-color: white; */
    }

    #report-template th:after {
        /* Chrome uses translucent background, */
        background-color: white;
    }

    #report-template th.sticky-header {
        position: sticky;
        top: -1px;
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
        padding: 5px 3px;
        z-index: 1000;
    }

    /* Why emulate bootstrap? */
    .table {
        width: 100%;
        max-width: 100%;
        margin-bottom: 1rem;
        background-color: white;
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
        width: 32px; /* Needs to be 32 px for comparison to be visible.*/
        height: 20px;
        display: block;
        color: transparent;

        /** While hidden, can a screen reader still find it? */
        overflow: hidden;
    }

    #report-template .testresultcell span span {
        font-size: 1px;
    }

    .testresultcell {
        border-left: 1px solid #dee2e6;
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
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 10px solid #00a0c6;
    }

    .arrow.dsc {
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 10px solid #00a0c6;
    }

    .arrow.unknown {
        border-left: 10px solid #00a0c6;
        border-right: 10px solid #00a0c6;
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

                <div class="do-not-print testresult_without_icon" v-if="selected_report.length < 2">
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

                <div class="do-not-print testresult_without_icon">
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
                                    <tab :name="$t('settings.main_category')">
                                        <h3>{{ $t("settings.main_category") }}</h3>
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
                                                        <input type="checkbox" v-model="issue_filters[field.name].show_dynamic_average" :onchange="visible_metrics_see_if_category_is_relevant(category)" :id="field.name + '_show_dynamic_average'">
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
                                        <span class="select-deselect-category"><a @click="check_fields(all_field_names_from_categories(category))">{{ $t("check") }}</a> / <a @click="uncheck_fields(all_field_names_from_categories(category))">{{ $t("uncheck") }}</a></span>

                                        <template v-for="category in category.categories">
                                            <div class="test-subsection">{{ category.label }}<br></div>
                                            <div v-for="field in category.fields" class="testresult_without_icon">
                                                <label :for="field.name + '_visible'">
                                                    <input type="checkbox" v-model="issue_filters[field.name].visible" :id="field.name + '_visible'">
                                                    {{ $t(field.name) }}
                                                </label>
                                                <template v-if="field.explanation">
                                                    <p><i>{{ $t(field.name + "_explanation") }}</i></p>
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
                                                        <p><i>{{ $t(field.name + "_explanation") }}</i></p>
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

        <div v-if="reports.length && !is_loading">

            <div class="block fullwidth">
                <h2>
                    📊 #{{selected_report[0].id}} - {{ selected_report[0].list_name }}</h2>
                <span>{{ $t("report_header.type_of_scan_performed") }}:
                    <img src="/static/images/vendor/internet_nl/icon-website-test.svg" style="height: 1em;" v-if="selected_report[0].type === 'web'">
                    <img src="/static/images/vendor/internet_nl/icon-emailtest.svg" style="height: 1em;" v-if="selected_report[0].type === 'mail'"> {{ selected_report[0].type }}<br>
                    {{ $t("report_header.number_of_domains") }}: {{ selected_report[0].number_of_urls }}<br> {{ $t("report_header.data_from") }} {{ humanize_date(selected_report[0].at_when) }}<br>
                    📘 <router-link :to="{ name: 'numbered_lists', params: { list: selected_report[0].urllist_id }}">{{ selected_report[0].list_name }}</router-link><br>
                </span><br>




                <div v-for="report in selected_report" v-if="selected_report.length > 1" style="padding-left: 10px">
                    <!-- Skip the first report -->
                    <template v-if="report.id !== selected_report[0].id">
                        <h3>{{ $t("report_header.compared_to") }}: #{{report.id}} - {{ report.list_name }}</h3>
                        <span>
                            {{ $t("report_header.number_of_domains") }}: {{ report.number_of_urls }}<br>
                            {{ $t("report_header.data_from") }} {{ humanize_date(report.at_when) }}<br>
                            📘 <router-link :to="{ name: 'numbered_lists', params: { list: report.urllist_id }}">{{ report.list_name }}</router-link><br>
                        </span>
                    </template>
                </div>

                <template v-if="selected_report.length > 2">
                    <p style="padding-top: 1em;">⚠️ {{ $t("report_header.only_graphs") }}</p>
                </template>

            </div>

            <internet-nl-charts
                    :selected_report="selected_report"
                    :scan_methods="scan_methods"
                    :compare_charts="compare_charts"
                    :issue_filters="issue_filters"
                    :field_name_to_category_names="field_name_to_category_names"
            >
            </internet-nl-charts>

            <!-- The table is only displayed with up to two reports (the first as the source of the table, the second as a comparison). -->
            <div v-if="filtered_urls !== undefined && selected_report.length < 3" class="block fullwidth" style="page-break-before: always;">
                <h2>{{ $t("report.title") }}</h2>
                <a class="anchor" name="report"></a>
                <p>{{ $t("report.intro") }}</p>

                <p v-if="differences_compared_to_current_list">
                    <template v-if="differences_compared_to_current_list.both_are_equal">
                        {{ $t("differences_compared_to_current_list.equal") }}
                        {{ $t("differences_compared_to_current_list.both_list_contain_n_urls", [differences_compared_to_current_list.number_of_urls_in_urllist]) }}
                    </template>
                    <template v-if="!differences_compared_to_current_list.both_are_equal">
                        ⚠️ {{ $t("differences_compared_to_current_list.not_equal") }}
                        <template v-if="differences_compared_to_current_list.number_of_urls_in_urllist === differences_compared_to_current_list.number_of_urls_in_report">
                            {{ $t("differences_compared_to_current_list.both_list_contain_n_urls", [differences_compared_to_current_list.number_of_urls_in_urllist]) }}
                        </template>
                        <template v-if="differences_compared_to_current_list.number_of_urls_in_urllist !== differences_compared_to_current_list.number_of_urls_in_report">
                            {{ $t("differences_compared_to_current_list.report_contains_n_urllist_contains_n", [differences_compared_to_current_list.number_of_urls_in_report, differences_compared_to_current_list.number_of_urls_in_urllist]) }}
                        </template>
                        <template v-if="differences_compared_to_current_list.in_report_but_not_in_urllist !== ''">
                            {{ $t("differences_compared_to_current_list.in_report_but_not_in_urllist") }}: {{ differences_compared_to_current_list.in_report_but_not_in_urllist }}.
                        </template>
                        <template v-if="differences_compared_to_current_list.in_urllist_but_not_in_report !== ''">
                            {{ $t("differences_compared_to_current_list.in_urllist_but_not_in_report") }}: {{ differences_compared_to_current_list.in_urllist_but_not_in_report }}.
                        </template>
                    </template>
                </p>

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
                            <li><span class="faq-test category_error"><span class="visuallyhidden">{{ $t("report.results.category_error_in_test") }}</span>{{ $t("icon_legend.category_error_in_test") }}</span></li>
                        </ul>
                        <h3>{{ $t("icon_legend.subtest_title") }}</h3>
                        <ul>
                            <li><span class="faq-subtest passed"><span class="visuallyhidden">{{ $t("report.results.passed") }}</span>{{ $t("icon_legend.subtest_good") }}</span></li>
                            <li><span class="faq-subtest failed"><span class="visuallyhidden">{{ $t("report.results.failed") }}</span>{{ $t("icon_legend.subtest_bad") }}</span></li>
                            <li><span class="faq-subtest warning"><span class="visuallyhidden">{{ $t("report.results.warning") }}</span>{{ $t("icon_legend.subtest_warning") }}</span></li>
                            <li><span class="faq-subtest info"><span class="visuallyhidden">{{ $t("report.results.info") }}</span>{{ $t("icon_legend.subtest_info") }}</span></li>
                            <li><span class="faq-test not_tested"><span class="visuallyhidden">{{ $t("report.results.not_tested") }}</span>{{ $t("icon_legend.subtest_not_tested") }}</span></li>
                            <li><span class="faq-test error_in_test"><span class="visuallyhidden">{{ $t("report.results.error_in_test") }}</span>{{ $t("icon_legend.subtest_error_in_test") }}</span></li>
                        </ul>
                    </div>
                </div>

                <div class="sticky-table-container" style="position: relative; page-break-before: always;">
                    <div id="horrible-chrome-td-sticky-white-background-fix"></div>
                    <table class="table table-striped">
                        <thead class="sticky_labels">

                            <tr class="sticky_labels">
                                <th style="width: 75px; min-width: 75px; border: 0; background-color: white;" class="sticky-header">
                                    <div class="rotate">
                                        <span @click="sortBy('score')" class="arrow" :class="sortOrders['score'] === -1 ? 'dsc' : (sortOrders['score'] === 1 ? 'asc' : 'unknown')"></span>
                                        <span @click="sortBy('score')">{{ $t("score") }}</span>
                                    </div>
                                </th>
                                <th style="width: 225px; min-width: 225px; border: 0; background-color: white;" class="sticky-header">
                                    <div class="rotate">
                                        <div @click="sortBy('url')" class="arrow" :class="sortOrders['url'] === -1 ? 'dsc' : (sortOrders['url'] === 1 ? 'asc' : 'unknown')"></div>
                                        <div @click="sortBy('url')" style="display: inline-block;">{{ $t("domain") }}</div>
                                    </div>
                                </th>

                                <th colspan="200" class="sticky-header" style="background-color: white;">
                                    <template v-if="['web', 'mail'].includes(selected_category)">

                                        <div style="border: 0; float: left; width: 100px" v-for="category in relevant_categories_based_on_settings">
                                            <div class="rotate">
                                                <span @click="sortBy(category)" class="arrow" :class="sortOrders[category] === -1 ? 'dsc' : (sortOrders[category] === 1 ? 'asc' : 'unknown')"></span>
                                                <span @click="sortBy(category)">{{ $t("" + category) }}</span>
                                            </div>
                                        </div>

                                    </template><template v-else>

                                         <div style="border: 0; float: left; width: 56px" v-for="category in relevant_categories_based_on_settings">
                                            <div class="rotate" style="white-space: nowrap;">
                                                <div @click="sortBy(category)" class="arrow" :class="sortOrders[category] === -1 ? 'dsc' : (sortOrders[category] === 1 ? 'asc' : 'unknown')"></div>
                                                <div @click="sortBy(category)" style="display: inline-block;">{{ $t("" + category) }}<div style="font-size: 0.7em; color: gray; margin-top: -3px; padding-left: 13px;" v-html="category_from_field_name(category)"></div></div>
                                            </div>
                                        </div>

                                    </template>

                                </th>

                            </tr>

                        </thead>

                        <tbody class="gridtable">
                            <template>
                                <!-- Zoom buttons for accessibility -->
                                <tr class="summaryrow">
                                    <td colspan="2" class="sticky_search">
                                        <label class="visuallyhidden" for="url_filter">{{ $t('report.url_filter') }}</label>
                                        <input v-if="selected_report" type="text" v-model="url_filter" id="url_filter" :placeholder="$t('report.url_filter')">
                                        <p class="visuallyhidden">{{ $t('report.zoom.explanation') }}</p>
                                    </td>
                                    <template v-if="['web', 'mail'].includes(selected_category)">
                                        <td style="width: 100px; min-width: 100px;" v-for="category_name in relevant_categories_based_on_settings" class="sticky_search">
                                            <button @click="select_category(category_name)">{{ $t("report.zoom.buttons.zoom") }}
                                            <span class="visuallyhidden">{{ $t("report.zoom.buttons.zoom_in_on", [$t("" + category_name)]) }}</span>
                                            </button>
                                        </td>
                                        <td class="sticky_search" style="width: 100%"></td>
                                    </template>
                                    <template v-else>
                                        <td :colspan="relevant_categories_based_on_settings.length + 1" style="text-align: center" class="sticky_search">
                                            <button style='width: 100%' @click="select_category(selected_report.urllist_scan_type)">
                                                <span role="img" :aria-label="$t('icons.remove_filter')">❌</span> {{ $t("report.zoom.buttons.remove_zoom") }}
                                            </button><br>
                                            {{ $t("report.zoom.zoomed_in_on") }} {{ $t("" + selected_category) }}.
                                        </td>
                                    </template>

                                </tr>
                            </template>

                            <template v-if="!filtered_urls.length">
                                <tr>
                                    <td :colspan="relevant_categories_based_on_settings.length + 2" style="text-align: center;">😱 {{ $t("report.empty_report") }}</td>
                                </tr>
                            </template>
                            <template v-else>

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
                                    <template v-else>
                                        <td style="width: 75px; min-width: 75px;">
                                            <a class='direct_link_to_report' :href='url.endpoints[0].ratings_by_type.internet_nl_score.internet_nl_url' target="_blank">
                                                <img src="/static/images/vendor/internet_nl/favicon.png" style="height: 16px;"> {{url.endpoints[0].ratings_by_type.internet_nl_score.internet_nl_score}}%
                                                <span class="visuallyhidden">${this.$i18n.t('report.link_to_report', {'url': url})}</span>
                                            </a>
                                        </td>
                                        <td style="width: 225px; min-width: 225px;">{{url.url}}</td>
                                        <template v-if="['web', 'mail'].includes(selected_category)">
                                            <td class="testresultcell" style="width: 100px" v-for="category_name in relevant_categories_based_on_settings">
                                                <div v-html="category_value_with_comparison(category_name, url)"></div>
                                            </td>
                                        </template>
                                        <template v-else>
                                            <td class="testresultcell" style="width: 56px" v-for="category_name in relevant_categories_based_on_settings">
                                                <div v-html="detail_value_with_comparison(category_name, url)"></div>
                                            </td>
                                        </template>
                                        <td>

                                        </td>
                                    </template>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
        <!-- The dropdown with recent reports is updated automatically when scans finish. But if that page
         had never loaded, this is a fallback that still tries to get the recent report every ten minutes. -->
        <autorefresh :visible="false" :callback="get_recent_reports" :refresh_per_seconds="600"></autorefresh>
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
                    // todo: translation will be given.
                    category_error_in_test: "Error occured while testing ⇒ null score",
                    subtest_title: internet_nl_messages.en.internet_nl.faqs_report_subtest_title,
                    subtest_good: internet_nl_messages.en.internet_nl.faqs_report_subtest_good,
                    subtest_bad: internet_nl_messages.en.internet_nl.faqs_report_subtest_bad,
                    subtest_warning: internet_nl_messages.en.internet_nl.faqs_report_subtest_warning,
                    subtest_info: internet_nl_messages.en.internet_nl.faqs_report_subtest_info,
                    subtest_not_applicable: "Not applicable ⇒ no score impact",
                    subtest_not_tested: "Not tested ⇒ no score impact",
                    subtest_error_in_test: "Error occured while testing ⇒ null score",
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
                report: {
                    title: 'Report',
                    intro: 'This table shows detailed results per category. It is possible to compare this report to a second report. In that case, progress incidators are ' +
                        'added to the first report where applicable. The domains of the second report are only compared, not displayed.',
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
                        not_testable: "Untestable",
                        error_in_test: "Test error",
                        failed: "Failed",
                        warning: "Warning",
                        info: "Info",
                        passed: "Passed",
                        unknown: "Unknown",
                        comparison: {
                            neutral: "-",
                            improved: "Improved compared to the second report selected.",
                            regressed: "Regressed compared to the second report selected.",
                        }
                    }
                },
                download: {
                    title: 'Download metrics as a spreadsheet',
                    intro: 'Report data is available in the following formats:',
                    xlsx: 'Excel Spreadsheet (Microsoft Office), .xlsx',
                    ods: 'Open Document Spreadsheet (Libre Office), .ods',
                    csv: 'Comma Separated (for programmers), .csv',
                },
                settings: {
                    title: 'Select visible metrics',
                    main_category: "Average adoption of standards",
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
                not_testable: 'Untestable',
                not_applicable: 'Not applicable',
                error_in_test: "Test error",

                // legacy values
                mail_legacy: 'Extra Fields',
                web_legacy: 'Extra Fields',

                differences_compared_to_current_list: {
                    equal: "The domains in this report are equal to the domains in the associated list of domains.",
                    not_equal: "The domains in this report differ from the domains in the associated list of domains.",
                    both_list_contain_n_urls: "Both the report and the associated list of domains contain {0} domains.",
                    report_contains_n_urllist_contains_n: "This report contains {0} domains, while the associated list contains {1}.",
                    in_report_but_not_in_urllist: "Domains in this report, but not in the list",
                    in_urllist_but_not_in_report: "Domains not in this report"
                },
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

                score: "Score",
                domain: "Domein",

                check: "Selecteer alle",
                uncheck: "Deselecteer alle",

                icon_legend: {
                    title: "Legenda van gebruikte pictogrammen",

                    // this has been placed here, because not_applicable and not_testable reuse icons and have
                    // a different meaning. That translation is not available in internet.nl
                    test_title: internet_nl_messages.nl.internet_nl.faqs_report_test_title,
                    test_good: internet_nl_messages.nl.internet_nl.faqs_report_test_good,
                    test_bad: internet_nl_messages.nl.internet_nl.faqs_report_test_bad,
                    test_warning: internet_nl_messages.nl.internet_nl.faqs_report_test_warning,
                    category_error_in_test: "Fout in test ⇒ nulscore",
                    test_info: internet_nl_messages.nl.internet_nl.faqs_report_test_info,
                    subtest_title: internet_nl_messages.nl.internet_nl.faqs_report_subtest_title,
                    subtest_good: internet_nl_messages.nl.internet_nl.faqs_report_subtest_good,
                    subtest_bad: internet_nl_messages.nl.internet_nl.faqs_report_subtest_bad,
                    subtest_warning: internet_nl_messages.nl.internet_nl.faqs_report_subtest_warning,
                    subtest_info: internet_nl_messages.nl.internet_nl.faqs_report_subtest_info,
                    subtest_not_tested:  "Niet getest ⇒ geen score impact",
                    subtest_error_in_test: "Fout in test ⇒ nulscore",
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


                report: {
                    title: 'Rapport',
                    intro: 'Deze tabel toont de details van het rapport. Het is mogelijk dit rapport te vergelijken met een vorig of ander rapport. Wanneer deze vergelijking' +
                        ' wordt gemaakt, wordt bij de gegevens van het eerste rapport voortgangsindicatoren geplaats waar relevant. De domeinen van het tweede rapport worden alleen vergeleken, niet getoond.',
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
                        not_testable: "Ontestbaar",
                        error_in_test: "Testfout",
                        failed: "Niet goed",
                        warning: "Waarschuwing",
                        info: "Info",
                        passed: "Goed",
                        unknown: "Onbekend",
                        comparison: {
                            neutral: "-",
                            improved: "Verbeterd vergeleken met het 2e geselecteerde rapport.",
                            regressed: "Verslechterd vergeleken met het 2e geselecteerde rapport.",
                        }
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
                    main_category: "Adoptie van standaarden",
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
                mail_legacy: 'Extra Velden',
                web_legacy: 'Extra Velden',

                differences_compared_to_current_list: {
                    equal: "Domeinen in dit rapport zijn gelijk aan de domeinen in de bijbehorende lijst.",
                    not_equal: "Domeinen in dit rapport wijken af van de domeinen in de bijbehorende lijst.",
                    both_list_contain_n_urls: "Zowel de rapportage als de bijbehorende lijst bevatten {0} domeinen.",
                    report_contains_n_urllist_contains_n: "Deze rapportage bevat {0} domeinen terwijl de bijbehorende lijst {1} domeinen bevat.",
                    in_report_but_not_in_urllist: "Domeinen in het rapport, maar niet in de bijbehorende lijst",
                    in_urllist_but_not_in_report: "Domeinen niet in het rapport"
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
    template: '#report_template',
    mixins: [humanize_mixin, http_mixin],
    data: function() {
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
                internet_nl_web_appsecpriv: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},  // Added 24th of May 2019

                mail: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                mail_legacy: {visible: false, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_mail_dashboard_tls: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_mail_dashboard_auth: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_mail_dashboard_dnssec: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},
                internet_nl_mail_dashboard_ipv6: {visible: true, show_dynamic_average: true, only_show_dynamic_average: false},

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
                category_web_security_options_appsecpriv: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_forum_standardisation_magazine: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_forum_standardisation_ipv6_monitor: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_web_forum_standardisation_status_fields: {show_dynamic_average: true, only_show_dynamic_average: false},

                category_mail_ipv6_name_servers: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_ipv6_mail_servers: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dnssec_email_address_domain: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dnssec_mail_server_domain: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_auth_dmarc: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_aut_dkim: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_dashboard_aut_spf: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_tls: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_certificate: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_starttls_dane: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_forum_standardisation_magazine: {show_dynamic_average: true, only_show_dynamic_average: false},
                category_mail_forum_standardisation_ipv6_monitor: {show_dynamic_average: true, only_show_dynamic_average: false},

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
                internet_nl_web_https_tls_keyexchangehash: {visible: true},
                internet_nl_web_https_tls_ocsp: {visible: true},
                internet_nl_web_https_tls_0rtt: {visible: true},
                internet_nl_web_https_tls_cipherorder: {visible: true},
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

                // added in 2.0:
                internet_nl_mail_starttls_tls_cipherorder: {visible: false},
                internet_nl_mail_starttls_tls_keyexchangehash: {visible: false},
                internet_nl_mail_starttls_tls_0rtt: {visible: false},

                internet_nl_web_legacy_tls_1_3: {visible: false},
                internet_nl_mail_legacy_mail_non_sending_domain: {visible: false},
                internet_nl_mail_legacy_mail_server_testable: {visible: false},
                internet_nl_mail_legacy_mail_server_reachable: {visible: false},
                internet_nl_mail_legacy_domain_has_mx: {visible: false},
                internet_nl_mail_legacy_tls_1_3: {visible: false},

                internet_nl_mail_legacy_category_ipv6: {visible: false},
                internet_nl_web_legacy_category_ipv6: {visible: false},
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
            selected_report: [],


            // show category headers in table only when there is a change of categeory:
            previous_category: "",


            compare_charts: [],
            compare_oldest_data: "",
            older_data_available: true,

            // simple sorting a la bootstrapvue.
            sortKey: 'url',
            sortOrders: {'url': 1},
        }
    },
    mounted: function(){

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

        category_value_with_comparison: function(category_name, url){
            let verdicts = url.endpoints[0].ratings_by_type[category_name];
            let simple_value = this.category_verdict_to_simple_value(verdicts, category_name);

            if (this.compare_charts.length < 2 || this.compare_charts[1].calculation.urls_by_url[url.url] === undefined)
                return `<span class="category_${simple_value}">${simple_value}</span>`;

            // in case there is no endpoint (exceptional case)
            if (this.compare_charts[1].calculation.urls_by_url[url.url].endpoints[0] === undefined)
                return `<span class="category_${simple_value}">${simple_value}</span>`;

            let other_verdicts = this.compare_charts[1].calculation.urls_by_url[url.url].endpoints[0].ratings_by_type[category_name];
            let other_simple_value = this.category_verdict_to_simple_value(other_verdicts, category_name);

            let progression = {'passed': 4, 'warning': 3, 'info': 2, 'failed': 1};
            let comparison_verdict = "";

            if (simple_value === other_simple_value || simple_value === "unknown" || other_simple_value === "unknown")
                comparison_verdict = "neutral";
            else {
                if (progression[simple_value] > progression[other_simple_value]){
                    comparison_verdict = "improved";
                } else {
                    comparison_verdict = "regressed";
                }
            }

            let comparison_text = this.$i18n.t("report.results.comparison." + comparison_verdict);

            return `<span class="category_${simple_value} compared_with_next_report_${comparison_verdict}">${comparison_text} ${simple_value}</span>`
        },

        category_verdict_to_simple_value: function(verdict, category_name) {
            if (verdict === undefined)
                return "unknown";

            // Internet.nl API V2.0:
            if (verdict.test_result !== undefined) {
                return verdict.test_result;
            }

            // backwards compatible with API v1.0 reports:
            if (verdict.ok > 0) {return 'passed'}
            if (verdict.ok < 1) {
                if (category_name === 'internet_nl_web_appsecpriv'){
                    return "warning";
                }
                return "failed"
            }

        },

        detail_value_with_comparison: function(category_name, url){
            /**
             * This function is called numerous times. It has been optimzed in the following ways:
             * - Translations have been removed, saving 1 second for (500 * 16) = 8000 metrics.
             * - values are precalculated: simple_value, simple_progression, score etc...
             * */

            let verdicts = url.endpoints[0].ratings_by_type[category_name];
            let simple_value = "";
            let simple_progression = "";

            // Adding the verdict to the report would speed things up...
            if (verdicts === undefined) {
                simple_value = "unknown";
                simple_progression = "unknown";
            } else {
                if (verdicts.test_result !== undefined)
                    // API V2.0:
                    simple_value = verdicts.test_result;  // error, not_testable, failed, warning, info, passed
                else
                    // API V1.0
                    simple_value = verdicts.simple_verdict;
                simple_progression = verdicts.simple_progression;
            }
            /* disabling translations saves a second on 500 urls and the TLS page.
            report_result_string = this.$i18n.t("report.results." + simple_value);

            if (["failed", "warning", "info"].includes(simple_value)) {
                category_name_verdict = this.$i18n.t('' + category_name + '_verdict_bad')
            }

            if (simple_value === "passed"){
                category_name_verdict = this.$i18n.t('' + category_name + '_verdict_good')
            }
            */

            // If we're not in comparison mode, just return the value.
            // a template string litteral is slower than just an ordinary string that will be parsen by the browser...
            // https://jsperf.com/es6-string-literals-vs-string-concatenation
            if (this.compare_charts.length < 2)
                return "<span class='" + simple_value + "'>" + simple_value + "</span>";

            // if we _are_ comparing, but the comparison is empty because there is nothing to compare to:
            // This is done separately to prevent another call to something undefined
            if (this.compare_charts[1].calculation.urls_by_url[url.url] === undefined)
                return `<span class="${simple_value}">${simple_value}</span>`;

            // in case there is no endpoint (exceptional case)
            if (this.compare_charts[1].calculation.urls_by_url[url.url].endpoints[0] === undefined)
                return `<span class="${simple_value}">${simple_value}</span>`;

            /*
            * This compares if the new value is progressive, neutral or regressive.
            * All to/from not_testable and not_applicable is neutral.
            * From good to worst: passed, info, warning, failed.
            *
            * Possible values are: not_applicable, not_testable, failed, warning, info, passed
            * */

            // older, previous...
            let other_verdicts = this.compare_charts[1].calculation.urls_by_url[url.url].endpoints[0].ratings_by_type[category_name];
            let other_simple_value = "";
            let other_simple_progression = "";

            if (other_verdicts === undefined) {
                other_simple_value = "unknown";
                other_simple_progression = "unknown";
            } else {
                if (other_verdicts.test_result !== undefined)
                    // API V2.0:
                    other_simple_value = other_verdicts.test_result;  // error_in_test, not_testable, failed, warning, info, passed
                else
                    // API V1.0
                    other_simple_value = other_verdicts.simple_verdict;
                other_simple_progression = other_verdicts.simple_progression;
            }

            let comparison_verdict = "";

            // all to and from not_tested or not_applicable is neutral, also going to the same state is neutral
            if (simple_value === other_simple_value)
                comparison_verdict = "neutral";

            const neutral_values = ["unknown", "not_applicable", "not_testable", 'no_mx', 'unreachable', 'error_in_test', 'error'];

            if (neutral_values.includes(simple_value) || neutral_values.includes(other_simple_value))
                comparison_verdict = "neutral";

            if (comparison_verdict === "") {
                if (simple_progression > other_simple_progression)
                    comparison_verdict = "improved";
                else
                    comparison_verdict = "regressed";
            }

            let comparison_text = this.$i18n.t("report.results.comparison." + comparison_verdict);
            return `<span class="${simple_value} compared_with_next_report_${comparison_verdict}">${comparison_text} ${simple_value}</span>`
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
            // You'll notice a load time at a random point in this function, this means Vue is processing the response.
            fetch(`/data/report/get/${report_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.reports = data;
                this.selected_category = this.selected_report[0].urllist_scan_type;

                this.original_urls = data[0].calculation.urls.sort(this.alphabet_sorting);
                this.older_data_available = true;

                // sort urls alphabetically
                // we'll probably just need a table control that does sorting, filtering and such instead of coding it ourselves.
                this.filtered_urls = this.order_urls(data[0].calculation.urls);
                // this.get_timeline();

                // we already have the first report, so don't request it again.
                // note that when setting the first chart, the subsequent updates do not "point ot a new object"
                // so a state change doesn not happen automatically using a wathcer, you have to watch deep.
                // console.log(`First compare chart set...`);
                this.$set(this.compare_charts, 0, data[0]);
                // this.compare_charts.$set(0, );

                this.is_loading = false;

                // new accordions are created, reduce their size.
                this.$nextTick(() => {accordinate(); this.$forceUpdate()});
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});

            fetch(`/data/report/differences_compared_to_current_list/${report_id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.differences_compared_to_current_list = data;
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
                    // Get all possible issue fields before overwriting them with whatever is stored.
                    const all_possible_fields = Object.keys(this.issue_filters);

                    // now overwrite with the custom settings
                    this.issue_filters = data.data;

                    // upgrade the saved issue filters with all fields we know. In case of missing fields, those will
                    // be added with a default value (invisible).
                    all_possible_fields.forEach((field_name) => {
                        this.upgrade_issue_filter_with_new_field(field_name);
                    })
                }
            });
        },


        upgrade_issue_filter_with_new_field: function(field_name){
            if (!Object.keys(this.issue_filters).includes(field_name)) {

                // web and mail and default categories are always visible by default.: otherwise we'd never see any categories when this data is malformed.
                // in totally empty data, all fields are invisble, which is ok.
                if (["web", "mail",

                    // default visible catagories
                    "internet_nl_web_ipv6", "internet_nl_web_dnssec", "internet_nl_web_tls",
                    "internet_nl_web_appsecpriv", "internet_nl_mail_dashboard_ipv6",
                    "internet_nl_mail_dashboard_dnssec", "internet_nl_mail_dashboard_auth",
                    "internet_nl_mail_dashboard_tls",

                    // fields visible by default;
                    "internet_nl_web_https_cert_domain", "internet_nl_web_https_http_redirect",
                    "internet_nl_web_https_cert_chain", "internet_nl_web_https_tls_version",
                    "internet_nl_web_https_tls_clientreneg", "internet_nl_web_https_tls_ciphers",
                    "internet_nl_web_https_http_available", "internet_nl_web_https_dane_exist",
                    "internet_nl_web_https_http_compress", "internet_nl_web_https_http_hsts",
                    "internet_nl_web_https_tls_secreneg", "internet_nl_web_https_dane_valid",
                    "internet_nl_web_https_cert_pubkey", "internet_nl_web_https_cert_sig",
                    "internet_nl_web_https_tls_compress", "internet_nl_web_https_tls_keyexchange",
                    "internet_nl_web_https_tls_keyexchangehash", "internet_nl_web_https_tls_ocsp",
                    "internet_nl_web_https_tls_0rtt", "internet_nl_web_https_tls_cipherorder",
                    "internet_nl_web_dnssec_valid", "internet_nl_web_dnssec_exist", "internet_nl_web_ipv6_ws_similar",
                    "internet_nl_web_ipv6_ws_address", "internet_nl_web_ipv6_ns_reach", "internet_nl_web_ipv6_ws_reach",
                    "internet_nl_web_ipv6_ns_address", "internet_nl_mail_starttls_cert_domain",
                    "internet_nl_mail_starttls_tls_version", "internet_nl_mail_starttls_cert_chain",
                    "internet_nl_mail_starttls_tls_available", "internet_nl_mail_starttls_tls_clientreneg",
                    "internet_nl_mail_starttls_tls_ciphers", "internet_nl_mail_starttls_dane_valid",
                    "internet_nl_mail_starttls_dane_exist", "internet_nl_mail_starttls_tls_secreneg",
                    "internet_nl_mail_starttls_dane_rollover", "internet_nl_mail_starttls_cert_pubkey",
                    "internet_nl_mail_starttls_cert_sig", "internet_nl_mail_starttls_tls_compress",
                    "internet_nl_mail_starttls_tls_keyexchange", "internet_nl_mail_auth_dmarc_policy",
                    "internet_nl_mail_auth_dmarc_exist", "internet_nl_mail_auth_spf_policy",
                    "internet_nl_mail_auth_dkim_exist", "internet_nl_mail_auth_spf_exist",
                    "internet_nl_mail_dnssec_mailto_exist", "internet_nl_mail_dnssec_mailto_valid",
                    "internet_nl_mail_dnssec_mx_valid", "internet_nl_mail_dnssec_mx_exist",
                    "internet_nl_mail_ipv6_mx_address", "internet_nl_mail_ipv6_mx_reach",
                    "internet_nl_mail_ipv6_ns_reach", "internet_nl_mail_ipv6_ns_address",
                    "internet_nl_web_appsecpriv_csp", "internet_nl_web_appsecpriv_referrer_policy",
                    "internet_nl_web_appsecpriv_x_content_type_options", "internet_nl_web_appsecpriv_x_frame_options",
                    "internet_nl_web_appsecpriv_x_xss_protection",

                ].includes(field_name)){
                    this.issue_filters[field_name] = {
                        visible: true,
                        show_dynamic_average: true,
                        only_show_dynamic_average: false
                    }
                } else {
                    // this is invisible because we don't want to tamper with existing settings when introducing new
                    // fields. Users will have to enable it themselves.
                    this.issue_filters[field_name] = {
                        visible: false,
                        show_dynamic_average: true,
                        only_show_dynamic_average: false
                    }
                }
            }
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
                data = data.slice().sort(function (a, b) {

                    // deal with urls without endpoints:
                    if (a.endpoints.length === 0){
                        return -1 * order;
                    }

                    if (b.endpoints.length === 0){
                        return 1 * order;
                    }

                    a = a.endpoints[0].ratings_by_type["internet_nl_score"].internet_nl_score;
                    b = b.endpoints[0].ratings_by_type["internet_nl_score"].internet_nl_score;
                    return (a === b ? 0 : a > b ? 1 : -1) * order;
                });

                return data;
            }
            data = data.slice().sort(function (a, b) {
                // for everything that is not the url name itself, is neatly tucked away. Only filter on high? Or on what kind of structure?

                // deal with urls without endpoints:
                if (a.endpoints.length === 0){
                    return -1 * order;
                }

                if (b.endpoints.length === 0){
                    return 1 * order;
                }

                let aref = a.endpoints[0].ratings_by_type[sortKey];
                let bref = b.endpoints[0].ratings_by_type[sortKey];

                // When switching reports (mail, web) some sort keys might not exist. In that case return 0 to not
                // influence sorting:
                if (aref === undefined)
                    return 0;

                a = aref.simple_progression;
                b = bref.simple_progression;
                return (a === b ? 0 : a > b ? 1 : -1) * order
            });

            return data;
        },
        all_field_names_from_categories(categories){
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
        all_subcategory_fields_from_category(category_name){
            let fields = [];

            let i = 0;
            // hack to get the right stuff from the scan methods. Should be done differently.
            if (this.selected_category === 'mail')
                i = 1;


            this.scan_methods[i].categories.forEach((category) => {

                if (category.key !== category_name.key){
                    return
                }

                category.categories.forEach((subcategory) => {
                    subcategory.fields.forEach((field) => {
                        fields.push(field.name);
                    });
                    subcategory.additional_fields.forEach((field) => {
                        fields.push(field.name);
                    });
                });

            });

            return fields;
        },

        category_from_field_name: function(field_name){
            return this.field_name_to_category_names[field_name];
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
        },

        visible_metrics_see_if_category_is_relevant: function(category_name) {
            // if all fields in the category are deselected, deselect the category, otherwise, select it.

            let fields = this.all_subcategory_fields_from_category(category_name);

            let should_be_visible = false;
            for (let i=0; i< fields.length; i++){

                // alerting if fields are missing:
                if (this.issue_filters[fields[i]] === undefined){
                    console.log(`Missing field ${fields[i]} in issue filters.`)
                }

                if (this.issue_filters[fields[i]].visible){
                    should_be_visible = true;
                    break;
                }
            }

            this.issue_filters[category_name.key].visible = should_be_visible;
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
            // when multiple items are selected, the old value is always 1 item, the new one is always 2 items.
            // as such it is not possible to determine reload without trickery safely...

            /* console.log(`New value: ${new_value}`);
            console.log(new_value);
            console.log(`Old value: ${old_value}`);
            console.log(old_value);*/

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
        amount_of_finished_scans: function(new_value, old_value) {
            // If there are more scans finished, this list is updated.
            if (new_value === old_value)
                return;

            this.get_recent_reports();
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
                                    name: 'Name servers',
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
                                    name: 'Web server',
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
                                    name: 'DNSSEC',
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
                                    name: 'HTTP',
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
                                    name: 'TLS',
                                    key: 'category_web_tls_tls',
                                    label: internet_nl_messages[language].internet_nl.results_domain_tls_tls_label,
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
                                    additional_fields: [],
                                },
                                {
                                    name: 'Certificate',
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
                                    name: 'DANE',
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
                                    name: 'Baseline NL Government',
                                    key: 'category_web_forum_standardisation_magazine',
                                    label: 'Baseline NL Government',
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
                                        {name: 'internet_nl_web_legacy_category_ipv6',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_web_legacy_ipv6_nameserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_web_legacy_ipv6_webserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_ipv6_webserver_explanation'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'Status Fields',
                                    key: 'category_web_forum_standardisation_status_fields',
                                    label: i18n.t('fields.forum_standardistation.status_fields'),
                                    fields: [
                                        {name: 'internet_nl_web_legacy_tls_1_3',
                                        explanation: 'fields.forum_standardistation.internet_nl_web_legacy_tls_1_3_explanation'},
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
                                    name: 'Email address domain',
                                    key: 'category_mail_dnssec_email_address_domain',
                                    label: internet_nl_messages[language].internet_nl.results_mail_dnssec_domain_label,
                                    fields: [
                                        {name: 'internet_nl_mail_dnssec_mailto_exist'},
                                        {name: 'internet_nl_mail_dnssec_mailto_valid'},
                                    ],
                                    additional_fields: [],
                                },
                                {
                                    name: 'Mail server domain(s)',
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
                                        {name: 'internet_nl_mail_starttls_tls_cipherorder'},
                                        {name: 'internet_nl_mail_starttls_tls_keyexchange'},
                                        {name: 'internet_nl_mail_starttls_tls_keyexchangehash'},
                                        {name: 'internet_nl_mail_starttls_tls_compress'},
                                        {name: 'internet_nl_mail_starttls_tls_secreneg'},
                                        {name: 'internet_nl_mail_starttls_tls_clientreneg'},
                                        {name: 'internet_nl_mail_starttls_tls_0rtt'},
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
                                    name: 'Baseline NL Government',
                                    label: 'Baseline NL Government',
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
                                        {name: 'internet_nl_mail_legacy_category_ipv6',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_category_explanation'},
                                        {name: 'internet_nl_mail_legacy_ipv6_nameserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_nameserver_explanation'},
                                        {name: 'internet_nl_mail_legacy_ipv6_mailserver',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_ipv6_mailserver_explanation'},

                                    ],
                                    additional_fields: [],
                                },

                                {
                                    name: 'Status Fields',
                                    key: 'category_web_forum_standardisation_status_fields',
                                    label: i18n.t('fields.forum_standardistation.status_fields'),
                                    fields: [
                                        {name: 'internet_nl_mail_legacy_tls_1_3',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_tls_1_3_explanation'},
                                        {name: 'internet_nl_mail_legacy_domain_has_mx',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_domain_has_mx_explanation'},
                                        {name: 'internet_nl_mail_legacy_mail_server_reachable',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_server_reachable_explanation'},
                                        {name: 'internet_nl_mail_legacy_mail_server_testable',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_server_testable_explanation'},
                                        {name: 'internet_nl_mail_legacy_mail_non_sending_domain',
                                        explanation: 'fields.forum_standardistation.internet_nl_mail_legacy_mail_non_sending_domain_explanation'},
                                    ],
                                    additional_fields: [],
                                }
                            ]
                        }
                    ]
                }
            ];
        },

        field_name_to_category_names: function(){
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
                    subcategory.additional_fields.forEach((field) => {
                        fields_mapping[field.name] = subcategory.name;
                    });
                });
            });

            this.scan_methods[1].categories.forEach((category) => {

                category.categories.forEach((subcategory) => {
                    subcategory.fields.forEach((field) => {
                        fields_mapping[field.name] = subcategory.name;
                    });
                    subcategory.additional_fields.forEach((field) => {
                        fields_mapping[field.name] = subcategory.name;
                    });
                });
            });

            return fields_mapping;
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

        amount_of_finished_scans: function() {
            // this helps auto-reloading the list of available reports

            // In the case no scans
            if (store.state.scan_monitor_data.length === 0)
                return 0;

            let finished = 0;
            // the first scan-monitor record where list_id is the same, is the one with the most recent state
            for(let i = 0; i < store.state.scan_monitor_data.length; i++) {
                if (store.state.scan_monitor_data[i].state === "finished") {
                    finished++;
                }
            }

            return finished;
        }

    }

});
</script>
