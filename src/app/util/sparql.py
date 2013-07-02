#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
from flask import render_template
import re
from urllib import unquote_plus
import networkx as nx
from networkx.readwrite import json_graph
import json
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.serializer import Serializer
import rdfextras

from app import app

endpoint = app.config['SPARQL_ENDPOINT']

sparql = SPARQLWrapper(endpoint)
sparql.setReturnFormat(JSON)


concept_type_color_dict = {'popg': '#9edae5', 'inpo': '#ffbb78', 'elii': '#dbdb8d', 'idcn': '#9edae5', 'neop': '#2ca02c', 'vita': '#9467bd', 'inpr': '#c5b0d5', 'phsu': '#c5b0d5', 'blor': '#98df8a', 'hops': '#c7c7c7', 'menp': '#f7b6d2', 'phsf': '#d62728', 'ftcn': '#e377c2', 'anim': '#ff9896', 'food': '#bcbd22', 'grpa': '#ffbb78', 'geoa': '#2ca02c', 'hcpp': '#98df8a', 'lbtr': '#c7c7c7', 'ocdi': '#17becf', 'tisu': '#17becf', 'orch': '#7f7f7f', 'tmco': '#dbdb8d', 'clas': '#bcbd22', 'lipd': '#c49c94', 'dsyn': '#f7b6d2', 'horm': '#aec7e8', 'bact': '#2ca02c', 'grup': '#e377c2', 'bacs': '#ffbb78', 'enty': '#c5b0d5', 'resa': '#98df8a', 'medd': '#9467bd', 'cell': '#bcbd22', 'fndg': '#ff7f0e', 'sbst': '#ff9896', 'prog': '#ff9896', 'celf': '#aec7e8', 'chvf': '#1f77b4', 'diap': '#aec7e8', 'celc': '#8c564b', 'hcro': '#ff7f0e', 'inbe': '#9467bd', 'clna': '#ffbb78', 'acab': '#d62728', 'bodm': '#9467bd', 'patf': '#e377c2', 'carb': '#c7c7c7', 'bpoc': '#d62728', 'dora': '#8c564b', 'moft': '#7f7f7f', 'plnt': '#7f7f7f', 'ortf': '#f7b6d2', 'bmod': '#9edae5', 'sosy': '#dbdb8d', 'enzy': '#d62728', 'qnco': '#1f77b4', 'imft': '#7f7f7f', 'antb': '#1f77b4', 'bdsy': '#c5b0d5', 'nnon': '#9467bd', 'socb': '#c49c94', 'ocac': '#8c564b', 'bdsu': '#8c564b', 'rcpt': '#ff9896', 'nsba': '#c5b0d5', 'mnob': '#e377c2', 'orga': '#1f77b4', 'orgf': '#c7c7c7', 'lbpr': '#d62728', 'orgt': '#aec7e8', 'gngm': '#f7b6d2', 'virs': '#17becf', 'fngs': '#98df8a', 'aapp': '#17becf', 'opco': '#c49c94', 'irda': '#98df8a', 'famg': '#2ca02c', 'acty': '#ff7f0e', 'inch': '#bcbd22', 'cnce': '#9edae5', 'topp': '#ffbb78', 'spco': '#2ca02c', 'lang': '#dbdb8d', 'podg': '#aec7e8', 'mobd': '#ff9896', 'qlco': '#c49c94', 'npop': '#ff7f0e', 'hlca': '#1f77b4', 'phpr': '#ff7f0e', 'strd': '#8c564b'}


def uri_to_label(uri):
    return uri
    #return unquote_plus(uri.encode('utf-8').replace('http://eligibility.data2semantics.org/resource/','')).replace('_',' ').lstrip('-').lstrip(' ').title()


def get_activities():
    q = render_template('activities.q')
    
    sparql.setQuery(q)

    results = sparql.query().convert()
    
    activities = []
    
    for result in results["results"]["bindings"]:
        activity_uri = result['activity']['value']
        activity_id = result['label']['value']
        
        
        activities.append({'uri': activity_uri, 'id': activity_id})
        
    return activities
        
    








def build_graph(G, name, source=None, target=None, query=None, intermediate = None):
    #print "Building graph for {}.".format(name)
    
    print query
    
    sparql.setQuery(query)
    results = sparql.query().convert()

    import pprint
    
    pprint.pprint(results)

    
    
    
    for result in results["results"]["bindings"]:
        print result
        
        if not intermediate :
            if not source :
                source_binding = uri_to_label(name).replace("'","");
                source_uri = name
            else :
                if source+"_label" in result:
                    source_binding = result[source+"_label"]["value"]
                else :
                    source_binding = uri_to_label(result[source]["value"]).replace("'","")
                source_uri = result[source]["value"]
                
            if target+"_label" in result:
                target_binding = result[target+"_label"]["value"]
            else :
                target_binding = uri_to_label(result[target]["value"]).replace("'","")
            
            
            if source+"_type" in result :
                source_type = result[source+"_type"]["value"]
            else :
                source_type = source
            
            if target+"_type" in result :
                target_type = result[target+"_type"]["value"]
            else :
                target_type = target
            
            
            print source_type, target_type
            
            G.add_node(source_binding, label=source_binding, type=source_type, uri=source_uri)
            G.add_node(target_binding, label=target_binding, type=target_type, uri=result[target]["value"])
            G.add_edge(source_binding,target_binding, value=10)
            
            
            

        else :
            source_binding = uri_to_label(result[source]["value"]).replace("'","")
            intermediate_binding = uri_to_label(result[intermediate]["value"]).replace("'","")
            target_binding = uri_to_label(result[target]["value"]).replace("'","")
            
            G.add_node(source_binding, label=source_binding, type=source, uri=result[source]["value"])
            G.add_node(intermediate_binding, label=intermediate_binding, type=intermediate, uri=result[intermediate]["value"])
            G.add_node(target_binding, label=target_binding, type=target, uri=result[target]["value"])
            
            G.add_edge(source_binding, intermediate_binding, value=10)
            G.add_edge(intermediate_binding, target_binding, value=10)

    #print "Done"

    return G


def build_activity_graph(activity_uri, activity_id):
    G = nx.DiGraph()
    
    q_activity_to_resource = render_template('activity_to_resource.q', activity_uri = activity_uri)
    
    G = build_graph(G, activity_uri, "activity", "entity", q_activity_to_resource)
    
    q_resource_to_activity = render_template('resource_to_activity.q', activity_uri = activity_uri)
    
    G = build_graph(G, activity_uri, "entity", "activity", q_resource_to_activity)
    
    print activity_uri, activity_id
    
    # origin_node_id = "{}".format(activity_id.lower())
    #origin_node_id = activity_id
    #
    #G.node[origin_node_id]['type'] = 'origin'
    
    names = {}
    for n, nd in G.nodes(data=True):
        if nd['type'] == 'activity' or nd['type'] == 'origin':
            label = nd['label'].replace('Activity','').upper()            
            names[n] = label
        else :
            names[n] = nd['label']
    
    nx.set_node_attributes(G,'label', names)
    
    
    
    deg = nx.degree(G)
    nx.set_node_attributes(G,'degree',deg)
    
    
    g_json = json_graph.node_link_data(G) # node-link format to serialize


    return g_json



        
    
    
    

