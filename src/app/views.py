#!/usr/bin/env python


from flask import render_template, g, request, jsonify
import util.sparql as s
from bs4 import BeautifulSoup
import requests
import os
import os.path
from datetime import datetime

from app import app

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
    pass












