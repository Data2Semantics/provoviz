PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?entity1 ?entity1_type ?entity1_label ?entity2 ?entity2_type ?entity2_label WHERE {
	
	GRAPH <{{graph_uri}}> {
		?entity2 prov:wasDerivedFrom ?entity1 .
	}
	OPTIONAL { ?entity1 rdf:type ?entity1_type .
			   ?entity1_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
			   FILTER(!isBlank(?entity1_type)) }
	OPTIONAL { ?entity1 rdfs:label ?entity1_label .}
	OPTIONAL { ?entity2 rdfs:label ?entity2_label . }
	OPTIONAL { ?entity2 rdf:type ?entity2_type .
			   ?entity2_type rdfs:isDefinedBy <http://www.w3.org/ns/prov-o#> .
			   FILTER(!isBlank(?entity2_type))}
} 