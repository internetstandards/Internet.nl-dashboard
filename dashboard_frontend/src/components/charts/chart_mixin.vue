<script>
import { debounce } from "debounce";
import field_translations from "@/components/field_translations";

export default {
    i18n: {
        sharedMessages: field_translations,
    },
    props: {
        trigger_rerender_when_this_changes: {type: String, required: false},
        chart_data: {type: Array, required: true},
        axis: {type: Array, required: false},
        color_scheme: {type: Object, required: false},
        title: {type: String, required: false},
        translation_key: {type: String, required: false},
        accessibility_text: {type: String, required: true},
        show_dynamic_average: {type: Boolean, required: false},
        only_show_dynamic_average: {type: Boolean, required: false},
        field_name_to_category_names: {type: Object, required: false},
        selected_report_ids: {type: Array, required: false}
    },
    data: function () {
        return {
            chart: {}
        }
    },
    render: function (createElement) {
        return createElement(
            'canvas',
            {
                ref: 'canvas',

                // Improve accessibility: https://www.chartjs.org/docs/latest/general/accessibility.html
                // Using createElement features: https://vuejs.org/v2/guide/render-function.html#createElement-Arguments
                attrs: {
                    role: "img",
                    class: "graph-image",
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
    created() {
        // When the chart data is downloaded, it might be that a ton of stuff is processed. To prevent
        // too many renders, we slow the chart building a bit by debouncing it.
        // This also prevents some of the "me.getDatasetMeta(...).controller is null" errors in charts.js (nov 2019)
        // You cannot add a debounce on a watch:
        // https://stackoverflow.com/questions/47172952/vuejs-2-debounce-not-working-on-a-watch-option
        this.unwatch = this.$watch('chart_data', debounce(() => {
            this.renderData();
        }, 500), {
            // Note that you don’t need to do so to listen for in-Array mutations as they won't happen and the
            // arrays are too complex and big.
            deep: false
        })
    },
    watch: {
        trigger_rerender_when_this_changes: function () {
            this.renderTitle();
        },
        axis: function (new_value, old_value) {
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },
        show_dynamic_average: function () {
            this.renderData();
        },
        only_show_dynamic_average: function () {
            this.renderData();
        },
        title: function (new_value, old_value) {
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderTitle();
            }
        },

        // Supports changing the colors of this graph ad-hoc.
        // charts.js is not reactive.
        color_scheme: function (new_value, old_value) {
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },
    }
};
</script>
<i18n>
{
    "en": {
        "pct_ok": "passed",
        "pct_low": "info",
        "pct_medium": "warning",
        "pct_high": "failed",
        "pct_not_applicable": "not applicable",
        "pct_not_testable": "not testable",
        "pct_error_in_test": "test error",
        "charts": {
            "adoption_timeline": {
                "title": "Average internet.nl score over time.",
                "month": "Month",
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
        }
    },
    "nl": {
        "pct_ok": "geslaagd",
        "pct_low": "info",
        "pct_medium": "waarschuwing",
        "pct_high": "gezakt",
        "pct_not_applicable": "niet van toepassing",
        "pct_not_testable": "niet testbaar",
        "pct_error_in_test": "testfout",
        "charts": {
            "adoption_timeline": {
                "title": "Adoptie van standaarden over tijd.",
                "month": "Maand",
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
        }
    }
}
</i18n>
