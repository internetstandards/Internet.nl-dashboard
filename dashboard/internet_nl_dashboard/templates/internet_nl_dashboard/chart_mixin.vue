<script>
const chart_mixin = {

    props: {
        chart_data: {type: Array, required: true},
        axis: {type: Array, required: false},
        color_scheme: {type: Object, required: false},
        title: {type: String, required: false},
        translation_key: {type: String, required: false},
        accessibility_text: {type: String, required: true},
        show_dynamic_average: {type: Boolean, required: false},
        only_show_dynamic_average: {type: Boolean, required: false},
    },
    data: function () {
        return {
            chart: {}
        }
    },
    render: function(createElement) {
        return createElement(
            'canvas',
            {
                ref: 'canvas',

                // Improve accessibility: https://www.chartjs.org/docs/latest/general/accessibility.html
                // Using createElement features: https://vuejs.org/v2/guide/render-function.html#createElement-Arguments
                attrs: {
                    role: "img",
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
    created(){
        // When the chart data is downloaded, it might be that a ton of stuff is processed. To prevent
        // too many renders, we slow the chart building a bit by debouncing it.
        // This also prevents some of the "me.getDatasetMeta(...).controller is null" errors in charts.js (nov 2019)
        // You cannot add a debounce on a watch:
        // https://stackoverflow.com/questions/47172952/vuejs-2-debounce-not-working-on-a-watch-option
        this.unwatch = this.$watch('chart_data', _.debounce((newVal) => {
            this.renderData();
        }, 300), {
            // Note that you don’t need to do so to listen for in-Array mutations as they won't happen and the
            // arrays are too complex and big.
            deep: false
        })
    },
    watch: {

        axis: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },
        show_dynamic_average: function(){
            this.renderData();
        },
        only_show_dynamic_average: function(){
            this.renderData();
        },
        title: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderTitle();
            }
        },

        // Supports changing the colors of this graph ad-hoc.
        // charts.js is not reactive.
        color_scheme: function(new_value, old_value){
            if (!this.arraysEqual(old_value, new_value)) {
                this.renderData();
            }
        },
    }
};
</script>
