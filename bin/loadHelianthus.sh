#!/bin/bash
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/pep725/output_reasoned_owl/Helianthus.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper_helianthus/sparql

curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/npn/output_reasoned_owl/1485013283920.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper_helianthus/sparql
