#!/usr/bin/env python


from flask import render_template, g, request, jsonify, make_response
import util.sparql as s
from bs4 import BeautifulSoup
import requests
import os
import os.path
from datetime import datetime
import json 
import hashlib
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from flask.ext.socketio import SocketIO, emit
import time
from app import app, socketio


DEFAULT_SPARQL_ENDPOINT_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/provoviz"
DEFAULT_RDF_DATA_UPLOAD_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/provoviz/statements"



@app.route('/')
def index():
    return render_template('base.html')


@app.route('/graphs', methods=['GET'])
def graphs():
    
    endpoint_uri = request.args.get('endpoint_uri','')
    
    if endpoint_uri != '' :
        graphs = s.get_named_graphs(endpoint_uri)
        
        return jsonify(graphs = graphs)

    return "Nothing! Oops"
    
    


@app.route('/activities', methods=['GET'])
def activities():
    graph_uri = request.args.get('graph_uri',None)
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    if graph_uri and endpoint_uri:
        
        if graph_uri == 'http://example.com/none':
            graph_uri = None
        
        activities = s.get_activities(graph_uri, endpoint_uri)
        
        response = generate_graphs(graph_uri, endpoint_uri, activities=activities)
        
        response = json.dumps(response)
        
        return render_template('activities_service_response.html', response=response, data_hash='default')

    return "Nothing! Oops"


@app.route('/service', methods=['POST'])
def service():
    prov_data = request.form['data']
    graph_uri = request.form['graph_uri']
    
    prov_data = unicode(prov_data).encode('utf-8')
    graph_uri = unicode(graph_uri).encode('utf-8')
    
    if 'client' in request.form:
        client = request.form['client']
    else :
        client = None
    return service(prov_data, graph_uri, client)
    

def service(prov_data, graph_uri, client=None):
    
    
    log("Starting service for {}".format(graph_uri))
    
    
    
    if graph_uri.startswith('<') :
        context = graph_uri
    else :
        context = "<{}>".format(graph_uri)
    
    if graph_uri == '<http://example.com/none>':
        graph_uri = None
    
    data_hash = hashlib.sha1(prov_data).hexdigest()
    
    headers =  {'content-type':'text/turtle;charset=UTF-8'}
    params = {'context': context}

    print prov_data
    
    r = requests.put(DEFAULT_RDF_DATA_UPLOAD_URL,
                     data = prov_data,
                     params = params,
                     headers = headers)
    
    if r.ok :
        response = generate_graphs(graph_uri, DEFAULT_SPARQL_ENDPOINT_URL)
        
        response = json.dumps(response)
        log("Done")
        
        if client == 'linkitup':
            return render_template('activities_service_response_linkitup.html', response=response, data_hash=data_hash)
        else :
            return render_template('activities_service_response.html', response=response, data_hash=data_hash)
        
    else :
        app.logger.debug("Something went wrong")
        return make_response(r.content, 500)
    
    
    
    
@app.route('/test')
def service_test():
    git_url = 'https://github.com/tdn/SMIF-Mozaiek.git'

    g2p_response = requests.get('http://git2prov.org/git2prov', params={'giturl': git_url, 'serialization': 'PROV-O'})  

    prov_data = g2p_response.content

    if not g2p_response.ok:
        g2p_response.raise_for_status()

    provoviz_response = service(prov_data, git_url)
    
    return provoviz_response

    

def generate_graphs(graph_uri, endpoint_uri, activities = None):
    log("Generating provenance graphs...")
    
    ## It seems we're good to go!
    G = s.build_full_graph(graph_uri, endpoint_uri)
    
    if not activities:
        activities = s.get_activities(graph_uri, endpoint_uri)
    
    response = []
    for a in activities:
        
        activity_uri = a['id']
        activity_id = a['text']
        
        log(activity_uri)
        try:
            graph, width, types, diameter = s.extract_activity_graph(G, activity_uri, activity_id)
        except Exception as e:
            app.logger.debug(e)
            app.logger.debug("Continuing as if nothing happened...")
            log("Continuing as if nothing happened...")
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
    emit('message', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/log')
def test_disconnect():
    app.logger.info('Client disconnected')
    

def log(message):
    socketio.emit('message',
                  {'data': message },
                  namespace='/log')
    time.sleep(.2)









