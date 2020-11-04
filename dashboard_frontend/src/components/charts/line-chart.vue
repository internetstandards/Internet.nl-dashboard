<script>
import Chart from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import chart_mixin from './chart_mixin.vue'

// this prevents the legend being written over the 100% scores
Chart.Legend.prototype.afterFit = function() {
    this.height = this.height + 20;
};

export default {
    mixins: [chart_mixin],
    plugins: [ChartDataLabels],
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
                            formatter: function(value) {
                                if (value.is_selected) {
                                    return `#${value.report}\n${Math.round(value.y)}%`;
                                } else {
                                    // https://github.com/internetstandards/Internet.nl-dashboard/issues/37
                                    return Math.round(value.y) + '%';
                                }
                            }
                        }
                    },
                    legend: {
                        display: true
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: this.$i18n.t(this.translation_key + '.title')
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,

                        // add the Z axis to the data, is harder, so (n) is unclear...
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
                                labelString: this.$i18n.t(this.translation_key + '.month'),
                            }
                        }],
                        yAxes: [{
                            display: true,
                            stacked: false,
                            ticks: {
                                padding: 20,
                                min: 0,
                                max: 100,
                                callback: function(label) {
                                    return label + '%';
                                }
                            },
                            scaleLabel: {
								display: true,
								labelString: this.$i18n.t(this.translation_key + '.yAxis_label'),
							},
                        }]
                    }
                }
            });
        },

        /*
        * [
              {
                "id": 3,
                "name": "testsites",
                "data": [
                  {
                    "date": "2020-01-07",
                    "urls": 3,
                    "average_internet_nl_score": 87.33
                  },
                  {
                    "date": "2020-01-07",
                    "urls": 3,
                    "average_internet_nl_score": 87.33
                  },
                  {
                    "date": "2020-01-07",
                    "urls": 3,
                    "average_internet_nl_score": 87.33
                  }
                ]
              },
        * */
        renderData: function(){
            let data = this.chart_data;

            let labels = Array();

            // There will be a large assortment of moment in time. These are added in random order, charts.js fixes it
            data.forEach((item) => {
                for(let i=0; i<item.data.length; i++){
                    labels.push(item.data[i].date);
                }
            });

            // the trick to time series is that you can add data with both an x and y.
            // see: view-source:https://www.chartjs.org/samples/latest/scales/time/line.html
            this.chart.data.labels = labels;

            let datasets = [];
            let colorset = 0;
            data.forEach((item) => {

                 let line_data = [];
                 item.data.forEach((item_data) => {
                    line_data.push({
                        x: item_data.date,
                        y: item_data.average_internet_nl_score,
                        z: item_data.urls,
                        is_selected: this.selected_report_ids.includes(item_data.report),
                        report: item_data.report})
                 });

                 let line_dataset =
                    {
                        // Each report has their own set of dates and such, there will be many gaps.
                        spanGaps: true,
                        label: item.name,
                        data: line_data,
                        // backgrounds do not work with multiple sets, only lines.
                        fill: false,
                        backgroundColor: this.color_scheme.incremental[colorset].background,
                        borderColor: this.color_scheme.incremental[colorset].border,
                        borderWidth: 3,
                        lineTension: 0,
                    };

                 colorset += 1;
                 datasets.push(line_dataset);
            });

            this.chart.data.datasets = datasets;

            this.chart.update();
        },
        renderTitle: function(){
            this.chart.options.title.text = this.title;
        },
    }
}
</script>
