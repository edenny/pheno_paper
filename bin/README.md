# example request to create a namespace
curl -X POST -H 'Content-Type: application/xml' --data @pheno_paper.namespace.xml http://localhost:9999/blazegraph/namespace

# example request to delete a namespace
curl -X DELETE -H 'Content-Type: application/xml' http://localhost:9999/blazegraph/namespace/pheno_paper

# example for loading daa:
./runFiles.sh npn npn_paper load test

