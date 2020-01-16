<script>
Vue.component('percentage-bar-chart', {
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
                            clamp: true, // always shows the number, also when the number 100%
                            anchor: 'end', // show the number at the top of the bar.
                            align: 'end', // shows the value outside of the bar,
                            display: true,
                            // format as a percentage
                            formatter: function(value, context) {
                                // The data labels should be rounded, while the rest of the data on hover etc is not.
                                // https://github.com/internetstandards/Internet.nl-dashboard/issues/37
                                return Math.round(value )+ '%';
                            }
                        }
                    },
                    legend: {
                        display: true,
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
            // console.log("Rendering bar chart.");

            // prevent the grapsh from ever growing (it's called twice at first render)
            this.chart.data.axis_names = [];
            this.chart.data.labels = [];
            this.chart.data.datasets = [];

            for(let i=0; i < this.chart_data.length; i++){
                // console.log(`Rendering set ${i}`);

                // it's possible the report data is not yet in, but the item in the array has been made.
                // so well:
                if (this.chart_data[i] === undefined)
                    return;

                let data = this.chart_data[i].calculation.statistics_per_issue_type;

                if (data === undefined) {
                    // nothing to show
                    console.log('nothing to show, probably because not all reports in compare charts are in...');
                    this.chart.data.axis_names = [];
                    this.chart.data.labels = [];
                    this.chart.data.datasets = [];
                    this.chart.update();
                    return;
                }

                let axis_names = [];
                let labels = [];
                let chartdata = [];
                let average = 0;

                this.axis.forEach((ax) => {
                    if (ax in data) {
                        if (!this.only_show_dynamic_average) {
                            labels.push(i18n.t(ax));
                            axis_names.push(ax);
                            chartdata.push(data[ax].pct_ok);
                        }
                        average += parseFloat(data[ax].pct_ok);
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
                    backgroundColor: this.color_scheme.incremental[i].background,
                    borderColor: this.color_scheme.incremental[i].border,
                    borderWidth: 1,
                    lineTension: 0,
                    label: `${this.chart_data[i].calculation.name} ${moment(this.chart_data[i].at_when).format('LL')} n=${this.chart_data[i].total_urls}`,
                });

            }

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
});
</script>
