import ast
import json
import os
import redis
import types

def json2redis(data,r):
    if isinstance(data, types.ListType): # training
        if not from_one_sensor(data):
            return None,False

        channel,data_type = channel_and_data_type(data)
        rkey = 'channel_{}_{}'.format(channel,data_type)
        del r[rkey] # clear old data

        for row in data:
            channel = row['channel']
            data_type = row['data_type']
            r.lpush(rkey,row)
    else:
        if not training_or_scoring_phase(data):
            return None,False
        channel = data['channel']
        data_type = data['data_type']
        rkey = 'channel_{}_{}'.format(channel,data_type)

        r.lpush(rkey,data)
    return channel,True

def json_stream_to_redis(data,r):
    curkey = 'channel_{}_curdata'.format(channel)
    r.lpush(curkey,data)
    if not training_or_scoring_phase(data):
        return None,False
    channel = data['channel']
    data_type = data['data_type']
    rkey = 'channel_{}_{}'.format(channel,data_type)
    r.lpush(rkey,data)
    return channel,True


def training_or_scoring_phase(d):
    return (d['data_type'] in ['training','scoring'])

def channel_and_data_type(data):
    channel = data[0]['channel']
    data_type = data[0]['data_type']
    return channel, data_type

    
def from_one_sensor(data):
    num_data_types = len(set([_r['data_type'] for _r in data]))
    num_channel_ids = len(set([_r['channel'] for _r in data]))
    from_one_sensor = (num_data_types == 1) and (num_channel_ids == 1)
    if not from_one_sensor:
        return False
    return True
    
def capture_data_to_redis(json_data,rkey,r):
    '''We want to figure out if we want to store data'''
    channel = json_data['channel']
    curkey = 'channel_{}_curdata'.format(channel)
    r.lpush(curkey,json_data)
    r.ltrim(curkey,0,0)

    if not r.exists(rkey):
        return


    current_capture_phase = ast.literal_eval(r[rkey])
    data_type = current_capture_phase['dataCapturePhase']
    label = current_capture_phase['label']
    json_data['label'] = label
    json_data['data_type'] = data_type

    if not data_type: # don't need to store data
        return
    else: # training or scoring
        rdatakey = 'channel_{}_{}'.format(channel,data_type)
        r.lpush(rdatakey,json_data)

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




