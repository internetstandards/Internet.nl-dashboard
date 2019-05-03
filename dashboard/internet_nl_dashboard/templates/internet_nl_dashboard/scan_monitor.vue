{% verbatim %}
<style>
    .scan {
        width: 32.3%;
        float:left;
        background-color: ghostwhite;
        border: 1px solid silver;
        border-radius: 5px;
        padding: 5px;
        margin: 5px;
    }

    .scan table {
        word-break: keep-all;
    }

    .scan table th {
        padding-top: 0em;
        width: 25%;
    }
    .scan table td {
        width:75%;
    }
    .scan .hide_overflow{

        width: 100%;
        height: 1.8em;
        margin: 0;
        padding: 0;
        overflow: auto;
    }


</style>
<template type="x-template" id="scan_monitor_template">
    <div>
        <h1>{{ $t("scan_monitor.title") }}</h1>
        <p>{{ $t("scan_monitor.intro") }}</p>
        <article class="scan" v-if="scans" v-for="scan in scans">
            <table>
                <tbody>
                <tr>
                    <th colspan="2">
                        <span v-if="scan.finished">✅</span>
                        <span v-if="!scan.finished">🔁</span>

                        {{ $t("scan_monitor.id") }} {{ scan.id }} {{ scan.type }}
                    </th>
                </tr>
                <tr>
                    <th>{{ $t("scan_monitor.list") }}</th><td><div class="hide_overflow">{{ scan.list }}</div></td>
                </tr>
                <tr>
                    <th>{{ $t("scan_monitor.started_on") }}</th><td><div class="hide_overflow"><span :title="scan.started_on">{{ humanize_date(scan.started_on) }}</span></div></td>
                </tr>
                <tr>
                    <th>{{ $t("scan_monitor.finished_on") }}</th>
                    <td v-if="scan.finished"><span :title="scan.finished_on"><div class="hide_overflow">{{ humanize_date(scan.finished_on) }}</div></span></td>
                    <td v-if="!scan.finished">Scan is running</td>
                </tr>
                <tr>
                    <th>{{ $t("scan_monitor.message") }}</th><td><div class="hide_overflow">{{ scan.message }}</div></td>
                </tr>
                <tr>
                    <th>{{ $t("scan_monitor.live") }}</th><td><a :href="scan.status_url" target="_blank">🔖 (open on internet.nl API)</a></td>
                </tr>
                </tbody>
            </table>
        </article>
        <span v-if="!scans.length">{{ $t("scan_monitor.no_scans") }}</span>

        <br style="clear: both">
        <p>
            <div class='auto_refresh'>{{ $t("auto_refresh.refresh_happening_in") }}
                <span v-html="current_step_inverted"></span>
                {{ $t("auto_refresh.units") }}
                <a @click="reload_now()"> ({{ $t("auto_refresh.refresh_now") }})</a>
            </div>
        </p>
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
            fetch(`/data/scan-monitor/`).then(response => response.json()).then(data => {
                this.scans = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
    }
});
</script>
