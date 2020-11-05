<style scoped>
.websitetest table th {
    word-break: keep-all;
}

h4 {
    font-size: 1.0em;
}

.monitor-block {
    background-color: white;
    background: linear-gradient(180deg, #00BFD6 0%, #00BFD6 3em, white 3em, rgba(255,255,255,1) 100%);
    border-radius: 4px;
}

.monitor-block h2 {
    color: white;
    padding-left: 0.4em;
    font-size: 1.2em;
    display: inline-block;
    margin: 0px;
}

</style>
<template>
    <div style="width: 100%;">
        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>
            <p>{{ $t("intro") }}</p>

            <autorefresh :visible="true" :callback="load" :refresh_per_seconds="60"></autorefresh>
        </div>

        <div class="wrap" v-if="scans">
            <div class="block monitor-block" v-for="scan in scans" :key="scan.id">
                <div class="wrapper">
                    <h2>
                    <span v-if="scan.state === 'finished'">✅</span>
                    <span v-if="scan.state === 'cancelled'">⭕</span>
                    <span v-if="!['finished', 'cancelled'].includes(scan.state)">
                        <img width="15" style="border-radius: 50%"
                             src="/static/images/vendor/internet_nl/probe-animation.gif"></span>
                    &nbsp; {{ scan.type }} {{ $t("id") }}{{ scan.id }}</h2><br>
                    <br>
                    <template v-if="scan.finished && (scan.state !== 'cancelled')">
                        <template v-if="scan.last_report_id">
                            📊
                            <router-link :to="{ name: 'numbered_report', params: { report: scan.last_report_id }}">
                                {{ $t("open_report") }}
                            </router-link>
                            <br>
                            <br>
                        </template>
                        <template v-if="!scan.last_report_id">
                            📊 {{ $t("report_is_being_generated") }}<br>
                            <br>
                        </template>
                    </template>
                    📘
                    <router-link :to="{ name: 'numbered_lists', params: { list: scan.list_id }}">{{
                            scan.list
                        }}
                    </router-link>
                    <br>
                    <br>
                    <template v-if="['finished', 'cancelled'].includes(scan.state)">
                        <b v-if="scan.state === 'cancelled'">{{ $t("cancelled_on") }}</b>
                        <b v-if="scan.state === 'finished'">{{ $t("finished_on") }}</b> <br>
                        <span :title="scan.finished_on">{{
                                humanize_date(scan.finished_on)
                            }},<br>{{ humanize_relative_date(scan.finished_on) }}</span><br><br>
                    </template>
                    <b>{{ $t("runtime") }}</b><br>
                    {{ humanize_duration(scan.runtime) }}<br>
                    <br>
                    <template v-if="!['finished', 'cancelled'].includes(scan.state)">
                        <b>{{ $t("message") }}</b>
                        <p>{{ scan.state }}</p>
                        <b>{{ $t("last_check") }}</b><br>
                        <span :title="scan.last_check">{{
                                humanize_date(scan.last_check)
                            }},<br>{{ humanize_relative_date(scan.last_check) }}</span><br>
                        <br>
                    </template>
                    <b>{{ $t("started_on") }}</b><br>
                    <span :title="scan.started_on">{{
                            humanize_date(scan.started_on)
                        }},<br>{{ humanize_relative_date(scan.started_on) }}</span><br>
                    <br>

                    <collapse-panel :title='$t("scan history")'>
                        <div slot="content">
                            <ul style="font-size: 0.7em;">
                                <li v-for="log_item in scan.log" :key="log_item.id">
                                    - {{ log_item.state }}, {{ humanize_relative_date(log_item.at_when) }}
                                </li>
                            </ul>
                            <template v-if="!scan.finished">
                                <button @click="start_stop_scan(scan)">{{ $t("stop_scan") }}</button>
                            </template>
                        </div>
                    </collapse-panel>

                    <br>

                    <template v-if="scan.status_url">
                        🔖
                        <template v-if="scan.state === 'finished'">
                            <a :href="scan.status_url + '/results'" target="_blank">{{ $t("open_in_api") }}</a>
                        </template>
                        <template v-else>
                            <a :href="scan.status_url" target="_blank">{{ $t("open_in_api") }}</a>
                        </template>
                        <br>
                    </template>
                </div>
            </div>
        </div>

        <div class='block fullwidth' v-if="!scans.length">{{ $t("no_scans") }}</div>

        <internet_nl_modal v-if="show_stop_scan" @close="stop_stop_scan()">
            <h3 slot="header">🛑 {{ $t("cancel.are_you_sure") }}</h3>
            <div slot="body">

                <server-response :response="stop_scan_server_response"></server-response>
                <div class="block" style="width: 100%">
                    <div class="wrapper">
                        <span><img width="15" style="border-radius: 50%"
                                   src="/static/images/vendor/internet_nl/probe-animation.gif"></span> &nbsp;
                        <b>{{ stop_scan.type }} {{ $t("id") }}{{ stop_scan.id }}</b><br>
                        <br>
                        📘 {{ stop_scan.list }}<br>
                        <br>
                        <b>{{ $t("runtime") }}</b><br>
                        {{ humanize_duration(stop_scan.runtime) }}<br>
                        <br>
                        <b>{{ $t("message") }}</b>
                        <p>{{ stop_scan.state }}</p>
                        <b>{{ $t("last_check") }}</b><br>
                        <span :title="stop_scan.last_check">{{
                                humanize_date(stop_scan.last_check)
                            }},<br>{{ humanize_relative_date(stop_scan.last_check) }}</span><br>
                        <br>
                        <b>{{ $t("started_on") }}</b><br>
                        <span :title="stop_scan.started_on">{{
                                humanize_date(stop_scan.started_on)
                            }},<br>{{ humanize_relative_date(stop_scan.started_on) }}</span><br>
                    </div>
                </div>

            </div>
            <div slot="footer">
                <button class="altbutton" @click="stop_stop_scan()">{{ $t("cancel.cancel") }}</button>
                <button class="modal-default-button defaultbutton" @click="confirm_stop_scan()">{{
                        $t("cancel.ok")
                    }}
                </button>
            </div>
        </internet_nl_modal>

    </div>
</template>


<script>
export default {
    name: 'scan_monitor',

    data: function () {
        return {
            scans: [],

            // cancellations:
            show_stop_scan: false,
            stop_scan: null, // the scan that will be cancelled when you hit OK
            stop_scan_server_response: "",
        }
    },
    mounted: function () {
        this.load();
    },
    methods: {
        load: function () {
            this.update_scan_data();
        },
        update_scan_data: function () {
            fetch(`${this.$store.state.dashboard_endpoint}/data/scan-monitor/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.scans = data;
                this.$store.commit("update_scan_monitor_data", data);
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

        start_stop_scan: function (scan) {
            this.stop_scan = scan;
            this.show_stop_scan = true;
        },
        stop_stop_scan: function () {
            this.stop_scan = null;
            this.show_stop_scan = false;
        },
        confirm_stop_scan: function () {
            this.asynchronous_json_post(
                '/data/scan/cancel/', {'id': this.stop_scan.id}, () => {
                    this.update_scan_data();
                    // if already cancelled...
                    this.stop_stop_scan();
                }
            );
        }
    }
}
</script>
<i18n>
{
    "en": {
        "title": "Scan monitor",
        "intro": "All scans that have happened for this account are displayed here. It gives an insight into how recent the most current information is. It can also help you with comparisons to select the ideal scan.",
        "id": " scan #",
        "type": "Type",
        "list": "List",
        "started_on": "Started",
        "finished_on": "Finished",
        "cancelled_on": "Cancelled",
        "message": "Status",
        "live": "API",
        "no_scans": "No scans have been performed yet.",
        "report": "Report",
        "runtime": "Runtime",
        "open_in_api": "Open on internet.nl API",
        "open_report": "Open report",
        "last_check": "Last status update",
        "report_is_being_generated": "Report is being generated.",
        "processing_results": "Processing results.",
        "scan history": "Scan Progress",
        "stop_scan": "Stop scan",
        "cancel": {
            "are_you_sure": "Do you want to cancel this scan?",
            "scan_id": "scan",
            "list": "list",
            "ok": "Stop scan",
            "cancel": "Continue scanning"
        }
    },
    "nl": {
        "title": "Scan monitor",
        "intro": "Alle scans die zijn uitgevoerd voor dit account staan hier. Het geeft een overzicht in hoe recent de data is. Het geeft ook inzicht in of de meest recente scan al is afgerond.",
        "id": "scan #",
        "type": "Soort",
        "list": "Lijst",
        "started_on": "Gestart",
        "finished_on": "Klaar",
        "cancelled_on": "Gestopt",
        "message": "Status",
        "live": "API",
        "no_scans": "Nog geen scans uitgevoerd.",
        "report": "Rapport",
        "runtime": "Looptijd",
        "open_in_api": "Open internet.nl API resultaat",
        "open_report": "Open rapport",
        "last_check": "Laatste status update",
        "report_is_being_generated": "Report wordt gemaakt.",
        "processing_results": "Resultaten worden verwerkt.",
        "scan history": "Voortgang van deze scan",
        "stop_scan": "Stop scan",
        "cancel": {
            "are_you_sure": "Deze scan stoppen?",
            "scan_id": "scan",
            "list": "lijst",
            "ok": "Stop scan",
            "cancel": "Blijf scannen"
        }
    }
}
</i18n>