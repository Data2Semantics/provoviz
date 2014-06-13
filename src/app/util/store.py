from rdflib.plugins.sparql.results.jsonresults import JSONResultParser
from rdflib import Graph
from StringIO import StringIO
from app import app, socketio
from flask import url_for
import requests

class Store(object):
    
    # Initialize the store, either with data or with endpoint (but not both)
    def __init__(self, data=None, endpoint=None, auth=None):
        if data and not endpoint:
            emit("Loading PROV data in Turtle format")
            
            self.remote = False
            try :
                self.graph = Graph()  
                app.logger.debug('Loading PROV-O definitions from {}'.format(url_for('.static',filename='prov-o.ttl',_external=True)))           
                self.graph.parse(url_for('.static',filename='prov-o.ttl',_external=True),format="turtle")      
                app.logger.debug('Loading data...')
                self.graph.parse(data=data,format="turtle")
            except Exception as e:
                emit("Store could not load data (not Turtle?)")
                
                raise e
        
        elif endpoint and not data:
            emit("Setting SPARQL connection parameters")
            
            self.remote = True
            self.session = requests.Session()
            self.session.headers.update({'Accept':'application/sparql-results+json'})
            
            if auth:
                emit("Setting basic HTTP authentication parameters for endpoint {}".format(endpoint))
                self.session.auth = auth
            
            self.endpoint = endpoint
        else:
            print "Whoops: cannot give me both data and an endpoint!"
             
    def query(self,q):
        if self.remote :
            try :
                app.logger.debug("Connecting to {}".format(self.endpoint))
                json_results = self.session.get(self.endpoint, params={'query':q})
                json_parser = JSONResultParser()
                return json_parser.parse(StringIO(json_results.text))
            except Exception as e:
                emit("Problem running query : {}".format(e.message))
                app.logger.warning("Problem running query : {}".format(e.message))
                raise e
        else :
            app.logger.debug("Directly querying internal store")
            return self.graph.query(q)
            



def emit(message):
    socketio.emit('message',
                  {'data': message },
                  namespace='/log')
