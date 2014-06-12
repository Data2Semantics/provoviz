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
from flask.ext.socketio import SocketIO
import time
from rdflib import Graph
from app import app, socketio
import sys
import traceback


# DEFAULT_SPARQL_ENDPOINT_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/provoviz"
# DEFAULT_RDF_DATA_UPLOAD_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/provoviz/statements"


DEFAULT_SPARQL_ENDPOINT_URL = "http://localhost:5820/provoviz/query"
DEFAULT_RDF_DATA_UPLOAD_URL = "http://localhost:5820/provoviz/update"

STARDOG = True
USER = 'admin'
PASS = 'admin'
# USER = None
# PASS = None


@app.route('/')
def index():
    return render_template('base.html', default_endpoint = DEFAULT_SPARQL_ENDPOINT_URL)


@app.route('/graphs', methods=['GET'])
def graphs():
    
    endpoint_uri = request.args.get('endpoint_uri','')
    
    stardog = STARDOG
    if endpoint_uri != DEFAULT_SPARQL_ENDPOINT_URL :
        stardog = False
    
    if endpoint_uri != '' :
        graphs = s.get_named_graphs(endpoint_uri, stardog=stardog, auth=(USER,PASS))
        
        return jsonify(graphs = graphs)

    return "Nothing! Oops"
    
    


@app.route('/activities', methods=['GET'])
def activities():
    graph_uri = request.args.get('graph_uri',None)
    endpoint_uri = request.args.get('endpoint_uri',None)
    
    stardog = STARDOG
    if endpoint_uri != DEFAULT_SPARQL_ENDPOINT_URL :
        stardog = False
    
    if graph_uri and endpoint_uri:
        
        if graph_uri == 'http://example.com/none':
            graph_uri = None
        
        activities = s.get_activities(graph_uri, endpoint_uri, stardog = stardog, auth = (USER, PASS))
        
        response = generate_graphs(graph_uri, endpoint_uri, activities=activities, stardog = stardog, auth = (USER, PASS))
        
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
    emit("Starting service for {}".format(graph_uri))
    
    if graph_uri.startswith('<') :
        context = graph_uri
    else :
        context = "<{}>".format(graph_uri)
    
    if graph_uri == '<http://example.com/none>':
        graph_uri = None
    
    data_hash = hashlib.sha1(prov_data).hexdigest()
    
    headers =  {'content-type':'text/turtle;charset=UTF-8'}
    params = {'context': context}

    try :
        emit("Parsing PROV and converting to N-Triples")
        prov_graph = Graph()
        prov_graph.parse(data=prov_data,format="turtle")
        prov_data_nt = prov_graph.serialize(format='nt')
    except Exception as e:
        message = "Could not parse your PROV. Please upload a valid Turtle or N-Triple serialization that uses the PROV-O vocabulary.<br/>\n{}".format(e.message)
        app.logger.debug(message)
        app.logger.debug(e.message)
        emit(message)
        return make_response(message, 500)
    
    emit("Uploading PROV to triple store...")
    
    if not STARDOG :    
        app.logger.debug("Using default PUT method (non STARDOG)")
        r = requests.put(DEFAULT_RDF_DATA_UPLOAD_URL,
                         data = prov_data_nt,
                         params = params,
                         headers = headers)
    else :
        app.logger.debug("Posting to STARDOG SPARQL Update endpoint using credentials, if provided")
        data = "INSERT DATA {{ GRAPH {} {{ {} }} }}".format(context, prov_data_nt)
        
        payload = {'update': data}
        
        if USER and PASS :
            app.logger.debug("Using credentials to post")
            r = requests.post(DEFAULT_RDF_DATA_UPLOAD_URL, data=payload, auth=(USER,PASS))
        else :
            app.logger.debug("Not using credentials")
            r = requests.post(DEFAULT_RDF_DATA_UPLOAD_URL, data=payload)
    
    emit("Received response from triple store...")
    
    if r.ok :
        response = generate_graphs(graph_uri, DEFAULT_SPARQL_ENDPOINT_URL, stardog=STARDOG, auth=(USER,PASS))
        
        response = json.dumps(response)
        emit("Done")
        
        if client == 'linkitup':
            return render_template('activities_service_response_linkitup.html', response=response, data_hash=data_hash)
        else :
            return render_template('activities_service_response.html', response=response, data_hash=data_hash)        
    else :
        app.logger.debug("Failed to upload the PROV to server: {} ({}).\n{}".format(r.reason, r.status_code,r.text))
        emit("Failed to upload the PROV to server: {} ({}).\n{}".format(r.reason, r.status_code,r.text))
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

    

def generate_graphs(graph_uri, endpoint_uri, activities = None, stardog=False, auth=None):
    emit("Generating provenance graphs...")
    
    
    
    ## It seems we're good to go!
    G = s.build_full_graph(graph_uri, endpoint_uri, stardog=stardog, auth=auth)
    
    if not activities:
        activities = s.get_activities(graph_uri, endpoint_uri, stardog=stardog, auth=auth)
    
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
        
        # except Exception as e:
        #     t_,v_,traceback_ = sys.exc_info()
        #     app.logger.warning(t_)
        #     app.logger.warning(traceback_)
        #     app.logger.debug("Continuing as if nothing happened...")
        #     emit("Continuing as if nothing happened...")
        #     continue
            
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









