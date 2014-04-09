#!/usr/bin/env python
from flask import Flask
import os
from flask.ext.socketio import SocketIO, emit

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


app = Flask(__name__, template_folder = TEMPLATE_FOLDER, static_folder = STATIC_FOLDER)



socketio = SocketIO(app)


app.config.from_object('config')

app.debug = True


import views