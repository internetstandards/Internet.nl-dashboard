<template>
    <div>
        <h2>{{ $t("report.title") }}</h2>
        <a class="anchor" name="report"></a>
        <p>{{ $t("report.intro") }}</p>

        <p v-if="differences_compared_to_current_list">
            <template v-if="differences_compared_to_current_list.both_are_equal">
                {{ $t("differences_compared_to_current_list.equal") }}
                {{
                    $t("differences_compared_to_current_list.both_list_contain_n_urls", [differences_compared_to_current_list.number_of_urls_in_urllist])
                }}
            </template>
            <template v-if="!differences_compared_to_current_list.both_are_equal">
                ⚠️ {{ $t("differences_compared_to_current_list.not_equal") }}
                <template
                    v-if="differences_compared_to_current_list.number_of_urls_in_urllist === differences_compared_to_current_list.number_of_urls_in_report">
                    {{
                        $t("differences_compared_to_current_list.both_list_contain_n_urls", [differences_compared_to_current_list.number_of_urls_in_urllist])
                    }}
                </template>
                <template
                    v-if="differences_compared_to_current_list.number_of_urls_in_urllist !== differences_compared_to_current_list.number_of_urls_in_report">
                    {{
                        $t("differences_compared_to_current_list.report_contains_n_urllist_contains_n", [differences_compared_to_current_list.number_of_urls_in_report, differences_compared_to_current_list.number_of_urls_in_urllist])
                    }}
                </template>
                <template v-if="differences_compared_to_current_list.in_report_but_not_in_urllist !== ''">
                    {{ $t("differences_compared_to_current_list.in_report_but_not_in_urllist") }}:
                    {{ differences_compared_to_current_list.in_report_but_not_in_urllist }}.
                </template>
                <template v-if="differences_compared_to_current_list.in_urllist_but_not_in_report !== ''">
                    {{ $t("differences_compared_to_current_list.in_urllist_but_not_in_report") }}:
                    {{ differences_compared_to_current_list.in_urllist_but_not_in_report }}.
                </template>
            </template>
        </p>

        <collapse-panel :title='$t("icon_legend.title")' class="do-not-print">
            <div slot="content">
                <h3>{{ $t("test_title") }}</h3>
                <ul>
                    <li><span class="faq-test category_passed"><span
                        class="visuallyhidden">{{ $t("report.results.passed") }}</span>{{ $t("test_good") }}</span></li>
                    <li><span class="faq-test category_failed">
                        <span class="visuallyhidden">{{ $t("report.results.failed") }}</span>{{ $t("test_bad") }}</span>
                    </li>
                    <li><span class="faq-test category_warning"><span class="visuallyhidden">{{
                            $t("report.results.warning")
                        }}</span>{{ $t("test_warning") }}</span></li>
                    <li><span class="faq-test category_error"><span class="visuallyhidden">{{
                            $t("report.results.category_error_in_test")
                        }}</span>{{ $t("icon_legend.category_error_in_test") }}</span></li>
                </ul>
                <h3>{{ $t("subtest_title") }}</h3>
                <ul>
                    <li><span class="faq-subtest passed"><span class="visuallyhidden">{{
                            $t("report.results.passed")
                        }}</span>{{ $t("subtest_good") }}</span></li>
                    <li><span class="faq-subtest failed"><span class="visuallyhidden">{{
                            $t("report.results.failed")
                        }}</span>{{ $t("subtest_bad") }}</span></li>
                    <li><span class="faq-subtest warning"><span class="visuallyhidden">{{
                            $t("report.results.warning")
                        }}</span>{{ $t("subtest_warning") }}</span></li>
                    <li><span class="faq-subtest info"><span class="visuallyhidden">{{
                            $t("report.results.info")
                        }}</span>{{ $t("subtest_info") }}</span></li>
                    <li><span class="faq-test not_tested"><span class="visuallyhidden">{{
                            $t("report.results.not_tested")
                        }}</span>{{ $t("icon_legend.subtest_not_tested") }}</span></li>
                    <li><span class="faq-test error_in_test"><span class="visuallyhidden">{{
                            $t("report.results.error_in_test")
                        }}</span>{{ $t("icon_legend.subtest_error_in_test") }}</span></li>
                </ul>
            </div>
        </collapse-panel>

        <div class="sticky-table-container" style="position: relative; page-break-before: always;">
            <div id="horrible-chrome-td-sticky-white-background-fix"></div>
            <table class="table table-striped">
                <thead class="sticky_labels">

                <tr class="sticky_labels">
                    <th style="width: 78px; min-width: 78px; border: 0; background-color: white;"
                        class="sticky-header">
                        <div class="rotate">
                                    <span @click="sortBy('score')" class="arrow"
                                          :class="sortOrders['score'] === -1 ? 'dsc' : (sortOrders['score'] === 1 ? 'asc' : 'unknown')"></span>
                            <span @click="sortBy('score')">{{ $t("score") }}</span>
                        </div>
                    </th>
                    <th style="width: 225px; min-width: 225px; border: 0; background-color: white;"
                        class="sticky-header">
                        <div class="rotate">
                            <div @click="sortBy('url')" class="arrow"
                                 :class="sortOrders['url'] === -1 ? 'dsc' : (sortOrders['url'] === 1 ? 'asc' : 'unknown')"></div>
                            <div @click="sortBy('url')" style="display: inline-block;">{{ $t("domain") }}</div>
                        </div>
                    </th>

                    <th colspan="200" class="sticky-header" style="background-color: white;">
                        <template v-if="['web', 'mail'].includes(selected_category)">

                            <div style="border: 0; float: left; width: 100px"
                                 v-for="category in relevant_categories_based_on_settings" :key="category">
                                <div class="rotate">
                                            <span @click="sortBy(category)" class="arrow"
                                                  :class="sortOrders[category] === -1 ? 'dsc' : (sortOrders[category] === 1 ? 'asc' : 'unknown')"></span>
                                    <span @click="sortBy(category)">{{ $t("" + category) }}</span>
                                </div>
                            </div>

                        </template>
                        <template v-else>

                            <div style="border: 0; float: left; width: 56px"
                                 v-for="category in relevant_categories_based_on_settings" :key="category">
                                <div class="rotate" style="white-space: nowrap;">
                                    <div @click="sortBy(category)" class="arrow"
                                         :class="sortOrders[category] === -1 ? 'dsc' : (sortOrders[category] === 1 ? 'asc' : 'unknown')"></div>
                                    <div @click="sortBy(category)" style="display: inline-block;">
                                        {{ $t("" + category) }}
                                        <div
                                            style="font-size: 0.7em; color: gray; margin-top: -3px; padding-left: 13px;"
                                            v-html="category_from_field_name(category)"></div>
                                    </div>
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
                            <input type="text" v-model="url_filter" id="url_filter"
                                   :placeholder="$t('report.url_filter')">
                            <p class="visuallyhidden">{{ $t('report.zoom.explanation') }}</p>
                        </td>
                        <template v-if="['web', 'mail'].includes(selected_category)">
                            <td style="width: 100px; min-width: 100px;"
                                v-for="category_name in relevant_categories_based_on_settings"
                                class="sticky_search" :key="category_name">
                                <button @click="select_category(category_name)">
                                    {{ $t("report.zoom.buttons.zoom") }}
                                    <span class="visuallyhidden">{{
                                            $t("report.zoom.buttons.zoom_in_on", [$t("" + category_name)])
                                        }}</span>
                                </button>
                            </td>
                            <td class="sticky_search" style="width: 100%"></td>
                        </template>
                        <template v-else>
                            <td :colspan="relevant_categories_based_on_settings.length + 1"
                                style="text-align: center" class="sticky_search">
                                <button style='width: 100%'
                                        @click="select_category(report_category)">
                                    <span role="img" :aria-label="$t('icons.remove_filter')">❌</span>
                                    {{ $t("report.zoom.buttons.remove_zoom") }}
                                </button>
                                <br>
                                {{ $t("report.zoom.zoomed_in_on") }} {{ $t("" + selected_category) }}.
                            </td>
                        </template>

                    </tr>
                </template>

                <template v-if="filtered_urls.length < 1">
                    <tr>
                        <td :colspan="relevant_categories_based_on_settings.length + 2"
                            style="text-align: center;">😱 {{ $t("report.empty_report") }}
                        </td>
                    </tr>
                </template>
                <template v-else>

                    <tr v-for="url in filtered_urls" class="result_row" :key="url.url">
                        <template v-if="!url.endpoints.length">
                            <td>
                                -
                            </td>
                            <td>{{ url.url }}</td>
                            <td colspan="200">
                                <small>{{ $t('report.not_eligeble_for_scanning') }}</small>
                            </td>
                        </template>
                        <template v-else>
                            <td style="width: 78px; min-width: 78px;">
                                <a class='direct_link_to_report'
                                   :href='url.endpoints[0].ratings_by_type.internet_nl_score.internet_nl_url'
                                   target="_blank">
                                    <img src="/static/images/vendor/internet_nl/favicon.png"
                                         style="height: 16px;">
                                    {{ url.endpoints[0].ratings_by_type.internet_nl_score.internet_nl_score }}%
                                    <span
                                        class="visuallyhidden">${this.$i18n.t('report.link_to_report', {'url': url})}</span>
                                </a>
                            </td>
                            <td style="width: 225px; min-width: 225px;">{{ url.url }}</td>
                            <template v-if="['web', 'mail'].includes(selected_category)">
                                <td class="testresultcell" style="width: 100px"
                                    v-for="category_name in relevant_categories_based_on_settings"
                                    :key="category_name">
                                    <div v-html="category_value_with_comparison(category_name, url)"></div>
                                </td>
                            </template>
                            <template v-else>
                                <td class="testresultcell" style="width: 56px"
                                    v-for="category_name in relevant_categories_based_on_settings"
                                    :key="category_name">
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
</template>

