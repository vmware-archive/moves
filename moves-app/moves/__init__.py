# -*- coding: utf-8 -*-

"""
moves
~~~~~~~~~~~~~
The moves PCF app contains the logic/front end for both the sensor and dashboard
application. This code launches the backend webserver of moves 
using flask with eventlet (for concurrency) and socket.io

author: Chris Rawles
"""

import ast
import json
import os
import time
import eventlet

from flask import Flask, render_template, request,jsonify
from flask.ext.socketio import SocketIO

import helper_functions

eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html',)

@app.route("/train")
def train():
    return render_template('train.html',)

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
    ''' 
    We want to keep current recording state in redis.
        1) training
        2) scoring
        3) neither training or scoring
    '''
    channel = json_data['channel']
    capture_phase = json_data['data_type']
    label = json_data['label']
    rkey = 'channel_{}_capture_phase'.format(channel);
    current_capture_phase = {'dataCapturePhase' : capture_phase,
                             'label' : label}
    r[rkey] = current_capture_phase

@socketio.on('streaming_data')
def streaming_data(json_data):
    """ 
    Capture streaming data from sensor to redis:
        1) if training phase - save all data to redis
        2) if scoring phase - save only some recent data to redis
        3) if neither - do not save data to redis
    """
    try:
        channel = json_data['channel']
        rkey = 'channel_{}_capture_phase'.format(channel);
        helper_functions.capture_data_to_redis(json_data,rkey,r)    
    except Exception, e:
        socketio.emit('error_message',str(e))

@socketio.on('get_streaming_data')
def get_streaming_data(json_data):
    """ 
    Retrieves streaming data for plotting (in training and scoring phase)
    """
    channel = json_data['channel']
    data_type = json_data['data_type']
    rkey = 'channel_{}_{}'.format(channel,data_type)
    cur_data = ast.literal_eval(r.lrange(rkey,0,0)[0])
    if cur_data['data_type'] == data_type:
        out_channel = '{}_{}_data'.format(channel,data_type)
        socketio.emit(out_channel,cur_data)

## these are for testing purposes 

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

@app.route('/info123')
def info123():
    return os.environ['VCAP_SERVICES']
##

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
