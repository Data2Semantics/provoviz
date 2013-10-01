#!/usr/bin/env python


from flask import render_template, g, request, jsonify, make_response
import util.sparql as s
from bs4 import BeautifulSoup
import requests
import os
import os.path
from datetime import datetime
import json 

from app import app

DEFAULT_SPARQL_ENDPOINT_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/goldendemo"
DEFAULT_RDF_DATA_UPLOAD_URL = "http://semweb.cs.vu.nl:8080/openrdf-sesame/repositories/goldendemo/statements"

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
    graph_uri = request.args.get('graph_uri','')
    endpoint_uri = request.args.get('endpoint_uri','')
    
    if graph_uri != '' and endpoint_uri != '':
        activities = s.get_activities(graph_uri, endpoint_uri)
    
        return jsonify(activities = activities)

    return "Nothing! Oops"


@app.route('/diagram', methods= ['GET'])
def diagram():
    graph_type = request.args.get('type','')
    
    
    if graph_type == 'activities':
        activity_uri = request.args.get('uri','')
        activity_id = request.args.get('id','')
        graph_uri = request.args.get('graph_uri','')
        endpoint_uri = request.args.get('endpoint_uri','')
        
        
        if activity_uri == '' :
            return 'Nada'
        else :
            graph, width, types, diameter = s.build_activity_graph(activity_uri, activity_id, graph_uri, endpoint_uri)
        
        return jsonify(graph = graph, width = width, types= types, diameter=diameter)
        
    
    return "Nothing! Oops"


@app.route('/service', methods=['POST'])
def service():
    prov_data = request.form['data']
    graph_uri = request.form['graph_uri']
    context = "<{}>".format(graph_uri)
    
    
    headers =  {'content-type':'text/turtle;charset=UTF-8'}
    params = {'context': context}

    r = requests.put(DEFAULT_RDF_DATA_UPLOAD_URL,
                     data = prov_data,
                     params = params,
                     headers = headers)
    
    if r.ok :
        ## It seems we're good to go!
        activities = s.get_activities(graph_uri, DEFAULT_SPARQL_ENDPOINT_URL)
        
        response = []
        for a in activities:
            activity_uri = a['id']
            activity_id = a['text']
            
            try:
                graph, width, types, diameter = s.build_activity_graph(activity_uri, activity_id, graph_uri, DEFAULT_SPARQL_ENDPOINT_URL)
            except Exception as e:
                app.logger.debug(e)
                app.logger.debug("Continuing as if nothing happened...")
                continue
                
            activity = {}
            activity['id'] = activity_uri
            activity['text'] = activity_id
            activity['graph'] = graph
            activity['width'] = width
            activity['types'] = types
            activity['diameter'] = diameter
        
            response.append(activity)
        
        response = json.dumps(response)
        return render_template('activities_service.html', response=response)
        
    else :
        return make_response(r.content, 500)
    
    
    
    
    











