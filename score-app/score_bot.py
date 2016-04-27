# -*- coding: utf-8 -*-
"""
bot-score
~~~~~~~~~~~~~
Scores streaming data (incoming via RabbitMQ) using ML model from redis 
"""

import cPickle
import os

from flask import Flask, request, jsonify, abort, make_response, Markup, render_template, g
from flask.ext import restful
from flask.ext.restful import Api
import numpy as np

import helper_functions
import model_functions

##

# load pickle object
win_size = 30
fmin,fmax,sr = 0,8,win_size

component_names = ['x','y','z']

def json2ts(di):
    return np.array([float(eval(di)['motion'][c]) for c in component_names])

def score_in_data(data,cl,channel_id):
    in_data = np.array([json2ts(r) for r in data])
    pred_label,pred_score = model_functions.apply_model(in_data.T,cl,fmin,fmax,sr)
    res = {'channel':channel_id,'label':pred_label ,'label_value':pred_score}
    return res
    
    
app = Flask(__name__)
api = restful.Api(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

@app.route('/score/<string:channel>')
def score(channel):
    print channel
    model_store_key = 'channel_{}_model'.format(channel)
    cl = cPickle.loads(r[model_store_key])
    rkey = 'channel_{}_scoring'.format(channel)

    r.ltrim(rkey,0,100) # trim so this doesn't blow up
    data = r.lrange(rkey,0,win_size-1)
    return jsonify(**score_in_data(data, cl,channel))
    
if os.environ.get('VCAP_SERVICES') is None: # running locally
    PORT = 8082
    DEBUG = True
    redis_service_name = None
else:                                       # running on CF
    PORT = int(os.getenv("PORT"))
    DEBUG = False
    redis_service_name = 'p-redis'

r = helper_functions.connect_redis_db(redis_service_name)
app.run(host='0.0.0.0', port=PORT, debug=DEBUG,threaded=True)

