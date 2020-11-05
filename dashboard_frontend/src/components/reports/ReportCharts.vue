<style>
.testresult h3 {
    margin-top: 0;
}
</style>
<template>

    <div v-if="color_scheme.incremental.length > 1">
        <div class="block fullwidth">
            <h2>{{ $t("chart_info.adoption_timeline.annotation.title") }}</h2>
            <a class="anchor" name="charts"></a>
            <p>{{ $t("chart_info.adoption_timeline.annotation.intro") }}</p>

            <div style="overflow: auto; width: 100%;">
                <!-- :key is used because that key changes when chaning the language, causing the graph to rerender and thus translate.
                this cannot be done inside the graph, even with rerender title unfortunately. Perhaps it can, but cant figure it out. -->
                <div class="chart-container" style="position: relative; height:300px; width:100%; min-width: 950px;"
                     v-for="item in [$i18n.t(scan_methods[0].name)]" :key="item">

                    <line-chart
                        :color_scheme="color_scheme"
                        :trigger_rerender_when_this_changes="locale"
                        :translation_key="'charts.adoption_timeline'"
                        :chart_data="issue_timeline_of_related_urllists"
                        :selected_report_ids="selected_report_ids"
                        :accessibility_text="$t('charts.adoption_timeline.accessibility_text')"
                        :axis="['average_internet_nl_score']">
                    </line-chart>

                    <div style="overflow-x: scroll; overflow-y: hidden;">
                        <span v-for="timeline in issue_timeline_of_related_urllists" :key="timeline.name">
                            <table class="table table-striped" style="font-size: 0.8em;">
                                <caption>{{ timeline.name }}: {{ $t("charts.adoption_timeline.title") }}</caption>
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
                                    <tr v-for="(stat, index) in timeline.data" :key="index">
                                        <td>
                                            {{ humanize_date_date_only(stat.date) }}
                                        </td>
                                        <td>
                                            {{ stat.average_internet_nl_score }}%
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </span>
                    </div>

                </div>
            </div>
        </div>

        <div class="block fullwidth" v-if="!can_show_charts()">
            <h2>⚠️ {{ $t("selected_report_is_from_before_api_2.title") }}</h2>
            <p>{{ $t("selected_report_is_from_before_api_2.intro") }}</p>
        </div>

        <div v-else>
            <div class="block fullwidth" style="page-break-before: always;" v-if='compare_charts.length > 0'>
                <h2>
                    {{ $t("chart_info.adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("chart_info.adoption_bar_chart.annotation.intro") }}</p>

                <!-- :key is used because that key changes when chaning the language, causing the graph to rerender and thus translate.
                this cannot be done inside the graph, even with rerender title unfortunately. Perhaps it can, but cant figure it out. -->
                <div v-for="scan_form in scan_methods" :key="$i18n.t(scan_form.name)">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div style="overflow: auto; width: 100%"
                             v-if="visible_fields_from_scan_form(scan_form).length > 0">
                            <div class="chart-container"
                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
                                <percentage-bar-chart
                                    :title="graph_bar_chart_title"
                                    :translation_key="'charts.adoption_bar_chart'"
                                    :chart_data="compare_charts"
                                    :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                    :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                    :axis="visible_fields_from_scan_form(scan_form)">
                                </percentage-bar-chart>
                            </div>
                        </div>

                        <div v-for="category in scan_form.categories" :key="category.key">
                            <template v-if="category_is_visible(category.key)">
                                <div style="page-break-inside: avoid;"
                                     v-if="visible_fields_from_categories(category).length > 0">

                                    <chart_collapse_panel :title="category.label" :level="'level_two'">
                                        <div slot="chart_content">
                                            <percentage-bar-chart
                                                style="height: 500px;"
                                                :title="graph_bar_chart_title"
                                                :translation_key="'charts.adoption_bar_chart'"
                                                :chart_data="compare_charts"
                                                :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                :field_name_to_category_names="field_name_to_category_names"
                                                :axis="visible_fields_from_categories(category)">
                                            </percentage-bar-chart>
                                        </div>
                                    </chart_collapse_panel>
                                </div>

                                <div v-for="subcategory in category.categories" :key="subcategory.key">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div style="page-break-inside: avoid;"
                                         v-if="fields_from_self(subcategory).length > 0">

                                        <chart_collapse_panel :title="subcategory.label" :level="'level_three'">
                                            <div slot="chart_content">
                                                <percentage-bar-chart
                                                    style="height: 500px;"
                                                    :title="graph_bar_chart_title"
                                                    :translation_key="'charts.adoption_bar_chart'"
                                                    :chart_data="compare_charts"
                                                    :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                    :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                    :field_name_to_category_names="field_name_to_category_names"
                                                    :axis="fields_from_self(subcategory)">
                                                </percentage-bar-chart>
                                            </div>
                                        </chart_collapse_panel>

                                        <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                        <template
                                            v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                            <chart_collapse_panel :title="subcategory.label" :level="'level_three'">
                                                <div slot="chart_content">
                                                    <percentage-bar-chart
                                                        style="height: 500px;"
                                                        :title="graph_bar_chart_title"
                                                        :translation_key="'charts.adoption_bar_chart'"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                        :show_dynamic_average="true"
                                                        :only_show_dynamic_average="true"
                                                        :field_name_to_category_names="field_name_to_category_names"
                                                        :axis="fields_from_self_and_do_not_filter(subcategory)">
                                                    </percentage-bar-chart>
                                                </div>
                                            </chart_collapse_panel>
                                        </template>

                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>
            </div>

            <div class="block fullwidth" style="page-break-before: always;" aria-hidden="true"
                 v-if='compare_charts.length > 1'>

                <h2>
                    {{ $t("chart_info.cumulative_adoption_bar_chart.annotation.title") }}
                </h2>
                <p>{{ $t("chart_info.cumulative_adoption_bar_chart.annotation.intro") }}</p>

                <div v-for="scan_form in scan_methods" :key="scan_form.name">
                    <template v-if="scan_form.name === selected_report[0].type">

                        <div style="overflow: auto; width: 100%"
                             v-if="visible_fields_from_scan_form(scan_form).length > 0">
                            <div class="chart-container"
                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
                                <cumulative-percentage-bar-chart
                                    style="height: 500px"
                                    :title="graph_cumulative_bar_chart_title"
                                    :translation_key="'charts.adoption_bar_chart'"
                                    :chart_data="compare_charts"
                                    :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
                                    :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                    :axis="visible_fields_from_scan_form(scan_form)">
                                </cumulative-percentage-bar-chart>
                            </div>
                        </div>

                        <div v-for="category in scan_form.categories" :key="category.key">
                            <template v-if="category_is_visible(category.key)">
                                <div style="page-break-inside: avoid;"
                                     v-if="visible_fields_from_categories(category).length > 0">


                                    <chart_collapse_panel :title="category.label" :level="'level_two'">
                                        <div slot="chart_content">
                                            <cumulative-percentage-bar-chart
                                                style="height: 500px"
                                                :title="graph_cumulative_bar_chart_title"
                                                :translation_key="'charts.adoption_bar_chart'"
                                                :chart_data="compare_charts"
                                                :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
                                                :show_dynamic_average="issue_filters[category.key].show_dynamic_average"
                                                :field_name_to_category_names="field_name_to_category_names"
                                                :axis="visible_fields_from_categories(category)">
                                            </cumulative-percentage-bar-chart>
                                        </div>
                                    </chart_collapse_panel>

                                </div>

                                <div v-for="subcategory in category.categories" :key="subcategory.label">
                                    <!-- Visibility depends on parent category, the labels themselves cannot yet be filtered for visibility. -->
                                    <div style="page-break-inside: avoid;"
                                         v-if="fields_from_self(subcategory).length > 0">


                                        <chart_collapse_panel :title="subcategory.label" :level="'level_three'">
                                            <div slot="chart_content">
                                                <cumulative-percentage-bar-chart
                                                    style="height: 500px"
                                                    :title="graph_cumulative_bar_chart_title"
                                                    :translation_key="'charts.adoption_bar_chart'"
                                                    :chart_data="compare_charts"
                                                    :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                    :show_dynamic_average="issue_filters[subcategory.key].show_dynamic_average"
                                                    :field_name_to_category_names="field_name_to_category_names"
                                                    :axis="fields_from_self(subcategory)">
                                                </cumulative-percentage-bar-chart>
                                            </div>
                                        </chart_collapse_panel>


                                        <!-- Special graph for Forum standardisation, that cannot have the items disabled -->
                                        <template
                                            v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                            <chart_collapse_panel :title="'This shows the average for Forum Standardisation, it is not possible\n'+
'                                                to\n'+
'                                                show the average or to select what fields should be visible.'" :level="'level_three'">
                                                <div slot="chart_content">
                                                    <cumulative-percentage-bar-chart
                                                        style="height: 500px"
                                                        :title="graph_cumulative_bar_chart_title"
                                                        :translation_key="'charts.adoption_bar_chart'"
                                                        :chart_data="compare_charts"
                                                        :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                                        :show_dynamic_average="true"
                                                        :only_show_dynamic_average="true"
                                                        :field_name_to_category_names="field_name_to_category_names"
                                                        :axis="fields_from_self_and_do_not_filter(subcategory)">
                                                    </cumulative-percentage-bar-chart>
                                                </div>
                                            </chart_collapse_panel>
                                        </template>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import field_translations from './../field_translations'

import CumulativePercentageBarChart from './../charts/cumulative-percentage-bar-chart'
import LineChart from './../charts/line-chart'
import PercentageBarChart from './../charts/percentage-bar-chart'
import chart_collapse_panel from './../chart_collapse_panel'

export default {
    components: {
        'cumulative-percentage-bar-chart': CumulativePercentageBarChart,
        'line-chart': LineChart,
        'percentage-bar-chart': PercentageBarChart,
        'chart_collapse_panel': chart_collapse_panel,
    },
    i18n: {
        sharedMessages: field_translations,
    },
    mounted: function () {
        this.color_scheme.incremental = this.generate_color_increments(10);
        this.get_timeline();
    },
    props: {
        compare_charts: {type: Array, required: true},
        scan_methods: {type: Array, required: true},
        issue_filters: {type: Object, required: true},
        selected_report: {type: Array, required: true},
        field_name_to_category_names: {type: Object, required: false},
        selected_report_ids: {type: Array, required: false},
    },
    data: function () {
        return {
            // https://github.com/ashiguruma/patternomaly/blob/master/assets/pattern-list.png
            possible_chart_patterns: [
                'weave', 'dot', 'ring', 'dash', 'plus', 'zigzag', 'square', 'diagonal',
                'disc', 'zigzag-vertical', 'triangle', 'line', 'cross-dash', 'diamond'],
            // See #18 for the primary sources of these colors.
            // this can help to explain the colors: https://www.canva.com/colors/color-wheel/
            // blue #154273, orange #E17000, green #39870C, red #731542, gray #7e7d82
            possible_chart_colors: [
                'rgba(225, 112, 0, 1)', 'rgba(57, 135, 12, 1)',
                'rgba(115, 21, 66, 1)', 'rgb(89, 88, 92)', 'rgba(21, 66, 115, 1)',
            ],
            color_scheme: {
                incremental: [],
            },

            // graphs:
            issue_timeline_of_related_urllists: [],
        }
    },
    methods: {

        can_show_charts: function () {
            // At June 30 2020 api 2.0 reports where introduced. Before that, calculations where done differently,
            // where info and warning would be seen as passed. This has been changed, and since then there is more
            // granularity. Because of differences in data: fields, statistics and how the data is used, a decision
            // was made to delete all prior reports. Since that also affects scores over time, and since the data
            // per metric in the metric table is still useful, the graphs have been set to hide.
            // Of course it is still possible to download the graph data, or even show it in the interface if you
            // know your way around javascript. But the result will be off the charts, literally :) -> thus hiding
            // is the friendliest choice..

            const api_2_introduced = Date.parse("2020-06-30 00:00:00.000000+00:00")

            let showable = true;
            this.compare_charts.forEach((item) => {
                // "2020-05-14 10:55:16.129108+00:00"
                if (Date.parse(item.at_when) < api_2_introduced)
                    showable = false
            });

            return showable;
        },

        generate_color_increments: function (number) {
            // Generate n colors for charts, rotating over the available options. Returns a list with css properties.
            // The first item is always the same in a single color to give a consistent look/feel to all first graphs
            let colors = [{background: 'rgba(21, 66, 115, 1)', border: 'rgba(21, 66, 115, 1)'},];
            for (let i = 0; i < number; i++) {
                // make sure we never run out of options.
                let my_pattern = this.possible_chart_patterns.shift();
                this.possible_chart_patterns.push(my_pattern);
                let my_color = this.possible_chart_colors.shift();
                this.possible_chart_colors.push(my_color);

                // this might be needed in the future pattern.draw(my_pattern, my_color)
                colors.push({background: my_color, border: my_color})
            }

            return colors;
        },
        get_timeline() {
            // selected_report.urllist_id contains the key to the timeline.
            // data/report/urllist_report_graph_data/10/

            if (this.selected_report[0].urllist_id === 0) {
                return;
            }

            // report_id's:
            let report_ids = [];
            this.selected_report.forEach((item) => {
                report_ids.push(item.urllist_id)
            });

            fetch(`${this.$store.state.dashboard_endpoint}/data/report/urllist_timeline_graph/${report_ids.join(",")}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.issue_timeline_of_related_urllists = data;
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });

        },
        visible_fields_from_scan_form: function (scan_form) {
            // see if any of the underlaying categories is visible. If so, include the category.
            let fields = [];

            scan_form.categories.forEach((category) => {
                // console.log(category.key);
                if (this.category_is_visible(category.key)) {
                    category.fields.forEach((field) => {
                        fields.push(field.name);
                    });
                }
            });
            return fields;
        },
        fields_from_self: function (category) {
            let fields = [];

            category.fields.forEach((field) => {
                fields.push(field.name);
            });

            let returned_fields = [];

            for (let i = 0; i < fields.length; i++) {
                if (this.issue_filters[fields[i]].visible)
                    returned_fields.push(fields[i])
            }
            return returned_fields;
        },
        category_is_visible: function (category_key) {

            // See #6. If any of the subcategory fields
            return this.visible_fields_from_categories(this.get_category_by_name(category_key)).length > 0;
        },
        // should be named: visible fields from categories
        visible_fields_from_categories(categories) {
            let fields = [];

            categories.categories.forEach((category) => {

                category.fields.forEach((field) => {
                    fields.push(field.name);
                });

            });

            let returned_fields = [];
            for (let i = 0; i < fields.length; i++) {
                if (this.issue_filters[fields[i]].visible)
                    returned_fields.push(fields[i])
            }

            return returned_fields;
        },
        fields_from_self_and_do_not_filter(category) {
            let fields = [];

            category.fields.forEach((field) => {
                fields.push(field.name);
            });
            return fields;
        },
        get_category_by_name: function (category_key) {
            let found = null;
            this.scan_methods.forEach((scan_method) => {
                scan_method.categories.forEach((category) => {
                    if (category.key === category_key) {
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
    },
    watch: {
        selected_report: function () {
            this.get_timeline();
        }
    },
    computed: {

        graph_bar_chart_title: function () {
            // fixing https://github.com/internetstandards/Internet.nl-dashboard/issues/65
            // 1 report:
            if (this.selected_report.length === 1) {
                return `📊 #${this.selected_report[0].id}: ${this.selected_report[0].list_name} ${this.$moment(this.selected_report[0].at_when).format('LL')} n=${this.selected_report[0].number_of_urls}`;
            } else {
                let titles = [];

                this.selected_report.forEach((report) => {
                    titles.push(`📊 #${report.id}: ${report.list_name} ${this.$moment(report.at_when).format('LL')} n=${report.number_of_urls}`);
                });

                return titles.join(" vs ");
            }
        },

        graph_cumulative_bar_chart_title: function () {
            // fixing https://github.com/internetstandards/Internet.nl-dashboard/issues/65
            // 1 report:
            if (this.selected_report.length === 1) {
                // not relevant
                return `📊 #${this.selected_report[0].id}: ${this.selected_report[0].list_name} ${this.$moment(this.selected_report[0].at_when).format('LL')} n=${this.selected_report[0].number_of_urls}`;
            } else {
                let titles = [];

                this.selected_report.forEach((report) => {
                    titles.push(`📊 #${report.id}: ${report.list_name} ${this.$moment(report.at_when).format('LL')} n=${report.number_of_urls}`);
                });

                let title_text = titles.join(" + ");
                return `(${title_text}) / ${this.selected_report.length}`
            }
        },
    }
}
</script>
<i18n>
{
    "en": {
        "charts": {
            "adoption_timeline": {
                "title": "Average internet.nl score over time.",
                "yAxis_label": "Average internet.nl score",
                "xAxis_label": "Date",
                "average_internet_nl_score": "Average internet.nl score",
                "accessibility_text": "A table with the content of this graph is shown below."
            },
            "adoption_bar_chart": {
                "title_single": "Average adoption of standards, %{list_information}, %{number_of_domains} domains.",
                "title_multiple": "Comparison of adoption of standards between %{number_of_reports} reports.",
                "yAxis_label": "Adoption",
                "average": "Average",
                "accessibility_text": "A table with the content of this graph is shown below."
            },
            "cumulative_adoption_bar_chart": {
                "title": "Average adoption of standards over %{number_of_reports} reports.",
                "yAxis_label": "Adoption",
                "average": "Average",
                "accessibility_text": "A table with the content of this graph is shown below."
            }
        },
        "selected_report_is_from_before_api_2": {
            "title": "Unable to show all statistics",
            "intro": "One of the selected reports are from before 30th of June 2020. Before that date, reports contained different calculations which are not consistent with the current version of the dashboard."
        },
        "chart_info": {
            "adoption_timeline": {
                "annotation": {
                    "title": "Internet.nl score over time",
                    "intro": "This graph compares the average internet.nl score over time."
                }
            },
            "magazine": {
                "intro": "Below graph only shows the average of all magazine fields. Other fields cannot be enabled/disabled and changing their visibility does not influence this average."
            },
            "adoption_bar_chart": {
                "annotation": {
                    "title": "Average adoption of standards ",
                    "intro": "This graph shows the average adoption per standard per report."
                }
            },
            "cumulative_adoption_bar_chart": {
                "annotation": {
                    "title": "Average adoption of standards over multiple reports",
                    "intro": "This graph shows the average adoption per standard averaged over multiple reports."
                }
            }
        }
    },
    "nl": {
        "charts": {
            "adoption_timeline": {
                "title": "Adoptie van standaarden over tijd.",
                "yAxis_label": "Gemiddelde internet.nl score",
                "xAxis_label": "Datum",
                "average_internet_nl_score": "Gemiddelde internet.nl score",
                "accessibility_text": "Een tabel met de inhoud van deze grafiek wordt hieronder getoond."
            },
            "adoption_bar_chart": {
                "title_single": "Adoptie van standaarden, %{list_information}, %{number_of_domains} domeinen.",
                "title_multiple": "Vergelijking adoptie van standaarden tussen %{number_of_reports} rapporten.",
                "yAxis_label": "Adoptiegraad",
                "average": "Gemiddeld",
                "accessibility_text": "Een tabel met de inhoud van deze grafiek wordt hieronder getoond."
            },
            "cumulative_adoption_bar_chart": {
                "title": "Gemiddelde adoptie van standaarden van %{number_of_reports} rapporten.",
                "yAxis_label": "Adoptiegraad",
                "average": "Gemiddeld",
                "accessibility_text": "Een tabel met de inhoud van deze grafiek wordt hieronder getoond."
            }
        },
        "selected_report_is_from_before_api_2": {
            "title": "Niet mogelijk om alle statistieken te tonen",
            "intro": "Een van de geselecteerde rapporten is van voor 30 juni 2020. Rapporten van voor deze datum gebruiken een andere rekenmethode, waardoor ze niet consistent zijn met de huidige versie van het dashboard."
        },
        "chart_info": {
            "adoption_timeline": {
                "annotation": {
                    "title": "Gemiddelde internet.nl score over tijd.",
                    "intro": "Deze grafiek toont de gemiddelde internet.nl score over tijd."
                }
            },
            "magazine": {
                "intro": "Onderstaande grafiek toont het gemiddelde van alle magazine velden. Deze grafiek kan niet worden aangepast, ook niet door de zichtbaarheid van velden aan te passen."
            },
            "adoption_bar_chart": {
                "annotation": {
                    "title": "Adoptie van standaarden",
                    "intro": "Deze grafiek toont het percentage adoptie per categorie en onderliggende metingen."
                }
            },
            "cumulative_adoption_bar_chart": {
                "annotation": {
                    "title": "Gemiddelde adoptie, waarbij rapporten bij elkaar worden opgeteld",
                    "intro": "In deze grafiek worden de geselecteerde rapporten bij elkaar opgeteld, en daar het gemiddelde van getoond."
                }
            }
        }
    }
}
</i18n>
