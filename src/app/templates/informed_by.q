PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?activity1 ?activity1_type ?activity1_label ?activity2 ?activity2_type ?activity2_label WHERE {
	
	{% if graph_uri %}
	{ GRAPH <{{graph_uri}}> {
	{% endif %}
		?activity2 prov:wasInformedBy ?activity1 .
    	OPTIONAL { ?activity1 rdf:type ?activity1_type .
    			   ?activity1_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?activity1_type)) }
    	OPTIONAL { ?activity1 rdfs:label ?activity1_label .}
    	OPTIONAL { ?activity2 rdfs:label ?activity2_label . }
    	OPTIONAL { ?activity2 rdf:type ?activity2_type .
    			   ?activity2_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?activity2_type))}
	{% if graph_uri %}
	} 
    } UNION {
    	OPTIONAL { ?activity1 rdf:type ?activity1_type .
    			   ?activity1_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?activity1_type)) }
    	OPTIONAL { ?activity1 rdfs:label ?activity1_label .}
    	OPTIONAL { ?activity2 rdfs:label ?activity2_label . }
    	OPTIONAL { ?activity2 rdf:type ?activity2_type .
    			   ?activity2_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?activity2_type))}
    }
	{% endif %}

} 