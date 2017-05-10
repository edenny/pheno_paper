# Useful Commands in this directory
buildConfig.sh (build configuration files)
runFiles.sh (pre-process, split, triplify, reason, post-process files)

An example of the runFiles script, loading data
```
./runFiles.sh npn npn_paper load test
```

An example of the runFiles script, initializing (pre-processing)
```
./runFiles.sh npn npn_paper init
```

# Some useful commands for working with blazegraph

example SPARQL query, referencing sparql as part of request
```
curl -X POST -H 'Accept: text/csv' http://localhost:9999/blazegraph/namespace/test/sparql --data-urlencode 'query=SELECT * { ?s ?p ?o } LIMIT 1'  > foo
```

example SPARQL query, referencing sparql contained in a file and redirecting output
```
curl -X POST -H 'Accept: text/csv' http://localhost:9999/blazegraph/namespace/pheno_paper/sparql --data-urlencode query@test.sparql  > test.output
```

Create a namespace. Note that immediately following namespace creation we load any supporting ontologies.
For *some* reason, it only works to first load the ontology file and then instance data.  If you do it in the
opposite order it takes a very long time to load.
```
curl -X POST -H 'Content-Type: application/xml' --data @pheno_paper.namespace.xml http://localhost:9999/blazegraph/namespace
curl -X POST -H 'Content-Type: application/xml' --data-binary @/home/jdeck88/code/PPO/ontology/ppo-reasoned.owl http://localhost:9999/blazegraph/namespace/pheno_paper/sparql
```

Delete a namespace (careful!)
```
curl -X DELETE -H 'Content-Type: application/xml' http://localhost:9999/blazegraph/namespace/NAMESPACE
```
