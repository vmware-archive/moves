var x = 0 ,  y = 0,
    vx = 0, vy = 0,
	ax = 0, ay = 0;
	
if (window.DeviceMotionEvent != undefined) {
	window.ondevicemotion = function(e) {
		ax = event.accelerationIncludingGravity.x;
		ay = event.accelerationIncludingGravity.y;
		az = event.accelerationIncludingGravity.z
	}

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    recordTime = 5*1000
    //create json output
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

    function getRandomArbitrary(min, max) {
        return Math.random() * (max - min) + min;
    }

    runningLocally = false;
    if (document.domain == "0.0.0.0") {
        runningLocally = true;
    }

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

    socket.emit('random_message',1);
    console.log('random_message');
    socket.on('echo1', 
        function (data) {console.log(data)});
    



    document.getElementById("start_stream").innerHTML = "<br>"

    // keep sensor awake
    var noSleep = new NoSleep();
    noSleep.enable(); // keep the screen on!

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
            //$('button#start_recording').toggleClass("btn-success");
            logData();
        });
    };
}
