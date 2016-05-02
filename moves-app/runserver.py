# -*- coding: utf-8 -*-

"""
runserver.py
~~~~~~~~~~~~~
This code launches the backend webserver of moves using flask with eventlet 
(for concurrency) and socket.io.
"""

from moves import app,socketio,r
app.run(debug=True)

socketio.run(app,host='0.0.0.0',port=PORT, debug=DEBUG)
