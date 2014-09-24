#!/usr/bin/env python
import util.sparql as s
import logging

logger = logging.getLogger('provoviz.views')
logger.setLevel(logging.WARNING)
    
def generate_graphs(store, graph_uri=None):
    logger.debug("Generating provenance graphs...")
    
    ## It seems we're good to go!
    G = s.build_full_graph(store,graph_uri)
    
    activities = s.get_activities(store,graph_uri)
    
    response = []
    total = len(activities)
    count = 0
    for a in activities:
        count += 1
        activity_uri = a['id']
        activity_id = a['text']
        
        # try:
        logger.debug("Extracting graph for {} - {}/{}".format(activity_id, count, total))
        
        try:
            graph, width, types, diameter = s.extract_activity_graph(G, activity_uri, activity_id)
        except Exception as e:
            logger.warning("Something went wrong, will skip this activity... {}".format(e.message))
            logger.warning(e.message)
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