<script>

import field_translations from './../field_translations'

export default {
    i18n: {
        sharedMessages: field_translations,
    },
    name: "ReportTable",
    props: {
        differences_compared_to_current_list: {
            type: Object
        },
        field_name_to_category_names: {type: Object, required: false},
        original_urls: {
            type: Array, required: true
        },
        report_category: {
            type: String
        },
        scan_methods: {
            type: Array
        },
        compare_charts: {
            type: Array,
            required: true
        },
    },
    data: function () {
        return {
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

            // simple sorting a la bootstrapvue.
            sortKey: 'url',
            sortOrders: {'url': 1},

            // this is the set of urls where filters are applied.
            filtered_urls: [],

            // url_filter allows the filtering of names in the list of urls.
            url_filter: '',

            // category selection with report category as fallback.
            selected_category: '',
        }
    },
    watch: {
        original_urls: function (new_value) {
            console.log('Setting original urls')
            this.filtered_urls = new_value;
            this.filter_urls();
        },
        url_filter: function (newValue) {
            this.filter_urls(newValue);
            // aside from debouncing not working, as it doesn't understand the vue context, it is not needed
            // up until 400 + items in the list.
            // this.debounce(function() {this.methods.filter_urls(newValue);});
        },
    },
    mounted: function () {
        // should be copied?
        this.filtered_urls = this.original_urls;

        // fall back to defailt category
        this.select_category()
    },
    methods: {
        select_category: function (category_name) {
            if (Object.keys(this.categories).includes(category_name))
                this.selected_category = category_name;
            else
                this.selected_category = this.report_category;
        },
        filter_urls(keyword) {
            // in case of filter reset, or initializiation of this value.
            if (keyword === "") {
                console.log("Removing filter");
                this.filtered_urls = this.order_urls(this.original_urls)
                return
            }

            let urls = [];
            // keep the search order, use a correctly ordered set of original urls:
            let tmp_urls = this.order_urls(this.original_urls);
            tmp_urls.forEach(function (value) {
                if (value.url.includes(keyword))
                    urls.push(value)
            });
            this.filtered_urls = this.order_urls(urls);
        },
        order_urls: function (data) {
            // todo: add sorting icons :)
            // todo: transform this to a component too, move translations here.
            // https://alligator.io/vuejs/grid-component/
            let sortKey = this.sortKey;
            if (!sortKey) {
                return data;
            }

            let order = this.sortOrders[sortKey] || 1;

            // The ordering keys are in different places in the data. See websecmap for the structure of the data.
            // So filter based on this structure.
            if (sortKey === "url") {
                data = data.slice().sort(function (a, b) {
                    // for everything that is not the url name itself, is neatly tucked away.
                    a = a[sortKey];
                    b = b[sortKey];

                    return (a === b ? 0 : a > b ? 1 : -1) * order
                });

                return data;
            }
            if (sortKey === "score") {
                data = data.slice().sort(function (a, b) {

                    // deal with urls without endpoints:
                    if (a.endpoints.length === 0) {
                        return -1 * order;
                    }

                    if (b.endpoints.length === 0) {
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
                if (a.endpoints.length === 0) {
                    return -1 * order;
                }

                if (b.endpoints.length === 0) {
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

        sortBy: function (key) {
            // console.log(`Sorting by ${key}.`);
            this.sortKey = key;

            // dynamically populate the orders
            if (!(key in this.sortOrders)) {
                // console.log('autopopulating sortOrder');
                this.sortOrders[key] = 1;
            }

            this.sortOrders[key] = this.sortOrders[key] * -1;
            this.filtered_urls = this.order_urls(this.filtered_urls);
        },

        category_verdict_to_simple_value: function (verdict, category_name) {
            if (verdict === undefined)
                return "unknown";

            // Internet.nl API V2.0:
            if (verdict.test_result !== undefined) {
                return verdict.test_result;
            }

            // backwards compatible with API v1.0 reports:
            if (verdict.ok > 0) {
                return 'passed'
            }
            if (verdict.ok < 1) {
                if (category_name === 'internet_nl_web_appsecpriv') {
                    return "warning";
                }
                return "failed"
            }

        },

        category_value_with_comparison: function (category_name, url) {
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
                if (progression[simple_value] > progression[other_simple_value]) {
                    comparison_verdict = "improved";
                } else {
                    comparison_verdict = "regressed";
                }
            }

            let comparison_text = this.$i18n.t("report.results.comparison." + comparison_verdict);

            return `<span class="category_${simple_value} compared_with_next_report_${comparison_verdict}">${comparison_text} ${simple_value}</span>`
        },

        detail_value_with_comparison: function (category_name, url) {
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
            /* disabling translations saves a second on 500 urls and the TLS page. Therefore no translations are applied */

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

            const neutral_values = ["unknown", "not_applicable", "not_testable", 'no_mx', 'unreachable', 'error_in_test', 'error', 'not_tested'];

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

        category_from_field_name: function (field_name) {
            return this.field_name_to_category_names[field_name];
        },


    },
    computed: {
        relevant_categories_based_on_settings: function () {
            let preferred_fields = [];  // this.categories[this.selected_category];
            this.scan_methods.forEach((scan_method) => {
                // todo: also get relevant column for scan_methods, just like with graphs. But given large refactor,
                // we'll do that later.
                if (['web', 'mail'].includes(scan_method.name) && scan_method.name === this.selected_category) {
                    scan_method.categories.forEach((category) => {
                        category.fields.forEach((field) => {
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
                            });
                        }
                    });
                }
            });
            // console.log("Prefered fields: " + preferred_fields)

            // now determine for each field if they should be visible or not. Perhaps this should be in
            // the new_categories
            let returned_fields = [];
            preferred_fields.forEach((preferred_field) => {
                if (this.$store.state.visible_metrics[preferred_field].visible) {
                    returned_fields.push(preferred_field)
                }
            });
            // console.log("Returned fields: " + returned_fields)
            return returned_fields;
        },
    }
}
</script>

<style>
#report-template {
    width: 100%;
    min-height: 500px;
}

/* Do print the whole table... */
@media print {
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
    transform: rotate(315deg);
    width: 32px; /*Fits the 100% value too.*/
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
    background-color: rgba(0, 0, 0, .05);
}

.table td, .table th {
    padding: .75rem;
    vertical-align: top;
    border-top: 1px solid #dee2e6;
}

.direct_link_to_report {
    font-size: 0.8em;
}

.table .summaryrow {
    font-size: 0.8em;
}


#report-template .testresultcell span {
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

.category_passed {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-check.svg");
}

.passed {
    background-image: url("/static/images/vendor/internet_nl/li-shield-ok.svg");
}

.category_failed {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-error.svg");
}

.failed {
    background-image: url("/static/images/vendor/internet_nl/icon-error.svg");
}

.warning {
    background-image: url("/static/images/vendor/internet_nl/icon-warning.svg");
}

.category_info {
    background-image: url("/static/images/vendor/internet_nl/icon-info.svg");
}

.category_unknown {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-check.svg");
}


.category_warning {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-warning.svg");
}

.category_error {
    background-image: url("/static/images/vendor/internet_nl/probe-error.svg");
}

.info {
    background-image: url("/static/images/vendor/internet_nl/icon-info.svg");
}

/* First name was old internet.nl v1 api, second is v2 api.*/
.good_not_tested {
    background-image: url("/static/images/vendor/internet_nl/icon-not-tested-question-mark.svg");
}

.error_in_test, .error, .not_testable, .unreachable {
    background-image: url("/static/images/vendor/internet_nl/icon-not-tested-bolt.svg");
}

.not_applicable, .not_tested, .no_mx {
    background-image: url("/static/images/vendor/internet_nl/icon-not-tested.svg");
}

.compared_with_next_report_neutral:before {
    content: '';
    /* No image is the cleanest background-image: url("/static/images/report_comparison_neutral.png"), none; */
    width: 32px;
    height: 100%;
    background-repeat: no-repeat;
    background-position: right top;
    display: block;
}

.compared_with_next_report_improved:before {
    content: '';
    background-image: url("/static/images/report_comparison_improved.png");
    width: 32px;
    height: 100%;
    background-repeat: no-repeat;
    background-position: right top;
    display: block;
}

.compared_with_next_report_regressed:before {
    content: '';
    background-image: url("/static/images/report_comparison_regressed.png");
    width: 32px;
    height: 100%;
    background-repeat: no-repeat;
    background-position: right top;
    display: block;
}

.faq-subtest {
    padding-left: 1.5em;
    background-image: url("/static/images/vendor/internet_nl/icon-testresult-default.svg");
    background-size: 1.125em 1.125em
}

.testresult.passed, .faq-subtest.passed {
    background-image: url("/static/images/vendor/internet_nl/icon-check.svg") !important
}

.testresult.failed, .faq-subtest.failed {
    background-image: url("/static/images/vendor/internet_nl/icon-error.svg") !important
}

.testresult.warning, .faq-subtest.warning {
    background-image: url("/static/images/vendor/internet_nl/icon-warning.svg") !important
}

.testresult.info, .faq-subtest.info {
    background-image: url("/static/images/vendor/internet_nl/icon-info.svg") !important
}

.testresult.good-not-tested, .faq-subtest.good-not-tested {
    background-image: url("/static/images/vendor/internet_nl/icon-not-tested-question-mark.svg") !important
}

.testresult.not-tested, .faq-subtest.not-tested {
    background-image: url("/static/images/vendor/internet_nl/icon-not-tested.svg") !important
}


.testresults h2.error, .faq-test.error, #testresults-overview ul li.error {
    background-image: url("/static/images/vendor/internet_nl/probe-error.svg") !important
}

.testresults h2.warning, .faq-test.warning, .test-header .test-title h2.warning, #testresults-overview ul li.warning {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-warning.svg") !important
}

.testresults h2.failed, .faq-test.failed, .test-header .test-title h2.failed, #testresults-overview ul li.failed {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-error.svg") !important
}

.testresults h2.info, .faq-test.info, .test-header .test-title h2.info, #testresults-overview ul li.info {
    background-image: url("/static/images/vendor/internet_nl/icon-info.svg") !important
}

