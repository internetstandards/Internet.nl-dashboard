<style scoped>
.panel-content {
    padding-bottom: 10px;
    padding-left: 20px;
}

.chart_collapse_panel {
    border-top: 1px solid gray;
    border-bottom: 1px solid gray;
    margin-top: 10px;
    margin-bottom: 10px;
}

.panel-title {
    font-size: 1.0em;
    padding-left: 20px;
}

</style>

<template>
    <div class="chart_collapse_panel">
        <h1 class="panel-title">
            <a href="" aria-expanded="false">
                <span class="visuallyhidden">-:</span>
                {{ title }}
                <span class="pre-icon visuallyhidden"></span>
                <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
            </a>
        </h1>
        <div class="panel-content">
            <slot name="content">
                default content
            </slot>
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
    }

}
</script>

<style scoped>

</style>
