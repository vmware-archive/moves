var socket = io.connect('http://' + document.domain + ':' + location.port);
var channel;
var recordTime = 20*1000
var waitToRecord = 1*1000
var trainSetLen = 0;
var dataSuccesfullyStored = false;

function setDataType(labelName,recordTime,elementID) { 
    captureJSON = {'channel':channel,
                   'data_type':'training',
                   'label':labelName};
    console.log(captureJSON)
    socket.emit('data_capture_phase',captureJSON);

    setTimeout(function() {
        captureJSON['data_type'] = null;
        captureJSON['label'] = null;
        socket.emit('data_capture_phase',captureJSON);
        }
    ,recordTime);
};
var zdata = new TimeSeries();

$('button#link_sensor').bind('click', function() {
    $('button#link_sensor').css('border', "solid 4px #18bc9c")
    channel = document.getElementsByName('channel')[0].value
    
    // for plots
    inputStreamingData = channel + '_training_data';
    socket.on(inputStreamingData, 
        function (data) {
            curData = data;
            az = data['motion']['z'];
            zdata.append(new Date().getTime(),az);
        });

});

$('button#start_activity_1').bind('click', function() {
    
    socket.emit('clear_redis_key',{'channel' : channel,'data_type' : 'training'});
    var activityName = document.getElementsByName('activity1')[0].value
    setDataType(activityName,recordTime,'activity_1_complete');

    // chart 
    chart1 = genChart('act1_chart',zdata)
    getPlotData = setInterval( function() {
        socket.emit('get_streaming_data',{'channel':channel, 'data_type':'training'});
    },500);

    setTimeout(function() {prog1.animate(1);},waitToRecord)
    setTimeout(function() {
        $('button#start_activity_1').css('border', "solid 4px #18bc9c");
        prog1.path.setAttribute('stroke','#18bc9c');
        chart1.stop()
    },waitToRecord+recordTime);

});



$('button#start_activity_2').bind('click', function() {
    //$(this).toggleClass("btn-success");
    //$('button#start_activity_2').toggleClass("btn-success");
    //
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

$('button#train_model').bind('click', function() {
    //socket.emit('training_data',{message :accel_data});
    dataIsStoredUrl = 'stored_data/training/' + channel
    console.log(dataIsStoredUrl);

    $.when(
        $.get(dataIsStoredUrl, function( data ) {
        trainSetLen = parseInt(data)
        dataSuccesfullyStored = (trainSetLen > 0);
        })
        ).then(function() {
                if (dataSuccesfullyStored) {
        if (document.domain == "0.0.0.0") {
            trainRequestUrl = 'http://0.0.0.0:8081/train/' + channel
        } else {
            trainRequestUrl = 'http://move-train-bot.cfapps.pez.pivotal.io/train/' + channel
        };
        $.get(trainRequestUrl, function( data ) {
            //document.getElementById('model_training_complete').innerHTML = '&#9989;';
            $('button#train_model').css('border', "solid 4px #18bc9c")
        });
        scoreUrl = 'scoring' + '/' + channel
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

function genChart(name,data) {
    chart = new SmoothieChart({maxValueScale:0.99,grid:{fillStyle:'#ffffff',strokeStyle:'transparent'},maxValue:15,minValue:-15,labels:{disabled:true}})       

    chart.addTimeSeries(data, {lineWidth:2.5,strokeStyle:'#18bc9c'});
    chart.streamTo(document.getElementById(name), 500); 
    chart.options.enableDpiScaling = false // fix weird scaling error
    
    console.log(document.getElementById(name));
    return chart
}
