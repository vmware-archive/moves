# -*- coding: utf-8 -*-

"""
runserver.py
~~~~~~~~~~~~~
This code launches the backend webserver of moves using flask with eventlet 
(for concurrency) and socket.io.

author: Chris Rawles
"""

from moves import app,socketio,r
app.run(debug=True)

if os.environ.get('VCAP_SERVICES') is None: # running locally
    PORT = 8080
    DEBUG = True
    redis_service_name = None
else:                                       # running on CF
    PORT = int(os.getenv("PORT"))
    DEBUG = False
    redis_service_name = 'p-redis'

socketio.run(app,host='0.0.0.0',port=PORT, debug=DEBUG)
