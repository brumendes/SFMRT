// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart', ], 'language': 'pt'});

google.charts.setOnLoadCallback(draw);

function draw() {
    drawChart();
};

function getMedidas() {
    var data = new google.visualization.DataTable();
    data.addColumn({ type: 'date', label: 'Data', role: 'domain' });
    data.addColumn({ type: 'string', label: 'Energia', role: 'scope' });
    data.addColumn({ type: 'number', label: 'Valor', role: 'data' });
    data.addColumn({ type: 'string', role: 'style'});
    data.addColumn({ type: 'number', label: 'Referência', role: 'data'});
    data.addColumn({ type: 'number', id: 'Referência_inf', role: 'interval' });
    data.addColumn({ type: 'number', id: 'Referência_sup', role: 'interval' });

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
        height: '500',
        width: '100%',
        legend: {
            'position': 'none',
        },
        explorer: {
            'actions': ['dragToZoom', 'rightClickToReset'],
            'keepInBounds': 'True',
            'maxZoomIn': '0.05',
            },
        intervals: {
            'style': 'area',
             'color': 'green',
             },
        series: {
            0: {type: 'scatter', color: 'green', pointShape: 'circle', pointSize: '5'},
            1: {type: 'line', pointsVisible: 'false', lineDashStyle: [4, 4], lineWidth: 0.5, color: 'gray', connectSteps: 'false'},
        },
    };

    var chart = new google.visualization.ComboChart(document.getElementById('chart_div'));
    chart.draw(data, options);
};

$(window).resize(function(){
  draw();
});