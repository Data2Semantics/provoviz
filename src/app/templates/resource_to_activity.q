PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?entity ?entity_type ?activity ?activity_type WHERE {
    ?activity prov:used ?entity .
    OPTIONAL { ?activity rdf:type ?activity_type . }
    OPTIONAL { ?concept rdf:type ?concept_type .  }
    
    
} 