#!/usr/bin/env python
from flask import Flask
import os

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder = TEMPLATE_FOLDER)

app.config.from_object('config')

app.debug = True


import views