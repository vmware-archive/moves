import helper_functions

from flask import Flask, render_template, request,jsonify
from flask.ext.socketio import SocketIO
import json
import time
import ast
import os
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html',)

@app.route("/train")
def train():
    return render_template('train.html',)

@socketio.on('random_message')
def streaming_data(json_data):
    """ 
    saves streaming data from sensor to redis 
    """
    socketio.emit('echo1','sent back')

#@app.route("/scoring")
#def score():
#    return render_template('score.html')

@app.route("/dashboard/<string:channel>")
def dashboard(channel):
    return render_template('dashboard.html',channel = str(channel))

@app.route("/sensor")
def sensor():
    return render_template('sensor.html',)

@app.route("/about")
def about():
    return render_template('about.html',)

@socketio.on('data_capture_phase')
def write_capture_stage_to_redis(json_data):
    ''' We want to keep current recording state in redis '''
    channel = json_data['channel']
    capture_phase = json_data['data_type']
    label = json_data['label']
    rkey = 'channel_{}_capture_phase'.format(channel);
    current_capture_phase = {'dataCapturePhase' : capture_phase,
                             'label' : label}
    r[rkey] = current_capture_phase


#@socketio.on('training_data')
#def store_training_data(json_data):
#    text = json_data['message']
#    channel,stored_data = helper_functions.json2redis(text,r)
#    socketio.emit('stored_training_data?', {'channel':channel,
#                                            'stored_data': stored_data})

#@socketio.on('streaming_data_for_scoring')
#def handle_source(json_data):
#    text = json_data['message']
#    channel,stored_data = helper_functions.json2redis(text,r)
#    #TODO emit channel_{}_is_connected and light up green box and not-empty

@socketio.on('get_streaming_data')
def get_streaming_data(json_data):
    """ 
    retrieves streaming data for plotting (in training and scoring phase)
    """
    channel = json_data['channel']
    data_type = json_data['data_type']
    rkey = 'channel_{}_{}'.format(channel,data_type)
    cur_data = ast.literal_eval(r.lrange(rkey,0,0)[0])
    if cur_data['data_type'] == data_type:
        out_channel = '{}_{}_data'.format(channel,data_type)
        socketio.emit(out_channel,cur_data)


@socketio.on('streaming_data')
def streaming_data(json_data):
    """ 
    Saves streaming data from sensor to redis 
    """
    try:
        channel = json_data['channel']
        rkey = 'channel_{}_capture_phase'.format(channel);
        helper_functions.capture_data_to_redis(json_data,rkey,r)    
    except Exception, e:
        socketio.emit('echo1',str(e))

@app.route('/stored_data/<string:data_type>/<string:channel>')
def check_if_stored_data(data_type,channel):
    rkey = 'channel_{}_{}'.format(channel,data_type)
    return str(r.llen(rkey))

@app.route('/cur_data/<string:channel>')
def get_cur_data(channel):
    rkey = 'channel_{}_curdata'.format(channel)
    print rkey
    return jsonify(ast.literal_eval(r.lrange(rkey,0,0)[0]))

@socketio.on('clear_redis_key')
def clear_redis_key(json_data):
    channel = json_data['channel']
    data_type = json_data['data_type']
    rkey = 'channel_{}_{}'.format(channel,data_type)
    print 'deleting' + rkey
    del r[rkey]


@socketio.on('send_message_from_log')
def handle_source(json_data):
    socketio.emit('echo', {'echo': '10'})

@app.route('/redis_key/<string:key>')
def get_redis_key(key):
    return str(r.lrange(key,0,-1))

@app.route('/redis_info')
def redis_info():
    return jsonify(r.info())

@app.route('/flush_all')
def flush_all():
    r.flushall()
    return jsonify(r.info())


if __name__ == "__main__":
    if os.environ.get('VCAP_SERVICES') is None: # running locally
        PORT = 8080
        DEBUG = True
        redis_service_name = None
    else:                                       # running on CF
        PORT = int(os.getenv("PORT"))
        DEBUG = False
        #DEBUG = True
        redis_service_name = 'p-redis'
        
    r = helper_functions.connect_redis_db(redis_service_name)
    socketio.run(app,host='0.0.0.0',port=PORT, debug=DEBUG)
