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


@app.route('/graphs', methods=['GET'])
def graphs():
    
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    if endpoint_uri :
        store = Store(endpoint=endpoint_uri)
        
        graphs = s.get_named_graphs(store)
        
        return jsonify(graphs = graphs)

    return "Nothing! Oops"
    
    


@app.route('/activities', methods=['GET'])
def activities():
    graph_uri = request.args.get('graph_uri',None)
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    if graph_uri and endpoint_uri:
        
        store = Store(endpoint=endpoint_uri)
        
        
        if graph_uri == 'http://example.com/none':
            graph_uri = None
        
        response = generate_graphs(store, graph_uri=graph_uri)
        response = json.dumps(response)
        
        return render_template('activities_service_response.html', response=response, data_hash='default')

    return "Nothing! Oops"


@app.route('/service', methods=['POST'])
def service():
    prov_data = request.form['data']
    
    prov_data = unicode(prov_data).encode('utf-8')
        
    if 'client' in request.form:
        client = request.form['client']
    else :
        client = None
        
    return service(prov_data, client)
    

def service(prov_data, client=None):
    emit("Starting service")
    
    data_hash = hashlib.sha1(prov_data).hexdigest()
    
    try :
        emit("Initializing Store")
        
        store = Store(data=prov_data)
    except Exception as e:
        message = "Could not parse your PROV. Please upload a valid Turtle or N-Triple serialization that uses the PROV-O vocabulary.<br/>\n{}".format(e.message)
        app.logger.debug(message)
        app.logger.debug(e.message)
        emit(message)
        return make_response(message, 500)
    
    response = generate_graphs(store)
    response = json.dumps(response)

    emit("Done")
        
    if client == 'linkitup':
        return render_template('activities_service_response_linkitup.html', response=response, data_hash=data_hash)
    else :
        return render_template('activities_service_response.html', response=response, data_hash=data_hash)      
    
    
@app.route('/test')
def service_test():
    git_url = 'https://github.com/tdn/SMIF-Mozaiek.git'

    g2p_response = requests.get('http://git2prov.org/git2prov', params={'giturl': git_url, 'serialization': 'PROV-O'})  

    prov_data = g2p_response.content

    if not g2p_response.ok:
        g2p_response.raise_for_status()

    provoviz_response = service(prov_data, git_url)
    
    return provoviz_response

    

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
        except:
            emit("Something went wrong, will skip this activity...")
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









