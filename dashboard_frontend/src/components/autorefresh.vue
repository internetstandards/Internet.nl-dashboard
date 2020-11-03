<template>
    <div v-if='visible' style='margin-bottom: 0 !important;'>
        <button @click="reload_now()">🔁 {{ $t("refresh_now") }}</button>
        {{ $t("refresh_happening_in") }} <span v-html="this.current_step_inverted"></span>
        {{ $t("units") }}
    </div>
</template>
<script>
export default {
    data: function () {
        return {
            // 60 * 1000ms
            refresh_time: this.refresh_per_seconds * 1000,

            // Counts down until the next refresh. Allows to add a visualisation on this timer.
            countdown_percentage: 0,

            // countdown every ms (more means more UI changes, slower site)
            countdown_refresh_time: 1000,

            //
            countdown_steps: 0,

            //
            current_step: 1,

            // make sure that the components are removed when navigation changes:
            refresh_interval: undefined
        }
    },

    props: {
        callback: {
            type: Function,
            default: null
        },
        visible: {
            type: Boolean,
            default: true,
        },
        refresh_per_seconds: {
            type: Number,
            default: 600
        }
    },

    methods: {
        init_auto_refresh: function () {
            // https://stackoverflow.com/questions/49424507/vue-router-creates-always-a-new-component-instance#49424657
            this.refresh_interval = setInterval(this.lower_countdown, this.countdown_refresh_time);
            this.countdown_steps = this.refresh_time / this.countdown_refresh_time;
        },
        lower_countdown: function () {
            if (100 / (this.countdown_steps / this.current_step) >= 100) {
                this.reload_now();
            } else {
                this.current_step += 1;
            }
        },
        reload_now: function () {
            this.current_step = 0;
            this.callback();
        }
    },
    mounted: function () {
        this.init_auto_refresh();
    },
    beforeDestroy: function () {
        // Cleanup interval, see init_auto_refresh.
        clearInterval(this.refresh_interval);
    },
    computed: {
        current_step_inverted: function () {
            return this.countdown_steps - this.current_step;
        }
    }
}
</script>
<i18n>
{
    "en": {
        "refresh_happening_in": "Auto refresh in:",
        "units": "s",
        "refresh_now": "refresh data now"
    },
    "nl": {
        "refresh_happening_in": "Gegevens worden ververst over:",
        "units": "s",
        "refresh_now": "ververs gegevens nu"
    }
}
</i18n>