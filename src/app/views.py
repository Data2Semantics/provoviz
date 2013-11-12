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
		
		response = generate_graphs(graph_uri, endpoint_uri)
		
		response = json.dumps(response)
		
		return render_template('activities_service_response.html', response=response, data_hash='default')

	return "Nothing! Oops"


# @app.route('/diagram', methods= ['GET'])
# def diagram():
# 	graph_type = request.args.get('type','')
# 	
# 	
# 	if graph_type == 'activities':
# 		activity_uri = request.args.get('uri','')
# 		activity_id = request.args.get('id','')
# 		graph_uri = request.args.get('graph_uri','')
# 		endpoint_uri = request.args.get('endpoint_uri','')
# 		
# 		
# 		if activity_uri == '' :
# 			return 'Nada'
# 		else :
# 			graph, width, types, diameter = s.build_activity_graph(activity_uri, activity_id, graph_uri, endpoint_uri)
# 		
# 		return jsonify(graph = graph, width = width, types= types, diameter=diameter)
# 		
# 	
# 	return "Nothing! Oops"


@app.route('/service', methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def service():
	prov_data = request.form['data']
	graph_uri = request.form['graph_uri']
	return service(prov_data, graph_uri)
	

def service(prov_data, graph_uri):
	
	if graph_uri.startswith('<') :
		context = graph_uri
	else :
		context = "<{}>".format(graph_uri)
	
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
		return render_template('activities_service_response.html', response=response, data_hash=data_hash)
		
	else :
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

	

def generate_graphs(graph_uri, endpoint_uri):
	## It seems we're good to go!
	G = s.build_full_graph(graph_uri, endpoint_uri)
	
	activities = s.get_activities(graph_uri, endpoint_uri)
	
	response = []
	for a in activities:
		
		activity_uri = a['id']
		activity_id = a['text']
		
		
		try:
			graph, width, types, diameter = s.extract_activity_graph(G, activity_uri, activity_id)
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
		
	return response






def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



