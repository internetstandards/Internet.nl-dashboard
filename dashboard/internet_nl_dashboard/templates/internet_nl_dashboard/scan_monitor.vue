{% verbatim %}
<style>
    .websitetest table th {
        word-break: keep-all;
    }
</style>
<template type="x-template" id="scan_monitor_template">
    <div style="width: 100%;">
        <div class="block fullwidth">
            <h1>{{ $t("scan_monitor.title") }}</h1>
            <p>{{ $t("scan_monitor.intro") }}</p>
        </div>

        <div class="wrap">
            <div class="block" v-if="scans" v-for="scan in scans">
                <div class="wrapper">
                    <span v-if="scan.finished">✅</span>
                    <span v-if="!scan.finished"><img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif"></span>
                    <b>{{ scan.type }} {{ $t("scan_monitor.id") }}{{ scan.id }}</b><br>
                    <br>
                    📘 <a :href="'/domains/' + scan.list_id + '/#' + scan.list_id">{{ scan.list }}</a><br>
                    <br>
                    <template v-if="scan.finished">
                        <template v-if="scan.last_report_id">
                            📊 <a :href="'/reports/' + scan.last_report_id">{{ $t("scan_monitor.open_report") }}</a><br>
                            <br>
                        </template>
                        <template v-if="!scan.last_report_id">
                            📊 {{ $t("scan_monitor.report_is_being_generated") }}
                        </template>
                        <b>{{ $t("scan_monitor.finished_on") }}</b><br>
                        <span :title="scan.finished_on">{{ humanize_date(scan.finished_on) }},<br>{{ humanize_relative_date(scan.finished_on) }}</span><br>
                        <br>
                        <b>{{ $t("scan_monitor.runtime") }}</b><br>
                        {{ humanize_duration(scan.runtime) }}<br>
                        <br>
                    </template>
                    <template v-if="!scan.finished">
                        <b>{{ $t("scan_monitor.message") }}</b>
                        <p>{{ scan.message }}</p>
                        <b>{{ $t("scan_monitor.last_check") }}</b><br>
                        <span :title="scan.last_check">{{ humanize_date(scan.last_check) }},<br>{{ humanize_relative_date(scan.last_check) }}</span><br>
                        <br>
                    </template>
                    <b>{{ $t("scan_monitor.started_on") }}</b><br>
                    <span :title="scan.started_on">{{ humanize_date(scan.started_on) }},<br>{{ humanize_relative_date(scan.started_on) }}</span><br>
                    <br>

                    🔖 <a :href="scan.status_url" target="_blank">{{ $t("scan_monitor.open_in_api") }}</a><br>
                </div>
            </div>
        </div>

        <div class='block fullwidth' v-if="!scans.length">{{ $t("scan_monitor.no_scans") }}</div>

        <div class='auto_refresh block fullwidth'>
            <p>{{ $t("auto_refresh.refresh_happening_in") }}<span v-html="current_step_inverted"></span>
            {{ $t("auto_refresh.units") }}<a @click="reload_now()"> ({{ $t("auto_refresh.refresh_now") }})</a></p>
        </div>

    </div>
</template>
{% endverbatim %}

<script>
const autoreload_mixin = {
    /*
    * Autoreloads the 'load' methods after every N seconds.
    * */
    data: {
        // 60 * 1000ms
        refresh_time: 30 * 60 * 1000,

        // Counts down until the next refresh. Allows to add a visualisation on this timer.
        countdown_percentage: 0,

        // countdown every ms (more means more UI changes, slower site)
        countdown_refresh_time: 1000,

        //
        countdown_steps: 0,

        //
        current_step: 1
    },
    methods: {
        init_auto_refresh: function () {
            setInterval(this.lower_countdown, this.countdown_refresh_time);
            this.countdown_steps = this.refresh_time /  this.countdown_refresh_time;
        },
        lower_countdown: function(){
            if (100 / (this.countdown_steps / this.current_step) >= 100) {
                this.reload_now();
            } else {
                this.current_step += 1;
            }
        },
        reload_now: function(){
            this.current_step = 0;
            this.load();
        }
    },
    mounted: function(){
        this.init_auto_refresh();
    },
    computed: {
        current_step_inverted: function(){
            return this.countdown_steps - this.current_step;
        }
    }
};

vueUpload = new Vue({
    i18n,
    name: 'scan_monitor',
    el: '#scan_monitor',
    template: '#scan_monitor_template',
    mixins: [humanize_mixin, autoreload_mixin],
    data: {
        scans: [],
    },
    mounted: function () {
        this.load();
    },
    methods: {
        load: function() {
            this.get_recent_uploads();
        },
        get_recent_uploads: function(){
            fetch(`/data/scan-monitor/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.scans = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
    }
});
</script>
