#!/usr/bin/env python
import util.sparql as s
import logging
from rdflib import Graph, Namespace, ConjunctiveGraph

logger = logging.getLogger('provoviz.views')
logger.setLevel(logging.WARNING)

PROV = Namespace('http://www.w3.org/ns/prov#')
PROVOMATIC = Namespace('http://provomatic.org/resource/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DCT = Namespace('http://purl.org/dc/terms/')

def extract_graph(g, ng, resource, visited = set()):
    # TODO: THIS DOES NOT WORK AT ALL!
    logger.debug(resource)
    related = set()

    def recursive_forward(uri):
       for (p,o) in g.predicate_objects(subject=uri):
           if isinstance(o,URIRef):
               related.add(o)

               if o in visited:
                   continue
               else :
                   visited.append(o)
                   recursive_forward(o)

    def recursive_backward(uri):
       for (s,p) in g.subject_predicates(object=uri):
           if isinstance(s,URIRef):
               related.add(s)

               if s in visited:
                   continue
               else :
                   visited.append(s)
                   recursive_backward(s)


    recursive_forward(resource)
    recursive_backward(resource)

    for s,p,o in g:
        if s in related:
            logger.debug((s,p,o))
            ng.add((s,p,o))
        elif o in related:
            logger.debug((s,p,o))
            ng.add((s,p,o))
           
    return ng, visited
    

    
def generate_graphs(store, graph_uri=None, predefined_resources=None):
    logger.debug("Generating provenance graphs...")
    
    if predefined_resources is None:
        ## It seems we're good to go!
        G = s.build_full_graph(store,graph_uri)
    
        resources = s.get_prov_resources(store,graph_uri)
    else :
        ## It seems we're good to go!
        G = s.build_full_graph(store,graph_uri)
        
        resources = predefined_resources
        
        # TODO: The below code will make things much more efficient... but it DOES NOT WORK ARG
        # G = Graph()
        # G.bind('prov',PROV)
        # G.bind('provomatic',PROVOMATIC)
        # G.bind('skos',SKOS)
        # G.bind('dcterms',DCT)
        #
        # visited = set()
        # for r in predefined_resources:
        #     G,visited = extract_graph(store, G, r['id'],visited)
        #
        # resources = s.get_prov_resources(G,graph_uri)
    
    
    

    
    
    
    response = []
    total = len(resources)
    count = 0
    
    if total > 100 :
        logger.warning("Generating over 100 provenance graphs ({} to be precise). This may take a while.".format(total))
    for r in resources:
        count += 1
        resource_uri = r['id']
        resource_id = r['text']
        
        # try:
        logger.debug("Extracting graph for {} - {}/{}".format(resource_id, count, total))
        
        try:
            graph, width, types, diameter = s.extract_resource_graph(G, resource_uri, resource_id)
        except Exception as e:
            logger.warning("Something went wrong, will skip this resource... {}".format(e.message))
            logger.warning(e.message)
            continue
        
        resource = {}
        resource['id'] = resource_uri
        resource['text'] = resource_id
        resource['graph'] = graph
        resource['width'] = width
        resource['types'] = types
        resource['diameter'] = diameter
    
        response.append(resource)
        
    return response











