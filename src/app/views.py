#!/usr/bin/env python


from flask import render_template, g, request, jsonify, make_response
import util.sparql as s
from util.store import Store 

from bs4 import BeautifulSoup
import requests
import os
import os.path
from datetime import datetime
import json 
import hashlib
from datetime import timedelta
from flask import make_response, request, current_app, url_for
from functools import update_wrapper
from flask.ext.socketio import SocketIO
import time
from rdflib import Graph
from app import app, socketio
import sys
import traceback


DEFAULT_SPARQL_ENDPOINT_URL = "http://example.com/sparql"



@app.route('/')
def index():
    return render_template('base.html', default_endpoint = DEFAULT_SPARQL_ENDPOINT_URL)


@app.route('/graphs', methods=['GET']) ## LEGACY
@app.route('/api/graphs', methods=['GET'])
def graphs_service():
    
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    if endpoint_uri :
        store = Store(endpoint=endpoint_uri)
        
        graphs = s.get_named_graphs(store)
        
        return jsonify(graphs = graphs)

    return "Nothing! Oops"
    
    


@app.route('/activities', methods=['GET']) ## LEGACY
@app.route('/api/endpoint', methods=['GET'])
def endpoint_service():
    graph_uri = request.args.get('graph_uri',None)
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    if endpoint_uri:
        store = Store(endpoint=endpoint_uri)
        
        if graph_uri == 'http://example.com/none':
            graph_uri = None
        
        response = generate_graphs(store, graph_uri=graph_uri)
        response = json.dumps(response)
        
        return render_template('activities_service_response.html', response=response, data_hash='default')

    else :
        return make_response("At the very least, you should provide a SPARQL endpoint URL using the 'endpoint_uri' parameter in your GET request.",500)


@app.route('/service', methods=['POST']) ## LEGACY
@app.route('/api/data',methods=['POST'])
def data_service():
    
    ## This is (somehow) needed to make sure Linkitup works.
    if 'client' in request.form:
        client = request.form['client']
    else :
        client = None    
    
    ## If the form posted to us contains data, then yay!
    if 'data' in request.form:
        app.logger.debug("Retrieved some data!")
        prov_data = request.form['data']
    
        prov_data = unicode(prov_data).encode('utf-8')
        
        try :
            emit("Initializing data store")
            
            data_hash = hashlib.sha1(prov_data).hexdigest()
            store = Store(data=prov_data)
            
            emit("Generating graphs")
            
            response = generate_graphs(store)
            response = json.dumps(response)

            emit("Done")
        
            if client == 'linkitup':
                return render_template('activities_service_response_linkitup.html', response=response, data_hash=data_hash)
            else :
                return render_template('activities_service_response.html', response=response, data_hash=data_hash)
        except Exception as e:
            message = "Could not parse your PROV. Please upload a valid Turtle or N-Triple serialization that uses the PROV-O vocabulary.<br/>\n{}".format(e.message)
            app.logger.debug(e.message)
            emit(message)
            return make_response(message, 500)
    else :
        message = "You need to provide PROV-O in Turtle format using the 'data' field in your POST request."
        emit(message)
        return make_response(message, 500)
    

    

    

def generate_graphs(store, graph_uri=None):
    emit("Generating provenance graphs...")
    
    ## It seems we're good to go!
    G = s.build_full_graph(store,graph_uri)
    
    activities = s.get_activities(store,graph_uri)
    
    response = []
    total = len(activities)
    count = 0
    for a in activities:
        count += 1
        activity_uri = a['id']
        activity_id = a['text']
        
        # try:
        emit("Extracting graph for {} - {}/{}".format(activity_id, count, total))
        
        try:
            graph, width, types, diameter = s.extract_activity_graph(G, activity_uri, activity_id)
        except Exception as e:
            emit("Something went wrong, will skip this activity... {}".format(e.message))
            app.logger.warning(e.message)
            continue
        
        activity = {}
        activity['id'] = activity_uri
        activity['text'] = activity_id
        activity['graph'] = graph
        activity['width'] = width
        activity['types'] = types
        activity['diameter'] = diameter
    
        response.append(activity)
        
    return response


@socketio.on('connect', namespace='/log')
def test_connect():
    socketio.emit('message', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/log')
def test_disconnect():
    app.logger.info('Client disconnected')
    

def emit(message):
    socketio.emit('message',
                  {'data': message },
                  namespace='/log')
    time.sleep(.05)









