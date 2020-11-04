<style scoped>
.panel-content {
    padding-bottom: 10px;
}

.chart-container {
    position: relative; height:500px; min-height:500px; width:100%; min-width: 950px;
}
.chart_collapse_panel{
    border-top: 1px solid dimgray;
    border-bottom: 1px solid dimgray;
    margin-top: 10px;
    margin-bottom: 10px;
}

.panel-title {
    font-size: 1.3em;
}

.h2 {
  padding-left: 2em;
    font-size: 1.2em;
}

.h3 {
  padding-left: 3em;
    font-size: 1.1em;
}

</style>

<template>
    <div class="chart_collapse_panel">
        <h1 :class="level" class="panel-title">
            <a href="" aria-expanded="false">
                <span class="visuallyhidden">-:</span>
                {{ title }}
                <span class="pre-icon visuallyhidden"></span>
                <span class="icon"><img
                    src="/static/images/vendor/internet_nl/push-open.png"
                    alt=""></span>
            </a>
        </h1>
        <div class="panel-content">
            <div style="overflow: auto; width: 100%;">
                <div class="chart-container">
                    <slot name="content">
                        default content
                    </slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "collapse_panel.vue",
    props: {
        title: {
            type: String,
            default: ""
        },
        level: {
            type: String,
            default: "",
        }
    }

}
</script>

<style scoped>

</style>
<!--
Possible upgrade:

    <b-button v-b-toggle="category.key" variant="primary">{{ category.label }}</b-button>
    <b-collapse :id="category.key" class="mt-2">
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
                    :field_name_to_category_names="field_name_to_category_names"
                    :axis="visible_fields_from_categories(category)">
                </percentage-bar-chart>
            </div>
        </div>
    </b-collapse>



-->