#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
import re
from urllib import unquote_plus
import networkx as nx
from networkx.readwrite import json_graph
import json
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef

from rdflib.serializer import Serializer
import rdfextras
from math import log
import time

from jinja2 import Environment, PackageLoader

import logging

logger = logging.getLogger('provoviz.util.sparql')
logger.setLevel(logging.WARNING)

env = Environment(loader=PackageLoader('provoviz','templates'))

concept_type_color_dict = {'popg': '#9edae5', 'inpo': '#ffbb78', 'elii': '#dbdb8d', 'idcn': '#9edae5', 'neop': '#2ca02c', 'vita': '#9467bd', 'inpr': '#c5b0d5', 'phsu': '#c5b0d5', 'blor': '#98df8a', 'hops': '#c7c7c7', 'menp': '#f7b6d2', 'phsf': '#d62728', 'ftcn': '#e377c2', 'anim': '#ff9896', 'food': '#bcbd22', 'grpa': '#ffbb78', 'geoa': '#2ca02c', 'hcpp': '#98df8a', 'lbtr': '#c7c7c7', 'ocdi': '#17becf', 'tisu': '#17becf', 'orch': '#7f7f7f', 'tmco': '#dbdb8d', 'clas': '#bcbd22', 'lipd': '#c49c94', 'dsyn': '#f7b6d2', 'horm': '#aec7e8', 'bact': '#2ca02c', 'grup': '#e377c2', 'bacs': '#ffbb78', 'enty': '#c5b0d5', 'resa': '#98df8a', 'medd': '#9467bd', 'cell': '#bcbd22', 'fndg': '#ff7f0e', 'sbst': '#ff9896', 'prog': '#ff9896', 'celf': '#aec7e8', 'chvf': '#1f77b4', 'diap': '#aec7e8', 'celc': '#8c564b', 'hcro': '#ff7f0e', 'inbe': '#9467bd', 'clna': '#ffbb78', 'acab': '#d62728', 'bodm': '#9467bd', 'patf': '#e377c2', 'carb': '#c7c7c7', 'bpoc': '#d62728', 'dora': '#8c564b', 'moft': '#7f7f7f', 'plnt': '#7f7f7f', 'ortf': '#f7b6d2', 'bmod': '#9edae5', 'sosy': '#dbdb8d', 'enzy': '#d62728', 'qnco': '#1f77b4', 'imft': '#7f7f7f', 'antb': '#1f77b4', 'bdsy': '#c5b0d5', 'nnon': '#9467bd', 'socb': '#c49c94', 'ocac': '#8c564b', 'bdsu': '#8c564b', 'rcpt': '#ff9896', 'nsba': '#c5b0d5', 'mnob': '#e377c2', 'orga': '#1f77b4', 'orgf': '#c7c7c7', 'lbpr': '#d62728', 'orgt': '#aec7e8', 'gngm': '#f7b6d2', 'virs': '#17becf', 'fngs': '#98df8a', 'aapp': '#17becf', 'opco': '#c49c94', 'irda': '#98df8a', 'famg': '#2ca02c', 'acty': '#ff7f0e', 'inch': '#bcbd22', 'cnce': '#9edae5', 'topp': '#ffbb78', 'spco': '#2ca02c', 'lang': '#dbdb8d', 'podg': '#aec7e8', 'mobd': '#ff9896', 'qlco': '#c49c94', 'npop': '#ff7f0e', 'hlca': '#1f77b4', 'phpr': '#ff7f0e', 'strd': '#8c564b'}




def uri_to_label(uri):
    if '#' in uri:
        (base,hash_sign,local_name) = uri.rpartition('#')
        base_uri = local_name.encode('utf-8')
    else :
        base_uri = re.sub("http://.*?/","",uri.encode('utf-8'))
        
    
    return shorten(unquote_plus(base_uri).replace('_',' ').lstrip('-').lstrip(' '))
    
def shorten(text):
    if len(text)>32:
        return text[:15] + "..." + text[-15:]
    else :
        return text


