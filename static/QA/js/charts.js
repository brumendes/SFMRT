// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart', ], 'language': 'pt'});

google.charts.setOnLoadCallback(draw);

function draw() {
    if (medidas.length > 1) {
        drawChart();
    }
};

function getMedidas() {
    var data = new google.visualization.DataTable();
    data.addColumn({ type: 'date', label: 'Data'});
    data.addColumn({ type: 'number', label: 'Medida'});
    data.addColumn({ type: 'string', role: 'style'});
    data.addColumn({ type: 'number', label: 'Referência'});
    data.addColumn({ type: 'number', id: 'ref_main', role: 'interval' });
    data.addColumn({ type: 'number', id: 'ref_main', role: 'interval' });
    data.addColumn({ type: 'number', id: 'ref_main', role: 'interval' });
    data.addColumn({ type: 'number', id: 'ref_main', role: 'interval' });

    // Convert to date format
    for(var i = 0; i < medidas.length; i++){
        medidas[i][0] = new Date(medidas[i][0]);
    };

    data.addRows(medidas);
    data.sort([{column: 0}]);

    return data;
};

function drawChart() {
    var data = getMedidas();

    // Scatter chart
    var options = {
        hAxis: {
            'title': 'Data',
        },
        vAxis: {
            'title': 'Taxa de dose',
            'minValue': 0.9,
            'maxValue': 1.1,
            'format': 'decimal',
        },
        height: '400',
        width: '100%',
        legend: {
            'position': 'none',
        },
        interpolateNulls: 'True',
        explorer: {
            'actions': ['dragToZoom', 'rightClickToReset'],
            'keepInBounds': 'True',
            'maxZoomIn': '0.05',
            },
        interval: {
            'ref_main': { 'style':'area', 'color':'green', 'fillOpacity': 0.10},
        },
        seriesType: 'scatter',
        series: {
            0: {type: 'scatter', color: 'green', pointShape: 'circle', pointSize: '5'},
            1: {type: 'line', color: 'gray', lineDashStyle: [4, 4], connectSteps: 'false'},
            // 1: {type: 'scatter', pointsVisible: 'false', lineDashStyle: [4, 4], lineWidth: 0.5, color: 'gray', connectSteps: 'false'},
        },
    };

    var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));

    google.visualization.events.addListener(chart, 'error', function (googleError) {
        google.visualization.errors.removeError(googleError.id);
    });

    chart.draw(data, options);
};

$(window).resize(function(){
  draw();
});