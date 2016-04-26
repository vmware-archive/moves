# -*- coding: utf-8 -*-
"""
bot-train
~~~~~~~~~~~~~
Trains a ML model for incoming data accessed via redis. The bot waits
for a message from RabbitMQ to initialize.
"""

import cPickle
import os
import time

from flask import Flask, request, jsonify, abort, make_response, Markup, render_template, g
from flask.ext import restful
from flask.ext.restful import Api

import helper_functions
import train_functions

# handshake parameters
exchange_name       = 'model_init'
redis_service_name  = 'p-redis'

app = Flask(__name__)
api = restful.Api(app)

############################

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

@app.route('/train/<string:channel>')
def train(channel):
    # show the post with the given id, the id is an integer
    #model_train
    channel_id = channel
    data_store_key = 'channel_{}_training'.format(channel_id)
    model_store_key = 'channel_{}_model'.format(channel_id)
    cl = train_functions.train_model(data_store_key,r)
    if cl:
        r[model_store_key] = cPickle.dumps(cl, 1)
        return 'Model trained : ' + str(time.ctime()) 
    else:
        return 'Error model not trained'



@app.route('/')
def index():
    return 'train home1'

if os.environ.get('VCAP_SERVICES') is None: # running locally
    PORT = 8081
    DEBUG = True
    redis_service_name = None
else:                                       # running on CF
    PORT = int(os.getenv("PORT"))
    DEBUG = False
    redis_service_name = 'p-redis'
    
r = helper_functions.connect_redis_db(redis_service_name)
app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