def get_prov_resources(store, graph_uri=None):
    logger.debug(('Retrieving prov resources...'))

    
    template = env.get_template('prov_resources.q')
    q = template.render(graph_uri=graph_uri)
    logger.debug(u"Query: \n".format(q))
    results = store.query(q)
    
    resources = []
    resource_uris = set()
    
    for result in results:
        resource_uri = unicode(result['resource'])
        
        if resource_uri in resource_uris:
            continue
        else :
            resource_uris.add(resource_uri)
        
        logger.debug(('PROV Resource: {}...'.format(resource_uri)))
        
        try:
            
            resource_label = unicode(result['label'])
            if not resource_label:
                raise Exception("None label")
            logger.debug(("Found label `{}` in result".format(result['label'])))
        except :
            logger.debug(("No label for {}".format(resource_uri)))
            resource_label = uri_to_label(unicode(resource_uri))
        
        logger.debug(("Found PROV resource {}".format(resource_label)))
         
        resources.append({'id': resource_uri, 'text': resource_label})
        
    return resources


def get_named_graphs(store):
    logger.debug(('Retrieving graphs...'))

    
    template = env.get_template('named_graphs.q')
    q = template.render()

    results = store.query(q)

    graphs = []
    
    for result in results:
        graph_uri = result['graph']

        logger.debug(("Found graph {}".format(graph_uri)))
        
        graphs.append({'uri': graph_uri, 'id': graph_uri, 'text': graph_uri})
        
    return graphs    
    








def build_graph(G, store, name=None, source=None, target=None, query=None, intermediate = None):
    logger.debug(('Building edges from {} to {}'.format(source, target)))
    
    
    logger.debug((u"Query:\n{}".format(query)))
    
    results = store.query(query)

    for result in results:
        logger.debug((u"Result:\n{}".format(result)))
        
        logger.debug(("Source: {}\nTarget: {}".format(result[source],result[target])))
        
        if result[source] == None or result[target] == None:
            logger.debug((u"This result is not usable as there is no binding to source and/or target"))
            continue
            
        source_uri = unicode(result[source])    
        target_uri = unicode(result[target])

        try :
            source_binding = shorten(result[source+"_label"])
            logger.debug(("{}_label in result".format(source)))
            if not source_binding:
                raise Exception("None label")
        except :
            logger.debug(("No {}_label in result!!".format(source)))
            source_binding = uri_to_label(result[source]).replace("'","")
        
        
            
        try :
            target_binding = shorten(result[target+"_label"])
            logger.debug(("{}_label in result".format(target)))
            
            if not target_binding:
                raise Exception("None label")
        except :
            logger.debug(("No {}_label in result!!".format(target)))
            target_binding = uri_to_label(result[target]).replace("'","")
            logger.debug(("Set to {}".format(target_binding)))
        
        
        try  :
            source_type = result[source+"_type"]
            if not source_type:
                raise Exception("None type")
            logger.debug(("{}_type in result: {}".format(source, source_type)))
        except :
            source_type = re.sub('\d+$','',source)
            logger.debug(("No {}_type in result!!".format(source)))
        
        try :
            target_type = result[target+"_type"]
            if not target_type:
                raise Exception("None type")
            logger.debug(("{}_type in result: {}".format(target, target_type)))
        except:
            target_type = re.sub('\d+$','',target)
            logger.debug(("No {}_type in result!!".format(target)))
            
        try :
            [_discard, source_type] = unicode(source_type).split('#')
            [_discard, target_type] = unicode(target_type).split('#')
        except :
            logger.debug('Could not split URI for source_type {} or target_type {}'.format(source_binding, target_binding))
        
        G.add_node(source_uri, label=unicode(source_binding), type=source_type, uri=unicode(source_uri))
        G.add_node(target_uri, label=unicode(target_binding), type=target_type, uri=unicode(target_uri))
        G.add_edge(source_uri, target_uri, value=10)

    logger.debug(('Query-based graph building complete...'))


    return G


