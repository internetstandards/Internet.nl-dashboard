<script>
Vue.component('cumulative-percentage-bar-chart', {
    i18n,
    mixins: [chart_mixin, humanize_mixin],

    methods: {

        buildChart: function(){
            let context = this.$refs.canvas.getContext('2d');
            this.chart = new Chart(context, {
                type: 'bar',
                data: {},
                options: {

                    // can prevent data falling off the chart.
                    layout: {
                        padding: {
                            left: 0,
                            right: 0,
                            top: 0,
                            bottom: 0
                        }
                    },
                    plugins:{
                        datalabels: {
                            color: '#262626',
                            display: true,  // auto hides overlapping labels, true always shows them.
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
                        display: false,
                        position: 'top',
                        labels: {
                            padding: 15,
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        position: 'top',
                        display: true,
                        text: this.title,
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    },
                    // this is now a percentage graph.
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: 100,
                                callback: function(label, index, labels) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
								labelString: i18n.t(this.translation_key + '.yAxis_label')
							},
                        }]
				    },
                    onClick: (event, item) => {
                        if (item[0] === undefined) {
                            return;
                        }

                        if (item[0]._chart.tooltip._lastActive[0] === undefined){
                            return;
                        }

                        // todo: handle zooming, this is optional / a nice to have.
                        let localChart = item[0]._chart;
                        let activeIndex = localChart.tooltip._lastActive[0]._index;
                        let clickCoordinates = Chart.helpers.getRelativePosition(event, localChart.chart);
                        if (clickCoordinates.y >= 0) { //custom value, depends on chart style,size, etc
                            this.$emit('bar_click', localChart.data.axis_names[activeIndex]);
                            // console.log("clicked on " + localChart.data.labels[activeIndex]);
                        }
                    }
                }
            });
        },
        renderData: function(){
            // prevent the grapsh from ever growing (it's called twice at first render)
            this.chart.data.axis_names = [];
            this.chart.data.labels = [];
            this.chart.data.datasets = [];

            let cumulative_axis_data = {};

            for(let i=0; i < this.chart_data.length; i++) {

                // it's possible the report data is not yet in, but the item in the array has been made.
                // so well:
                if (this.chart_data[i] === undefined)
                    return;

                let data = this.chart_data[i].statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    this.chart.data.axis_names = [];
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        if (!Object.keys(cumulative_axis_data).includes(ax)) {
                            cumulative_axis_data[ax] = 0
                        }
                        cumulative_axis_data[ax] += data[ax].pct_ok
                    }
                });

            }

            let data = this.chart_data[0].statistics_per_issue_type;
            let axis_names = [];
            let labels = [];
            let chartdata = [];
            let average = 0;

            this.axis.forEach((ax) => {
                if (ax in data) {
                    if (!this.only_show_dynamic_average) {
                        labels.push(i18n.t(ax));
                        axis_names.push(ax);
                        chartdata.push((Math.round(cumulative_axis_data[ax] / this.chart_data.length * 100)) / 100);
                    }
                    // toFixed delivers some 81.32429999999999 results, which is total nonsense.
                    average += (Math.round(cumulative_axis_data[ax] / this.chart_data.length * 100)) / 100;
                }
            });

            // add the average of all these to the report, not as a line, but as an additional bar
            if ((labels.length > 1 && this.show_dynamic_average) || this.only_show_dynamic_average) {
                chartdata.push(Math.round((average / this.axis.length) * 100) / 100);
                labels.push(i18n.t(this.translation_key + '.average'));
                axis_names.push("Average");
            }

            this.chart.data.axis_names = axis_names;
            this.chart.data.labels = labels;
            this.chart.data.datasets.push({
                data: chartdata,
                backgroundColor: this.color_scheme.incremental[0].background,
                borderColor: this.color_scheme.incremental[0].border,
                borderWidth: 1,
                lineTension: 0,
                label: `${this.chart_data[0].calculation.name} ${moment(this.chart_data[0].at_when).format('LL')}`,
            });

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});
</script>
