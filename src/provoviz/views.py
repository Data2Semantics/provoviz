#!/usr/bin/env python
import util.sparql as s
import logging

logger = logging.getLogger('provoviz.views')
logger.setLevel(logging.WARNING)
    
def generate_graphs(store, graph_uri=None):
    logger.debug("Generating provenance graphs...")
    
    ## It seems we're good to go!
    G = s.build_full_graph(store,graph_uri)
    
    resources = s.get_prov_resources(store,graph_uri)
    
    response = []
    total = len(resources)
    count = 0
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











