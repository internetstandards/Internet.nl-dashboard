{% verbatim %}
<template type="text/x-template" id="internet-nl-charts-template">

    <div v-if="color_scheme.incremental.length > 1">
        <div class="block fullwidth">
            <h2>{{ $t("chart_info.adoption_timeline.annotation.title") }}</h2>
            <a class="anchor" name="charts"></a>
            <p>{{ $t("chart_info.adoption_timeline.annotation.intro") }}</p>

            <div style="overflow: auto; width: 100%;">
                <div class="chart-container" style="position: relative; height:300px; width:100%; min-width: 950px;">
                    <line-chart
                            :color_scheme="color_scheme"
                            :translation_key="'charts.adoption_timeline'"
                            :chart_data="issue_timeline_of_related_urllists"
                            :accessibility_text="$t('charts.adoption_timeline.accessibility_text')"
                            :axis="['average_internet_nl_score']">
                    </line-chart>

                    <div style="overflow-x: scroll; overflow-y: hidden;">
                        <template  v-for="timeline in issue_timeline_of_related_urllists">
                            <table class="table table-striped" style="font-size: 0.8em;">
                                <caption>{{timeline.name}}: {{ $t("charts.adoption_timeline.title") }}</caption>
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
                                    <tr v-for="stat in timeline.data">
                                        <td>
                                            {{ humanize_date_date_only(stat.date) }}
                                        </td>
                                        <td>
                                            {{ stat.average_internet_nl_score }}%
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </template>
                    </div>

                </div>
            </div>
        </div>

        <div class="block fullwidth" style="page-break-before: always;" v-if='compare_charts.length > 0'>
            <h2>
                {{ $t("chart_info.adoption_bar_chart.annotation.title") }}
            </h2>
            <p>{{ $t("chart_info.adoption_bar_chart.annotation.intro") }}</p>

            <template v-for="scan_form in scan_methods">
                <template v-if="scan_form.name === selected_report[0].type">

                    <div style="overflow: auto; width: 100%" v-if="visible_fields_from_scan_form(scan_form).length > 0">
                        <div class="chart-container"
                             style="position: relative; height:500px; width:100%; min-width: 950px;">
                            <percentage-bar-chart
                                    :title="graph_bar_chart_title"
                                    :translation_key="'charts.adoption_bar_chart'"
                                    :color_scheme="color_scheme"
                                    :chart_data="compare_charts"
                                    :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
                                    :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                    :only_show_dynamic_average="false"
                                    :axis="visible_fields_from_scan_form(scan_form)">
                            </percentage-bar-chart>
                        </div>
                    </div>

                    <template v-for="category in scan_form.categories">
                        <template v-if="category_is_visible(category.key)">
                            <div class="testresult" style="page-break-inside: avoid;"
                                 v-if="visible_fields_from_categories(category).length > 0">
                                <h3 class="panel-title">
                                    <a href="" aria-expanded="false">
                                        <span class="visuallyhidden">-:</span>
                                        {{ category.label }}
                                        <span class="pre-icon visuallyhidden"></span>
                                        <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png"
                                                                alt=""></span>
                                    </a>
                                </h3>
                                <div class="panel-content">
                                    <div style="overflow: auto; width: 100%">
                                        <div class="chart-container"
                                             style="position: relative; height:500px; width:100%; min-width: 950px;">
                                            <percentage-bar-chart
                                                    :title="graph_bar_chart_title"
                                                    :translation_key="'charts.adoption_bar_chart'"
                                                    :color_scheme="color_scheme"
                                                    :chart_data="compare_charts"
                                                    :accessibility_text="$t('charts.adoption_bar_chart.accessibility_text')"
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
                                <div class="testresult" style="page-break-inside: avoid;"
                                     v-if="fields_from_self(subcategory).length > 0">
                                    <h4 class="panel-title">
                                        <a href="" aria-expanded="false">
                                            <span class="visuallyhidden">-:</span>
                                            {{ subcategory.label }}
                                            <span class="pre-icon visuallyhidden"></span>
                                            <span class="icon"><img
                                                    src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                        </a>
                                    </h4>
                                    <div class="panel-content">
                                        <div style="overflow: auto; width: 100%">
                                            <div class="chart-container"
                                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
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
                                        <div style="overflow: auto; width: 100%"
                                             v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                            <p>{{ $t("chart_info.magazine.intro") }}</p>
                                            <div class="chart-container"
                                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
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

        <div class="block fullwidth" style="page-break-before: always;" aria-hidden="true" v-if='compare_charts.length > 1'>

            <h2>
                {{ $t("chart_info.cumulative_adoption_bar_chart.annotation.title") }}
            </h2>
            <p>{{ $t("chart_info.cumulative_adoption_bar_chart.annotation.intro") }}</p>

            <template v-for="scan_form in scan_methods">
                <template v-if="scan_form.name === selected_report[0].type">

                    <div style="overflow: auto; width: 100%" v-if="visible_fields_from_scan_form(scan_form).length > 0">
                        <div class="chart-container"
                             style="position: relative; height:500px; width:100%; min-width: 950px;">
                            <cumulative-percentage-bar-chart
                                    :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                'number_of_reports': compare_charts.length})"
                                    :translation_key="'charts.adoption_bar_chart'"
                                    :color_scheme="color_scheme"
                                    :chart_data="compare_charts"
                                    :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
                                    :show_dynamic_average="issue_filters[scan_form.name].show_dynamic_average"
                                    :only_show_dynamic_average="false"
                                    :axis="visible_fields_from_scan_form(scan_form)">
                            </cumulative-percentage-bar-chart>
                        </div>
                    </div>

                    <template v-for="category in scan_form.categories">
                        <template v-if="category_is_visible(category.key)">
                            <div class="testresult" style="page-break-inside: avoid;"
                                 v-if="visible_fields_from_categories(category).length > 0">
                                <h3 class="panel-title">
                                    <a href="" aria-expanded="false">
                                        <span class="visuallyhidden">-:</span>
                                        {{ category.label }}
                                        <span class="pre-icon visuallyhidden"></span>
                                        <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png"
                                                                alt=""></span>
                                    </a>
                                </h3>
                                <div class="panel-content">
                                    <div style="overflow: auto; width: 100%">
                                        <div class="chart-container"
                                             style="position: relative; height:500px; width:100%; min-width: 950px;">
                                            <cumulative-percentage-bar-chart
                                                    :title="$t('charts.cumulative_adoption_bar_chart.title', {
                                                    'number_of_reports': compare_charts.length})"
                                                    :translation_key="'charts.adoption_bar_chart'"
                                                    :color_scheme="color_scheme"
                                                    :chart_data="compare_charts"
                                                    :accessibility_text="$t('charts.cumulative_adoption_bar_chart.accessibility_text')"
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
                                <div class="testresult" style="page-break-inside: avoid;"
                                     v-if="fields_from_self(subcategory).length > 0">
                                    <h4 class="panel-title">
                                        <a href="" aria-expanded="false">
                                            <span class="visuallyhidden">-:</span>
                                            {{ subcategory.label }}
                                            <span class="pre-icon visuallyhidden"></span>
                                            <span class="icon"><img
                                                    src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                                        </a>
                                    </h4>
                                    <div class="panel-content">
                                        <div style="overflow: auto; width: 100%">
                                            <div class="chart-container"
                                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
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
                                        <div style="overflow: auto; width: 100%"
                                             v-if="['category_mail_forum_standardisation_magazine', 'category_web_forum_standardisation_magazine'].includes(subcategory.key)">
                                            <p>This shows the average for Forum Standardisation, it is not possible to
                                                show the average or to select what fields should be visible.</p>
                                            <div class="chart-container"
                                                 style="position: relative; height:500px; width:100%; min-width: 950px;">
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

    </div>
