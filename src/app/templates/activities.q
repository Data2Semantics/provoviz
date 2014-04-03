PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?activity ?label WHERE {
  ?activity a prov:Activity .
  
  {% if graph_uri %}
  GRAPH <{{ graph_uri }}> {
	?activity ?p ?o .
	OPTIONAL {?activity rdfs:label ?label . }
  }
  {% else %}
  OPTIONAL {?activity rdfs:label ?label . }
  {% endif %}
} ORDER BY ?activity