.testresults h2.passed, .faq-test.passed, .test-header .test-title h2.passed, #testresults-overview ul li.passed {
    background-image: url("/static/images/vendor/internet_nl/icon-circle-check.svg") !important
}

</style>

<i18n>
{
    "en": {
        "score": "Score",
        "domain": "Domain",
        "report": {
            "title": "Report",
            "intro": "This table shows detailed results per category. It is possible to compare this report to a second report. In that case, progress incidators are added to the first report where applicable. The domains of the second report are only compared, not displayed.",
            "url_filter": "Filter on domain...",
            "not_eligeble_for_scanning": "Domain did not match scanning criteria at the time the scan was initiated. The scanning criteria are an SOA DNS record (not NXERROR) for mail and an A or AAAA DNS record for web. This domain is ignored in all statistics.",
            "zoom": {
                "buttons": {
                    "zoom": "details",
                    "remove_zoom": "Back to the category view",
                    "zoom_in_on": "View details of {0}"
                },
                "zoomed_in_on": "Details from",
                "explanation": "Using the details buttons, it is possible to see the individual metrics for each category."
            },
            "link_to_report": "View score and report from %{url} on internet.nl.",
            "empty_report": "It looks like this report is empty... did you filter too much?",
            "results": {
                "not_applicable": "Not applicable",
                "not_testable": "Not testable",
                "error_in_test": "Test error",
                "category_error_in_test": "Test error",
                "not_tested": "Not tested",
                "failed": "Failed",
                "warning": "Warning",
                "info": "Info",
                "passed": "Passed",
                "unknown": "Unknown",
                "comparison": {
                    "neutral": "-",
                    "improved": "Improved compared to the second report selected.",
                    "regressed": "Regressed compared to the second report selected."
                }
            }
        },
        "icons": {
            "remove_filter": "Remove filter"
        },
        "icon_legend": {
            "title": "Legend of used icons",
            "category_error_in_test": "Error occured while testing ⇒ null score",
            "subtest_not_applicable": "Not applicable ⇒ no score impact",
            "subtest_not_tested": "Not tested ⇒ no score impact",
            "subtest_error_in_test": "Error occured while testing ⇒ null score"
        },
        "differences_compared_to_current_list": {
            "equal": "The domains in this report are equal to the domains in the associated list of domains.",
            "not_equal": "The domains in this report differ from the domains in the associated list of domains.",
            "both_list_contain_n_urls": "Both the report and the associated list of domains contain {0} domains.",
            "report_contains_n_urllist_contains_n": "This report contains {0} domains, while the associated list contains {1}.",
            "in_report_but_not_in_urllist": "Domains in this report, but not in the list",
            "in_urllist_but_not_in_report": "Domains not in this report"
        }
    },
    "nl": {
        "score": "Score",
        "domain": "Domein",
        "report": {
            "title": "Rapport",
            "intro": "Deze tabel toont de details van het rapport. Het is mogelijk dit rapport te vergelijken met een vorig of ander rapport. Wanneer deze vergelijking wordt gemaakt, wordt bij de gegevens van het eerste rapport voortgangsindicatoren geplaats waar relevant. De domeinen van het tweede rapport worden alleen vergeleken, niet getoond.",
            "not_eligeble_for_scanning": "Dit domein voldeed niet aan de scan-criteria op het moment van scannen. Deze criteria zijn een SOA DNS record (geen NXERROR) voor mail en een A of AAAA DNS record voor web. Dit domein komt niet terug in de statistieken.",
            "url_filter": "Filter op domein...",
            "zoom": {
                "buttons": {
                    "zoom": "details",
                    "remove_zoom": "Terug naar hoofdniveau",
                    "zoom_in_on": "Bekijk de details van {0}"
                },
                "zoomed_in_on": "Details van ",
                "explanation": "Met de detail buttons is het mogelijk om details van ieder categorie naar voren te halen."
            },
            "link_to_report": "Bekijk de score en rapportage van %{url} op internet.nl.",
            "empty_report": "Geen meetgegevens gevonden, wordt er misschien teveel gefilterd?",
            "results": {
                "not_applicable": "Niet van toepassing",
                "not_testable": "Niet testbaar",
                "error_in_test": "Testfout",
                "category_error_in_test": "Testfout",
                "not_tested": "Niet getest",
                "failed": "Niet goed",
                "warning": "Waarschuwing",
                "info": "Info",
                "passed": "Goed",
                "unknown": "Onbekend",
                "comparison": {
                    "neutral": "-",
                    "improved": "Verbeterd vergeleken met het 2e geselecteerde rapport.",
                    "regressed": "Verslechterd vergeleken met het 2e geselecteerde rapport."
                }
            }
        },
        "icons": {
            "remove_filter": "Wis filter"
        },
        "icon_legend": {
            "title": "Legenda van gebruikte pictogrammen",
            "category_error_in_test": "Fout in test ⇒ nulscore",
            "subtest_not_tested": "Niet getest ⇒ geen score impact",
            "subtest_error_in_test": "Fout in test ⇒ nulscore"
        },
        "differences_compared_to_current_list": {
            "equal": "Domeinen in dit rapport zijn gelijk aan de domeinen in de bijbehorende lijst.",
            "not_equal": "Domeinen in dit rapport wijken af van de domeinen in de bijbehorende lijst.",
            "both_list_contain_n_urls": "Zowel de rapportage als de bijbehorende lijst bevatten {0} domeinen.",
            "report_contains_n_urllist_contains_n": "Deze rapportage bevat {0} domeinen terwijl de bijbehorende lijst {1} domeinen bevat.",
            "in_report_but_not_in_urllist": "Domeinen in het rapport, maar niet in de bijbehorende lijst",
            "in_urllist_but_not_in_report": "Domeinen niet in het rapport"
        }
    }
}
</i18n>