</template>
<script>
    Vue.component('internet-nl-charts', {
        mixins: [humanize_mixin, http_mixin],
        i18n: {
            messages: {
                en: {
                    chart_info: {
                        adoption_timeline: {
                            annotation: {
                                title: 'Internet.nl score over time',
                                intro: 'This graph compares the average internet.nl score over time.'
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

                },
                nl: {
                    chart_info: {
                        adoption_timeline: {
                            annotation: {
                                title: 'Gemiddelde internet.nl score over tijd.',
                                intro: 'Deze grafiek toont de gemiddelde internet.nl score over tijd.'
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
                }
            }
      },
        template: '#internet-nl-charts-template',
        mounted: function () {
            this.color_scheme.incremental = this.generate_color_increments(10);
            this.get_timeline();
        },
        props: {
            compare_charts: {type: Array, required: true},
            scan_methods: {type: Array, required: true},
            issue_filters: {type: Object, required: true},
            selected_report: {type: Array, required: true},
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

                    colors.push({background: pattern.draw(my_pattern, my_color), border: my_color})
                }

                return colors;
            },
            get_timeline(){
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

                fetch(`/data/report/urllist_timeline_graph/${report_ids.join(",")}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                    this.issue_timeline_of_related_urllists = data;
                }).catch((fail) => {console.log('A loading error occurred: ' + fail);});

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
                          category.additional_fields.forEach((field) => {
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
                  category.additional_fields.forEach((field) => {
                      fields.push(field.name);
                  });

                  let returned_fields = [];
                  for (let i = 0; i < fields.length; i++) {

                      if (this.issue_filters[fields[i]].visible)
                          returned_fields.push(fields[i])
                  }
                  return returned_fields;
              },
              category_is_visible: function (category_key){

                  // See #6. If any of the subcategory fields
                  return this.visible_fields_from_categories(this.get_category_by_name(category_key)).length > 0;
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
        },
        watch: {
            selected_report: function(){
                this.get_timeline();
            }
        },
        computed: {

            graph_bar_chart_title: function () {
                // fixing https://github.com/internetstandards/Internet.nl-dashboard/issues/65
                // 1 report:
                if (this.selected_report.length === 1) {
                    return i18n.t('charts.adoption_bar_chart.title_single', {
                        'list_information': this.selected_report[0].list_name,
                        'number_of_domains': this.selected_report[0].number_of_urls,
                    });
                } else {
                    return i18n.t('charts.adoption_bar_chart.title_multiple', {
                        'number_of_reports': this.selected_report.length,
                    });
                }
            },
        }
    });
</script>
{% endverbatim %}
