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

example SPARQL query
```
curl -X POST -H 'Accept: text/csv' http://localhost:9999/blazegraph/namespace/test/sparql --data-urlencode 'query=SELECT * { ?s ?p ?o } LIMIT 1'  > foo
```

Create a namespace
```
curl -X POST -H 'Content-Type: application/xml' --data @pheno_paper.namespace.xml http://localhost:9999/blazegraph/namespace
```

Delete a namespace (careful!)
```
curl -X DELETE -H 'Content-Type: application/xml' http://localhost:9999/blazegraph/namespace/NAMESPACE
```



