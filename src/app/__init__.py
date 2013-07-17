#!/usr/bin/env python
from flask import Flask
import os

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

if STATIC_URL_PATH :
    app = Flask(__name__, template_folder = TEMPLATE_FOLDER, static_url_path = STATIC_URL_PATH)
else :
    app = Flask(__name__, template_folder = TEMPLATE_FOLDER)



app.config.from_object('config')

app.debug = True


import views