{% verbatim %}
<style>
    .websitetest table th {
        word-break: keep-all;
    }
</style>
<template type="x-template" id="scan_monitor_template">
    <div style="width: 100%;">
        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>
            <p>{{ $t("intro") }}</p>
        </div>

        <autorefresh :visible="true" :callback="load"></autorefresh>

        <div class="wrap">
            <div class="block" v-if="scans" v-for="scan in scans">
                <div class="wrapper">
                    <span v-if="scan.finished">✅</span>
                    <span v-if="!scan.finished"><img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif"></span>
                    <b>{{ scan.type }} {{ $t("id") }}{{ scan.id }}</b><br>
                    <br>
                    <template v-if="scan.finished">
                        <template v-if="scan.last_report_id">
                            📊 <router-link :to="{ name: 'numbered_report', params: { report: scan.last_report_id }}">{{ $t("open_report") }}</router-link><br>
                            <br>
                        </template>
                        <template v-if="!scan.last_report_id">
                            📊 {{ $t("report_is_being_generated") }}<br>
                            <br>
                        </template>
                    </template>
                    📘 <router-link :to="{ name: 'numbered_lists', params: { list: scan.list_id }}">{{ scan.list }}</router-link><br>
                    <br>
                    <template v-if="scan.finished">
                        <b>{{ $t("finished_on") }}</b><br>
                        <span :title="scan.finished_on">{{ humanize_date(scan.finished_on) }},<br>{{ humanize_relative_date(scan.finished_on) }}</span><br>
                        <br>
                    </template>
                    <b>{{ $t("runtime") }}</b><br>
                        {{ humanize_duration(scan.runtime) }}<br>
                        <br>
                    <template v-if="!scan.finished">
                        <b>{{ $t("message") }}</b>
                        <p>{{ scan.state }}</p>
                        <b>{{ $t("last_check") }}</b><br>
                        <span :title="scan.last_check">{{ humanize_date(scan.last_check) }},<br>{{ humanize_relative_date(scan.last_check) }}</span><br>
                        <br>
                    </template>
                    <b>{{ $t("started_on") }}</b><br>
                    <span :title="scan.started_on">{{ humanize_date(scan.started_on) }},<br>{{ humanize_relative_date(scan.started_on) }}</span><br>
                    <br>


                    <div class="testresult" style="padding-left: 0px !important;">
                        <h3 class="panel-title" >
                            <a href="" aria-expanded="false">
                                <span class="visuallyhidden">-:</span>
                                {{ $t("scan history") }}
                                <span class="pre-icon visuallyhidden"></span>
                                <span class="icon"><img src="/static/images/vendor/internet_nl/push-open.png" alt=""></span>
                            </a>
                        </h3>
                        <div class="panel-content" style="font-size: 0.7em;">
                            <ul>
                                <li v-for="log_item in scan.log">
                                    - {{ log_item.state }}, {{ humanize_relative_date(log_item.at_when) }}
                                </li>
                            </ul>
                        </div>
                    </div>
                    <br>

                    🔖 <a :href="scan.status_url" target="_blank">{{ $t("open_in_api") }}</a><br>
                </div>
            </div>
        </div>

        <div class='block fullwidth' v-if="!scans.length">{{ $t("no_scans") }}</div>

    </div>
</template>


<script>
const ScanMonitor = Vue.component('ScanMonitor', {
    i18n: {
        messages: {
            en: {
                title: 'Scan monitor',
                intro: 'All scans that have happened for this account are displayed here. It gives an insight into how ' +
                    'recent the most current information is. It can also help you with comparisons to select the ideal ' +
                    'scan.',
                id: ' scan #',
                type: 'Type',
                list: 'List',
                started_on: 'Started',
                finished_on: 'Finished',
                message: 'Status',
                live: 'API',
                no_scans: 'No scans have been performed yet.',
                report: 'Report',
                runtime: 'Runtime',
                open_in_api: 'Open on internet.nl API',
                open_report: 'Open report',
                last_check: 'Last status update',
                report_is_being_generated: 'Report is being generated.',
                processing_results: 'Processing results.',
                "scan history": "Scan Progress",
            },
            nl: {
                title: 'Scan monitor',
                intro: 'Alle scans die zijn uitgevoerd voor dit account staan hier. Het geeft een overzicht in hoe recent ' +
                    'de data is. Het geeft ook inzicht in of de meest recente scan al is afgerond.',
                id: 'scan #',
                type: 'Soort',
                list: 'Lijst',
                started_on: 'Gestart',
                finished_on: 'Klaar',
                message: 'Status',
                live: 'API',
                no_scans: 'Nog geen scans uitgevoerd.',
                report: 'Rapport',
                runtime: 'Looptijd',
                open_in_api: 'Open internet.nl API resultaat',
                open_report: 'Open rapport',
                last_check: 'Laatste status update',
                report_is_being_generated: 'Report wordt gemaakt.',
                processing_results: 'Resultaten worden verwerkt.',
                "scan history": "Voortgang van deze scan",
            }
        }
    },
    name: 'scan_monitor',
    template: '#scan_monitor_template',
    mixins: [humanize_mixin],
    data: function() {
        return {
            scans: [],
        }
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
                this.$nextTick(() => {accordinate();});
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
    }
});
</script>
{% endverbatim %}