def build_full_graph(store, graph_uri=None):
    logger.debug((u"Building full provenance graph..."))
    
    G = nx.DiGraph()
    
    q_activity_to_resource_template = env.get_template('activity_to_resource.q')
    q_activity_to_resource = q_activity_to_resource_template.render(graph_uri=graph_uri)
    logger.debug(("Running activity to resource"))
    G = build_graph(G, store, source="activity", target="entity", query=q_activity_to_resource)
    
    q_resource_to_activity_template = env.get_template('resource_to_activity.q')
    q_resource_to_activity = q_resource_to_activity_template.render(graph_uri=graph_uri)
    logger.debug(("Running resource to activity"))
    G = build_graph(G, store, source="entity", target="activity", query=q_resource_to_activity)
    
    q_derived_from_template = env.get_template('derived_from.q')
    q_derived_from = q_derived_from_template.render(graph_uri = graph_uri)
    logger.debug(("Running derived from"))
    G = build_graph(G, store, source="entity1", target="entity2", query=q_derived_from)
    
    q_informed_by_template = env.get_template('informed_by.q')
    q_informed_by = q_informed_by_template.render(graph_uri = graph_uri)
    logger.debug(("Running informed by"))
    G = build_graph(G, store, source="activity1", target="activity2", query=q_informed_by)
 

    for c in nx.simple_cycles(G):
        logger.warning(("Found cycle of length {}, removing the edge between the last two nodes (if it still exists)".format(len(c))))
        if (c[-2],c[-1]) in G.edges():
            G.remove_edge(c[-2],c[-1])

    for (s,t) in G.edges():
        if (t,s) in G.edges():
            logger.warning(("Found cycle (removing the first):\n{} {}\n{} {}".format(s,t,t,s)))
            
            logger.debug(("Data:\nSource {}\nTarget {}".format(G.node[s],G.node[t])))
            G.remove_edge(s,t)
    
    logger.debug(("Building full provenance graph complete..."))



    return G
    
    
def extract_ego_graph(G, activity_uri):
    sG = None
    inG = None
    outG = None
    
    logger.debug((u"Extracting ego graph (forward) {}".format(activity_uri)))
    outG = nx.ego_graph(G,activity_uri,50)
    logger.debug((u"Extracting ego graph (backward) {}".format(activity_uri)))
    inG = nx.ego_graph(G.reverse(),activity_uri,50)
    logger.debug((u"Reversing backward ego graph {}".format(activity_uri)))
    inG = inG.reverse()
    logger.debug((u"Joining ego graphs {}".format(activity_uri)))
    sG = nx.compose(outG,inG)
    
    return sG

def extract_resource_graph(G, resource_uri, resource_id):
    logger.debug((u"Extracting graph for {} ({})".format(resource_uri, resource_id)))
    
    try:
        sG = extract_ego_graph(G, resource_uri)
    except Exception as e:
        logger.warning((u"Could not extract ego graph for {}/{} (Bug in NetworkX?)".format(resource_id, resource_uri)))
        logger.debug((e.message))
        logger.debug((e))
        return
        
        
    logger.debug(("Original graph: {} nodes\nEgo graph: {} nodes".format(len(G.nodes()),len(sG.nodes()))))

    # Set node type for the resource_uri to 'origin'
    sG.node[resource_uri]['type'] = 'origin'
    
    logger.debug((u"Assigning weights to edges"))
    logger.debug(("Assigning weights to edges"))
    
    # Get start and end nodes (those without incoming or outgoing edges, respectively)
    start_nodes = [ n for n in sG.nodes() if sG.in_degree(n) == 0 ]
    end_nodes = [ n for n in sG.nodes() if sG.out_degree(n) == 0 ]
    
    edge_weights = {}
    try:
        # Walk all edges, and assign weights
        edge_weights = walk_weights(graph = sG, pending_nodes = set(start_nodes), edge_weights = {}, visited = set())
    except Exception as e:
        logger.error(("ERROR: Provenance trace contains cycles: {}".format(e.message)))
        raise e
        
    
    # Check to make sure that the edge weights dictionary has the same number of keys as edges in the ego graph
    logger.debug(("Check {}/{}".format(len(edge_weights.keys()),len(sG.edges()))))
    nx.set_edge_attributes(sG,'value',edge_weights)
    del(edge_weights)
    # nx.set_node_attributes(sG,'value',node_weights)

    
    
    # Convert to JSON
    g_json = json_graph.node_link_data(sG) # node-link format to serialize

    # Get number of start and end nodes to determine ideal width of the viewport
    start_nodes = len(start_nodes)
    end_nodes = len(end_nodes)
    max_degree = 1
    for n,d in sG.nodes(data=True):
        if sG.in_degree(n) > max_degree :
            max_degree = sG.in_degree(n)
        if sG.out_degree(n) > max_degree :
            max_degree = sG.out_degree(n)
            
    # Set width to the largest of # end nodes, # start nodes, or the maximum degree
    width = max([end_nodes,start_nodes,max_degree])      

    logger.debug((u"Computing graph diameter {} ({})".format(resource_uri, resource_id)))
    try:
        diameter = nx.diameter(sG.to_undirected())
    except Exception:
        logger.debug(("Could not determine diameter, setting to arbitrary value of 25"))
        diameter = 25
    
    types = len(set(nx.get_node_attributes(sG,'type').values()))
    
    if types > 11:
        types = 11
    elif types < 3 :
        types = 3
    
    logger.debug((u"Done extracting graph for {} ({})".format(resource_uri, resource_id)))
    return g_json, width, types, diameter


