# -*- coding: utf-8 -*-

"""
setup_moves
~~~~~~~~~~~~~
This setup script has two goals:
    1) Update names (from moves_params.yml) of manifest files for the 3 apps: 
    moves, training app, and scoring app by reading """

import json
import yaml

# read parameters file
fname = 'moves_params.yml'
with open(fname) as f:
    dct = yaml.load(f)

redis_name = dct['redis-name']
moves_name = dct['moves-name']
train_name = dct['training-app-name']
score_name = dct['scoring-app-name']

def update_manifest(manifest_fname,app_name,redis_name):
    ''' We want to update the manifest files using the correct app and redis
    service names. '''
    with open(manifest_fname) as f:
        dct = yaml.load(f)

    dct['applications'][0]['name'] = app_name
    dct['applications'][0]['services'][0] = redis_name

    with open(manifest_fname,'w') as f:
        yaml.dump(dct, f,default_flow_style=False)
    
# update manifest files according to names
update_manifest('moves-app/manifest.yml',moves_name,redis_name)
update_manifest('train-app/manifest.yml',train_name,redis_name)
update_manifest('score-app/manifest.yml',score_name,redis_name)

# write parameter file 
params_fname = 'moves-app/moves/static/js/movesParams.js'

domain = 'cfapps.pez.pivotal.io'
train_route = '{}.{}'.format(train_name, domain)
score_route = '{}.{}'.format(score_name, domain)

train_score_params = {'trainAppUrl' : train_route,'scoreAppUrl' : score_route}
json.dump(train_score_params,open(params_fname,'w'))
