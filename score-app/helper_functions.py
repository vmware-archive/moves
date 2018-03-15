# -*- coding: utf-8 -*-

"""
helper_functions.py
~~~~~~~~~~~~~
Helper functions for building a movement classification app
"""

import json
import os
import types

import redis

# initialize redis connection for local and CF deployment
def connect_redis_db(redis_service_name = None):
    if os.getenv('NODE_ENV') == 'micropcf':
        DB_HOST = os.getenv('REDIS_HOST')
        DB_PORT = os.getenv('REDIS_PORT')
        DB_PW = os.getenv('REDIS_PASSWORD')
        REDIS_DB = 0
    elif os.environ.get('VCAP_SERVICES') is None: # running locally
        DB_HOST = 'localhost'
        DB_PORT = 6379
        DB_PW = ''
        REDIS_DB = 1
    else:                                       # running on CF
        env_vars = os.environ['VCAP_SERVICES']
        rediscloud_service = json.loads(env_vars)[redis_service_name][0]
        credentials = rediscloud_service['credentials']
        DB_HOST = credentials['host']
        DB_PORT = credentials['port']
        DB_PW = password=credentials['password']
        REDIS_DB = 0

    return redis.StrictRedis(host=DB_HOST,
                              port=DB_PORT,
                              password=DB_PW,
                              db=REDIS_DB)