def walk_weights(graph, pending_nodes = set(), edge_weights = {}, visited = set()):
    # If we have no more nodes in the queue, return the computed edge weights
    logger.debug((pending_nodes))
    if pending_nodes == set():
        return edge_weights
        
    next_nodes = set()
    for n in pending_nodes:
        # If a node has already been visited, just ignore it
        if n in visited:
            logger.debug(("Already visited {}".format(n)))
            continue
            
        # If the node does not have any incoming edges, 
        # set the edge weight of each outgoing edge to log(10) (why? search me! Looks nice)
        if graph.in_degree(n) == 0:
            out_edges = graph.out_edges([n])
            for (u,v) in out_edges:
                edge_weights[(u,v)] = log(10)
                next_nodes.add(v)
                
            # We can safely add the node to the visited list.
            visited.add(n)
            
        # Otherwise, the node *does* have outgoing edges
        else:
            # Get all incoming edges
            in_edges = graph.in_edges([n])
            
            # Make sure that all incoming edges already have a weight
            incomplete = [e for e in in_edges if e not in edge_weights.keys()]
            
            # If some of them don't, we add the current node to the end of the queue and stop treating it.
            # This is because we need all edge weights before we can redistribute the weight to the outgoing edges
            if incomplete != [] :
                logger.debug(("Node `{}` has unvisited incoming edges, adding to end of queue".format(n)))
                next_nodes.add(n)
                continue
            
            # Otherwise, we'll just calculate the accumulated weight of all incoming edges
            accumulated_weight = sum([edge_weights[e] for e in in_edges])
            
            # Get the outgoing edges of the current node
            out_edges = graph.out_edges([n])
            
            # Get the out degree of the current node (actually just len(out_edges))
            out_degree = graph.out_degree(n)
                
            
            # And then we divide the accumulated weight by the out degree, 
            # assign it to each outgoing edge, and
            # add the target node to the next_nodes queue
            for (u,v) in out_edges:
                edge_weights[(u,v)] = accumulated_weight/out_degree
                next_nodes.add(v)
                
            # Only append node to visited if it is not in next_nodes
            visited.add(n)

    # Once we have visited all nodes, we call walk_weights recursively with the next_nodes list
    # If next_nodes is the same as the pending_nodes, we run the risk of going in circles, and we'll just return the edge_weights
    if set(next_nodes) == set(pending_nodes):
        logger.debug(("Next nodes and pending nodes are equal, we are going in circles. Assigning log(10) weights to incoming edges, and trying again."))
        
        # Get all incoming edges
        in_edges = graph.in_edges(list(next_nodes))
        # Filter out those that do not have an edge weight
        incomplete = [e for e in in_edges if e not in edge_weights.keys()]
        # Assign the arbitrary value of log(10) to the incoming edges
        for (u,v) in incomplete:
            edge_weights[(u,v)] = log(10)
        
        return walk_weights(graph, next_nodes, edge_weights, visited)
    else :
        return walk_weights(graph, next_nodes, edge_weights, visited)
    



        
    
    
    

