var socket = io.connect('http://' + document.domain + ':' + location.port);
var channel;
var recordTime = 20*1000
var waitToRecord = 1*1000
var trainSetLen = 0;
var dataSuccesfullyStored = false;
var zdata = new TimeSeries();
var curDataUrl;
var dTime;
var channelExists = false;

// for testing
runningLocally = false;
if (document.domain == "0.0.0.0") {
    runningLocally = true;
}

// update redis data type to training, so it is stored
// after recordTime, change data_type to null - i.e stop storing it
function setDataType(labelName,recordTime,elementID) { 
    captureJSON = {'channel':channel,
                   'data_type':'training',
                   'label':labelName};
    socket.emit('data_capture_phase',captureJSON);

    setTimeout(function() {
        captureJSON['data_type'] = null;
        captureJSON['label'] = null;
        socket.emit('data_capture_phase',captureJSON);
        }
        ,recordTime);
};

$('button#link_sensor').bind('click', function() {
    channel = document.getElementsByName('channel')[0].value
    
    // change color of outline of button
    // 1) green: streaming data is coming in
    // 2) red  : streaming data is not coming in
    curDataUrl = '/cur_data/' + channel;
    $.get(curDataUrl, function( data ) {
        channelExists = true;
        // check if data is fresh
        dTime = Date.now() - data['timestamp']; 
        capturingStreamingData = (dTime < 1000)
        if (capturingStreamingData) {
            $('button#link_sensor').css('border', "solid 4px #18bc9c");
        }
        else {
            $('button#link_sensor').css('border', "solid 4px red");
        }
    });

    // if channel doesn't even exist and has never recorded data
    $(document).ajaxError(function(){
        $('button#link_sensor').css('border', "solid 4px red");
    });

    // set up - capture streaming data (during training) for plotting
    inputStreamingData = channel + '_training_data';
    socket.on(inputStreamingData, 
        function (data) {
            curData = data;
            az = data['motion']['z'];
            zdata.append(new Date().getTime(),az);
        }
    );
});

// when user hit start activity - clear old training data, update data type
// for recordTime, plot data, show progress bar, and change button color
$('button#start_activity_1').bind('click', function() {
    socket.emit('clear_redis_key',{'channel' : channel,'data_type' : 'training'});
    var activityName = document.getElementsByName('activity1')[0].value
    setDataType(activityName,recordTime,'activity_1_complete');

    // for z data
    chart1 = genChart('act1_chart',zdata)
    getPlotData = setInterval( function() {
        socket.emit('get_streaming_data',{'channel':channel, 'data_type':'training'});
    },150);

    setTimeout(function() {prog1.animate(1);},waitToRecord);
    setTimeout(function() {
        $('button#start_activity_1').css('border', "solid 4px #18bc9c");
        prog1.path.setAttribute('stroke','#18bc9c');
        chart1.stop()
        },waitToRecord+recordTime
    );

});

// same as for button 1, but don't clear old training data!
$('button#start_activity_2').bind('click', function() {
    var activityName = document.getElementsByName('activity2')[0].value
    setDataType(activityName,recordTime,'activity_2_complete');

    chart2 = genChart('act2_chart',zdata)
    getPlotData = setInterval( function() {
        socket.emit('get_streaming_data',{'channel':channel, 'data_type':'training'});
    },500);

    setTimeout(function() {prog2.animate(1);},waitToRecord);
    setTimeout(function() {
        $('button#start_activity_2').css('border', "solid 4px #18bc9c");
        prog2.path.setAttribute('stroke','#18bc9c');
        chart2.stop()
    },waitToRecord+recordTime);


});

// same as for button 1, but don't clear old training data!
$('button#start_activity_3').bind('click', function() {
    var activityName = document.getElementsByName('activity3')[0].value
    setDataType(activityName,recordTime,'activity_3_complete');

    chart3 = genChart('act3_chart',zdata)
    getPlotData = setInterval( function() {
        socket.emit('get_streaming_data',{'channel':channel, 'data_type':'training'});
    },500);

    setTimeout(function() {prog3.animate(1);},waitToRecord)
    setTimeout(function() {
        $('button#start_activity_3').css('border', "solid 4px #18bc9c");
        prog3.path.setAttribute('stroke','#18bc9c');
        chart3.stop()
    },waitToRecord+recordTime);
    
    
});

// see if training data was successfully stored, if so then request ping
// the training application to build a model for that channel.
// finally - update link for go to scoring/dashboard with the proper channel
// number
$('button#train_model').bind('click', function() {
    dataIsStoredUrl = 'stored_data/training/' + channel
    $.when(
        $.get(dataIsStoredUrl, function( data ) {
            trainSetLen = parseInt(data)
            dataSuccesfullyStored = (trainSetLen > 0);
        });
    ).then(function() {
        if (dataSuccesfullyStored) {
            if (runningLocally) {
                trainRequestUrl = 'http://0.0.0.0:8081/train/' + channel;
            } else {
                trainRequestUrl = 'http://move-train-bot.cfapps.pez.pivotal.io/train/' + channel;
            };
            $.get(trainRequestUrl, function( data ) {
                $('button#train_model').css('border', "solid 4px #18bc9c")
            });
            scoreUrl = 'dashboard' + '/' + channel;
            document.getElementById('go_to_scoring').setAttribute("href", scoreUrl);
        };
    });
});

function makeProgBar(elementName) {
    var line = new ProgressBar.Line(elementName, {
        color: '#FCB03C',
        duration: recordTime
    });
    return line;
};

prog1 = makeProgBar('#progress1');
prog2 = makeProgBar('#progress2');
prog3 = makeProgBar('#progress3');

// use smoothie library for making chart
function genChart(name,data) {
    chart = new SmoothieChart({maxValueScale:0.99,grid:{fillStyle:'#ffffff',strokeStyle:'transparent'},maxValue:15,minValue:-15,labels:{disabled:true}})       

    chart.addTimeSeries(data, {lineWidth:2.5,strokeStyle:'#18bc9c'});
    chart.streamTo(document.getElementById(name), 500); 
    chart.options.enableDpiScaling = false // fix weird scaling error
    
    console.log(document.getElementById(name));
    return chart
}
