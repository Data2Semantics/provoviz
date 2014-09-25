PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?resource ?label WHERE {
  {% if graph_uri %}
  { GRAPH <{{ graph_uri }}> {
    { ?resource a prov:Activity . } UNION { ?resource a prov:Entity } UNION { ?resource a prov:Plan }
	?resource ?p ?o .
	OPTIONAL {?resource rdfs:label ?label . }
  } } UNION {
    { ?resource a prov:Activity . } UNION { ?resource a prov:Entity } UNION { ?resource a prov:Plan }
    GRAPH <{{ graph_uri }}> {
    	?resource ?p ?o .
    	OPTIONAL {?resource rdfs:label ?label . }
     }
  } 
  {% else %}
  { ?resource a prov:Activity . } UNION { ?resource a prov:Entity } UNION { ?resource a prov:Plan }
  OPTIONAL {?resource rdfs:label ?label . }
  {% endif %}
} ORDER BY ?label