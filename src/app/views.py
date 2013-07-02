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
    
    activities = s.get_activities()
    
    return render_template('base.html', activities = activities)


@app.route('/graph', methods= ['GET'])
def graph():
    graph_type = request.args.get('type','')
    
    if graph_type == 'activities':
        activity_uri = request.args.get('uri','')
        activity_id = request.args.get('id','')
        
        if activity_uri == '' :
            return 'Nada'
        else :
            graph = s.build_activity_graph(activity_uri, activity_id)
        
        return jsonify(graph = graph)
        
    
    return "Nothing! Oops"
















@app.route('/editor')
def editor():
    patterns = s.get_patterns()
    
    return render_template('editor.html', patterns = patterns)
    
@app.route('/savetrial', methods=['POST'])
def savetrial():
    print request.json
    
    patterns = request.json['patterns']
    trial = request.json['trial']
    
    trial_rdf = s.build_trial_rdf(trial, patterns)
    
    trial_output_path = app.config['TRIAL_OUTPUT_PATH']
    
    print "Checking if directory exists:", trial_output_path
    if not os.path.exists(trial_output_path):
        print "Creating", trial_output_path
        os.makedirs(trial_output_path)
        print "Created"
        
    now = datetime.now()
    
    trial_file = open('{}/{}_{}.ttl'.format(trial_output_path,trial, now.isoformat('T')),'w')

    trial_file.write(trial_rdf)
    
    trial_file.close()
    
    print "Written RDF to", trial_file.name
    
    return 'Success!'



@app.route('/patternvalues')
def patternvalues():
    concepts = s.get_concepts()
    values = s.get_values()
    
    options = []
    options.extend(concepts)
    options.extend(values)
    
    values = []
    for o in options:
        v = {'id' : o['uri'], 'text': o['label']}
        values.append(v)
           
    
    return jsonify(values = values)

@app.route('/patterninstances', methods= ['GET'])
def patterninstances():
    pattern_uri = request.args.get('uri','')
    pattern_instances =  s.get_pattern_instances(pattern_uri)
    
    return jsonify(instances = pattern_instances)


@app.route('/trialtable', methods= ['GET'])
def trialtable():
    trial_id = request.args.get('trial','')
    
    url = "http://clinicaltrials.gov/ct2/show/record/{}".format(trial_id)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content)

    content = soup.find(id='main-content')
    
    return unicode(content)
