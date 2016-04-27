/**
 * sensor.js
 *
 * Captures accelerometric data from smartphone and emits to backend
 * using socket.io
 *
 * @author Chris Rawles
 **/
var ax = 0, ay = 0;

// accelerometer API
if (window.DeviceMotionEvent != undefined) {
	window.ondevicemotion = function(e) {
		ax = event.accelerationIncludingGravity.x;
		ay = event.accelerationIncludingGravity.y;
		az = event.accelerationIncludingGravity.z
	}

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // create json output - will be sent to backend server
    function event2json(label) {
        currentSample = {'data':true,
        'channel':channel,
        'label':label,
        'data_type':dataCapturePhase,
        'timestamp':Date.now(),
        'orientation':{'x':null,'y':null,'z':null},
        'motion':{'x':ax,'y':ay,'z':az}
        };
        return currentSample;
    };

    // for testing purposes only
    function getRandomArbitrary(min, max) {
        return Math.random() * (max - min) + min;
    }

    // for testing
    runningLocally = false;
    if (document.domain == "0.0.0.0") { 
        runningLocally = true;
    }

    // capture data, emit via socketio, and update html
    document.getElementById("start_stream").innerHTML = "<br>"
    function logData() { 
        var dataInterval = setInterval( function() {
        if (runningLocally) {
//            for local testing
//            ax = 1+Math.round((Date.now()%40000)/40000)*15*(Date.now()%20000)/20000
//            ay = 1+Math.round((Date.now()%40000)/40000)*15*(Date.now()%20000)/20000
//            az = 1+Math.round((Date.now()%40000)/40000)*15*(Date.now()%20000)/20000
            ax = getRandomArbitrary(-9, 9)
            ay = getRandomArbitrary(-9, 9)
            az = getRandomArbitrary(-9, 9)
            };
            socket.emit('streaming_data',event2json());
            document.getElementById("start_stream").innerHTML = "Streaming data for sensor id: <b>" + channel + "</b>";
        }, 67)
    };

    // keep sensor awake
    var noSleep = new NoSleep();
    noSleep.enable(); 

    // hide input to prevent user from incorrectly using app
    if (!runningLocally & !isMobile.any) {
        document.getElementById('channel').disabled = true;
        $('#link_phone').remove();
    }
    else {
        var label;
        var dataCapturePhase;
        $('a#start_recording').bind('click', function() {
            channel = document.getElementsByName('channel')[0].value
            $('button#start_recording').css('border', "solid 4px #18bc9c");
            function myFunction() {
                document.getElementById("channel").disabled = true;
            }
            logData();
        });
    };
}
