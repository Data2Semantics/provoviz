#!/usr/bin/env python

from app import app, socketio

from threading import Thread



if __name__ == '__main__':
    socketio.run(app)

#app.run(host='0.0.0.0',port=5000)