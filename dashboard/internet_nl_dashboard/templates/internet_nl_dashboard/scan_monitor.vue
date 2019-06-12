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

        <autorefresh :visible="true"  :callback="load"></autorefresh>
    </div>
</template>


<script>
vueScanMonitor = new Vue({
    i18n,
    name: 'scan_monitor',
    el: '#scan_monitor',
    template: '#scan_monitor_template',
    mixins: [humanize_mixin],
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
{% endverbatim %}