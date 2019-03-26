{% verbatim %}
<template type="x-template" id="scan_monitor_template">
    <div>
        <h3>{{ $t("scan_monitor.title") }}</h3>
        <p>{{ $t("scan_monitor.intro") }}</p>
        <div class='auto_refresh'>{{ $t("auto_refresh.refresh_happening_in") }} <span v-html="current_step_inverted"></span>{{ $t("auto_refresh.units") }} <a @click="reload_now()"> ({{ $t("auto_refresh.refresh_now") }})</a></div>
        <table v-if="scans">
            <thead>
                <tr>
                    <th>{{ $t("scan_monitor.id") }}</th>
                    <th>{{ $t("scan_monitor.started_on") }}</th>
                    <th>{{ $t("scan_monitor.finished_on") }}</th>
                    <th>{{ $t("scan_monitor.message") }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="scan in scans">
                    <td width="10%">{{ scan.id }}</td>
                    <td width="15%"><span :title="scan.started_on">{{ humanize_date(scan.started_on) }}</span></td>
                    <td width="15%"><span :title="scan.finished_on">{{ humanize_date(scan.finished_on) }}</span></td>
                    <td>{{ scan.message }}</td>
                </tr>
            </tbody>
        </table>
        <span v-if="!scans.length">{{ $t("scan_monitor.no_scans") }}</span>
    </div>
</template>
{% endverbatim %}

<script>

const messages = {
    en: {
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'All scans that have happened for this account are displayed here. It gives an insight into how ' +
                'recent the most current information is. It can also help you with comparisons to select the ideal ' +
                'scan.',
            id: '#',
            started_on: 'Started on',
            finished_on: 'Finished on',
            message: 'Status',
            no_scans: 'No scans have been performed yet.',
        },
        auto_refresh: {
            refresh_happening_in: 'Auto refresh in:',
            units: 's',
            refresh_now: 'refresh now'
        }
    },
    nl: {
        scan_monitor: {
            title: 'Scan monitor',
            intro: 'Alle scans die zijn uitgevoerd voor dit account staan hier. Het geeft een overzicht in hoe recent ' +
                'de data is. Het geeft ook inzicht in of de meest recente scan al is afgerond.',
            id: '#',
            started_on: 'Begonnen',
            finished_on: 'Klaar',
            message: 'Status',
            no_scans: 'Nog geen scans uitgevoerd.',
        },
        auto_refresh: {
            refresh_happening_in: 'Lijst wordt ververst over:',
            units: 's',
            refresh_now: 'ververs nu'
        }
    }
};

const i18n = new VueI18n({
    locale: get_cookie('dashboard_language'),
    fallbackLocale: 'en',
    messages,
});


const autoreload_mixin = {
    /*
    * Autoreloads the 'load' methods after every N seconds.
    * */
    data: {
        // 60 * 1000ms
        refresh_time: 60 * 1000,

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
