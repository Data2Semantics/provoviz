from rdflib.plugins.sparql.results.jsonresults import JSONResultParser
from rdflib import Graph
from StringIO import StringIO
from app import app, socketio
from flask import url_for
import requests

class Store(object):

    remote = False

    # Initialize the store, either with data or with endpoint (but not both)
    def __init__(self, data=None, data_format='turtle', endpoint=None, auth=None):
        app.logger.debug("Data: ")
        app.logger.debug(data)
        app.logger.debug("Endpoint: ")
        app.logger.debug(endpoint)

        if data:
            emit("Loading PROV data in Turtle format")
            if endpoint:
                app.logger.warning("You provided both data and an endpoint... the endpoint will be ignored.")

            self.remote = False
            try :
                self.graph = Graph()
                app.logger.debug('Loading PROV-O definitions from {}'.format(url_for('.static',filename='prov-o.ttl',_external=True)))
                self.graph.parse(url_for('.static',filename='prov-o.ttl',_external=True),format='turtle')


                if data.lower().startswith('http'):
                    app.logger.debug('Loading data from URL: {}'.format(data))
                    self.graph.parse(location=data,format=data_format)
                else :
                    app.logger.debug('Loading data...')
                    self.graph.parse(data=data,format=data_format)

            except Exception as e:
                emit("Store could not load data (not Turtle?)")

                raise e

        elif endpoint:
            emit("Setting SPARQL connection parameters")

            self.remote = True
            self.session = requests.Session()
            self.session.headers.update({'Accept':'application/sparql-results+json'})

            if auth:
                emit("Setting basic HTTP authentication parameters for endpoint {}".format(endpoint))
                self.session.auth = auth

            self.endpoint = endpoint
        else:
            app.logger.error("Whoops: cannot give me no data nor an endpoint!")

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
