PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?activity ?activity_type ?activity_label ?entity ?entity_type ?entity_label
								?entity_time ?entity_creator ?entity_modified ?entity_version (group_concat(?entity_cls;separator=", ") as ?entity_class) WHERE {
	{% if graph_uri %}
	{ GRAPH <{{graph_uri}}> {
	{% endif %}
	  { ?entity prov:wasGeneratedBy ?activity . }
	  UNION
	  { ?activity prov:generated ?entity . }
	  UNION
	  {
		?entity	prov:qualifiedGeneration ?qg .
		?qg		prov:activity ?activity .
	  }
      	OPTIONAL { ?activity rdf:type ?activity_type .
      			   ?activity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
      			   FILTER(!isBlank(?activity_type)) }
      	OPTIONAL { ?activity rdfs:label ?activity_label .}
      	OPTIONAL { ?entity rdfs:label ?entity_label . }
				OPTIONAL { ?entity prov:generatedAtTime ?entity_time .}
				OPTIONAL { ?entity rdf:type ?entity_cls .}
				OPTIONAL { ?entity dct:modified ?entity_modified .}
				OPTIONAL { ?entity dct:hasVersion ?entity_version .}
				OPTIONAL { ?entity (dct:creator|dc:creator) ?entity_creator .}
      	OPTIONAL { ?entity rdf:type ?entity_type .
      			   ?entity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
  			   FILTER(!isBlank(?entity_type))}
  	{% if graph_uri %}
  	}
    } UNION {
    	OPTIONAL { ?activity rdf:type ?activity_type .
    			   ?activity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?activity_type)) }
    	OPTIONAL { ?entity rdf:type ?entity_type .
    			   ?entity_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
    			   FILTER(!isBlank(?entity_type))}

    }
  	{% endif %}

} GROUP BY ?entity ?activity ?activity_type ?activity_label ?entity_type ?entity_label ?entity_time ?entity_creator ?entity_modified ?entity_version
