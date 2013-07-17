#!/usr/bin/env python
from flask import Flask
import os

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


app = Flask(__name__, template_folder = TEMPLATE_FOLDER, static_folder = STATIC_FOLDER)



app.config.from_object('config')

app.debug = True


import views