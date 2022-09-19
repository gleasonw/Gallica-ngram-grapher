export default function generateOptions(series, settings) {
    let options = {
        plotOptions:{
            series: {
                cursor: 'pointer',
                point: {
                  events: {
                    click: function (e) {
                      console.log(this);
                      console.log(e);
                    }
                  }
                }
              }
        },
        legend: {
            dateTimeLabelFormats: {
                month: '%b',
                year: '%Y'
            },
            align: 'left',
            verticalAlign: 'top',
            borderWidth: 0
        },
        title: {
            text: null
        },
        yAxis: {
            title: {
                text: 'Mentions'
            }
        },
        series: series,
        tooltip: {
            shared: true,
            crosshairs: true,
        },
    };
    if (settings.timeBin === 'year') {
        formatYearOptions()
    } else if (settings.timeBin === 'month') {
        formatYearMonOptions()
    } else {
        formatYearMonDayOptions()
    }

    function formatYearOptions() {
        options.plotOptions = {
            ...options.plotOptions,
            line: {
                marker: {
                    enabled: false
                }
            }
        }
        options.xAxis = {
            type: 'line'
        }
    }

    function formatYearMonOptions() {
        options.xAxis = {
            type: 'datetime',
            dateTimeLabelFormats: {
                month: '%b',
                year: '%Y'
            }
        }
    }

    function formatYearMonDayOptions() {
        options.xAxis = {type: 'datetime'}
    }

    return options;
}
