<script>
// done: place different labels  (add info about date in image)
Vue.component('line-chart', {
    mixins: [chart_mixin],

    methods: {
        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'line',
                data: {
                    datasets: []
                },
                options: {
                    plugins:{
                        datalabels: {
                            color: '#262626',
                            display: true,
                            clamp: true, // always shows the number, also when the number 100%
                            anchor: 'end', // show the number at the top of the bar.
                            align: 'end', // shows the value outside of the bar,
                            // format as a percentage
                            formatter: function(value, context) {
                                // https://github.com/internetstandards/Internet.nl-dashboard/issues/37
                                return Math.round(value )+ '%';
                            }
                        }
                    },
                    legend: {
                        display: false
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: i18n.t(this.translation_key + '.title')
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    layout: {
                        padding: {
                            left: 0,
                            right: 20,
                            top: 0,
                            bottom: 0
                        }
                    },
                    scales: {
                        xAxes: [{
                            barPercentage: 0.9,
                            categoryPercentage: 0.55,

                            display: true,
                            type: 'time',
                            distribution: 'linear',
                            time: {
                                unit: 'month'
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'Month'
                            }
                        }],
                        yAxes: [{
                            display: true,
                            stacked: false,
                            ticks: {
                                padding: 20,
                                min: 0,
                                max: 100,
                                callback: function(label, index, labels) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
								labelString: i18n.t(this.translation_key + '.yAxis_label'),
							},
                        }]
                    }
                }
            });
        },

        renderData: function(){
            let data = this.chart_data;

            let labels = Array();
            let high = Array();
            let medium = Array();
            let low = Array();
            let ok = Array();
            let not_ok = Array();
            let pct_ok = Array();
            let pct_not_ok = Array();
            let average_internet_nl_score = [];

            for(let i=0; i<data.length; i++){
                labels.push(data[i].date);
                high.push(data[i].high);
                medium.push(data[i].medium);
                low.push(data[i].low);
                ok.push(data[i].ok);
                not_ok.push(data[i].not_ok);
                pct_ok.push(data[i].pct_ok);
                pct_not_ok.push(data[i].pct_not_ok);
                average_internet_nl_score.push(data[i].average_internet_nl_score);
            }

            this.chart.data.labels = labels;
            this.chart.data.datasets = [
                {
                    label: '# OK',
                    data: ok,
                    backgroundColor: this.color_scheme.ok_background,
                    borderColor: this.color_scheme.ok_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('ok')
                },
                {
                    label: '# Not OK',
                    data: not_ok,
                    backgroundColor: this.color_scheme.high_background,
                    borderColor: this.color_scheme.high_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('not_ok')
                },
                {
                    label: '% OK',
                    data: pct_ok,
                    backgroundColor: this.color_scheme.incremental[1].background,
                    borderColor: this.color_scheme.incremental[1].border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('pct_ok')
                },
                {
                    label: i18n.t(this.translation_key + '.average_internet_nl_score'),
                    data: average_internet_nl_score,
                    backgroundColor: this.color_scheme.incremental[0].background,
                    borderColor: this.color_scheme.incremental[0].border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('average_internet_nl_score')
                },
                {
                    label: '% NOT OK',
                    data: pct_not_ok,
                    backgroundColor: this.color_scheme.high_background,
                    borderColor: this.color_scheme.high_border,
                    borderWidth: 1,
                    lineTension: 0,
                    hidden: !this.axis.includes('pct_not_ok')
                },
            ];

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});
</script>
