PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>


SELECT DISTINCT ?activity ?activity_type ?entity ?entity_type WHERE {
    ?entity prov:wasGeneratedBy ?activity .
    OPTIONAL { ?activity rdf:type ?activity_type . }
    OPTIONAL { ?entity rdf:type ?entity_type . }
} 