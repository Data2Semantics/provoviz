PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?entity ?entity_type ?entity_label ?entity_time ?activity ?activity_type ?activity_label WHERE {
	{% if graph_uri %}
	{ GRAPH <{{graph_uri}}> {
	{% endif %}
		{ ?activity prov:used ?entity . }
		UNION
		{ ?entity prov:wasUsedBy ?activity . }
	  	UNION
	  	{
			?activity	prov:qualifiedUsage ?qu .
			?qu			prov:entity ?entity .
	  	}
		UNION
		{ ?activity prov:invalidated ?entity . }
		UNION
		{ ?entity prov:wasInvalidatedBy ?activity . }
	  	UNION
	  	{
			?activity	prov:qualifiedInvalidation ?qi .
			?qi			prov:entity ?entity .
	  	}
    	OPTIONAL { ?activity rdf:type ?activity_type .
    			 ?activity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			 FILTER(!isBlank(?activity_type)) }
    	OPTIONAL { ?activity rdfs:label ?activity_label . }
			OPTIONAL { ?entity prov:generatedAtTime ?entity_time .}
    	OPTIONAL { ?entity rdf:type ?entity_type .
    			 ?entity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			 FILTER(!isBlank(?entity_type)) }
    	OPTIONAL { ?entity rdfs:label ?entity_label .  }
	{% if graph_uri %}
	}
    } UNION {
    	OPTIONAL { ?activity rdf:type ?activity_type .
    			 ?activity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			 FILTER(!isBlank(?activity_type)) }
    	OPTIONAL { ?entity rdf:type ?entity_type .
    			 ?entity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			 FILTER(!isBlank(?entity_type)) }

    }
	{% endif %}



}
