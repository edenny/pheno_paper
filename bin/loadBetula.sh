#!/bin/bash
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/pep725/output_reasoned_owl/Betula_1.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/pep725/output_reasoned_owl/Betula_2.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/pep725/output_reasoned_owl/Betula_3.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/pep725/output_reasoned_owl/Betula_4.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql

curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/npn/output_reasoned_owl/1485012823554_1.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql
curl -X POST -H 'Content-Type:application/xml' --data-binary '@../data/npn/output_reasoned_owl/1485012823554_2.csv.owl' http://localhost:9999/blazegraph/namespace/pheno_paper2/sparql
