'''
For testing purposes - simulate data
'''
import pika
import time
import json
import os
import redis

import pandas as pd

channel_id = str(9999999999)
exchange_name = 'channel_{}'.format(channel_id)
data_store_key = 'channel_{}_data'.format(channel_id)
redis_label_pred_key = 'channel_{}_label'.format(channel_id)


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=exchange_name,
                         type='fanout')


# initialize redis connection for local and CF deployment
def connect_db():
    if os.environ.get('VCAP_SERVICES') is None: # running locally
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

r = connect_db()


while True:
    print r[redis_label_pred_key]
##




jsonf=open('phone_data2.json')
data = json.load(jsonf)

## write training data to redis
#r.delete(data_store_key)
#for di in data:
#    r.lpush(data_store_key,str(di))
#    print di['label']
#
#raw_input()


def pub(msg):
    channel.basic_publish(exchange=exchange_name,
                          routing_key = '',
                          body = msg)

while True:
    a =time.time()
    for di in data:
        time.sleep(1./30.)
        pub(str(di))
        print di['label']
        
    b = time.time()
    print b - a


