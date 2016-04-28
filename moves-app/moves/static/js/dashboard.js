/**
 * dashboard.js
 *
 * Displays streaming accelerometric data and classification (if a model is
 * available)
 *
 * @author Chris Rawles
 **/

var socket = io.connect('http://' + document.domain + ':' + location.port);

var scoreResult;
var inScoring = false;
var chartsDrawn = false;

// for displaying confidence
var opacity;
var opacityLowerBound = 0.33;
var opacityUpperBound = 0.8 - opacityLowerBound;

// for testing
runningLocally = false;
if (document.domain == "0.0.0.0") {
    runningLocally = true;
}

document.getElementById("score_result").innerHTML = '<br>'
document.getElementById("channel_name").innerHTML = channel;
    
// for debugging
socket.on('error_message', 
    function (data) {
        console.log(data);
    }
);


// show more confident results with less opacity
function calcOpacity(data) {
    rawOpacity = (data['label_value'] - opacityLowerBound)/opacityUpperBound
    opacity = Math.min(rawOpacity,1)
};

// for updating redis with current data capture stage
var captureJSON = {'channel':channel,
                   'data_type':null,
                   'label':null};

function startScoring() {
    captureJSON['data_type'] = 'scoring';
    // ping scoring application application
    if (runningLocally) {
        url = 'http://0.0.0.0:8082/score/' + channel;
    } else {
        url = 'https://move-score-bot.cfapps.pez.pivotal.io/score/' + channel;
    };
    
    // show label in real time
    getLabel = setInterval( function() {
        $.get( url, function( data ) {
            calcOpacity(data);
            document.getElementById("score_result_font").style.opacity = opacity;
            document.getElementById("score_result").innerHTML = data['label'];//scoreResult;
        });
    },1000);
    // get redis plot data
    getPlotData = setInterval( function() {
        socket.emit('get_streaming_data',{'channel':channel, 'data_type':'scoring'});
    },250);
};

// for when you click the button
function stopScoring() {
    clearInterval(getLabel);
    clearInterval(getPlotData);
    captureJSON['data_type'] = null;
    captureJSON['label'] = null;
    document.getElementById("score_result").innerHTML = '<br>'
};

$('button#toggle_dashboard').bind('click', function() {
    inScoring = !inScoring;
    if (inScoring) {
        startScoring();
        if (!chartsDrawn) { // then draw the chart
            xchart = genChart('xchart',xdata);
            ychart = genChart('ychart',ydata);
            zchart = genChart('zchart',zdata);
            chartsDrawn = true;
        } else {
        xchart.start()
        ychart.start()
        zchart.start()
        };
        document.getElementById('toggle_dashboard').innerHTML = 'Stop';
    }
    else {
        stopScoring();
        xchart.stop()
        ychart.stop()
        zchart.stop()
        document.getElementById('toggle_dashboard').innerHTML = 'Start';
    }
    socket.emit('data_capture_phase',captureJSON);
});

var emptyData = new TimeSeries();
var xdata = new TimeSeries();
var ydata = new TimeSeries();
var zdata = new TimeSeries();
inputStreamingData = channel + '_scoring_data';
var curData;
// update data as it comes in
socket.on(inputStreamingData, 
    function (data) {
        curData = data;
        ax = data['motion']['x'];
        ay = data['motion']['y'];
        az = data['motion']['z'];
        xdata.append(new Date().getTime(),ax);
        ydata.append(new Date().getTime(),ay);
        zdata.append(new Date().getTime(),az);
    });
    
function genChart(name,data) {
    chart = new SmoothieChart({maxValueScale:0.99,grid:{fillStyle:'#ffffff',strokeStyle:'rgba(119,119,119,0.28)',millisPerLine:3000},labels:{fillStyle:'#000000',fontSize:14,precision:0},maxValue:15,minValue:-15})       
    //chart.addTimeSeries(random, { strokeStyle: 'rgba(0, 255, 0, 1)', lineWidth: 4 });
    chart.addTimeSeries(data, {lineWidth:2.5,strokeStyle:'#18bc9c'});
    chart.streamTo(document.getElementById(name), 500); 
    chart.options.enableDpiScaling = false // fix weird scaling error
    return chart
}

