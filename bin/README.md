# Useful Commands in this directory

# Building configuration files

Before any initializing or processing is done, we must build the configuration files for each 
project.  This is done using our build configuration script. This script relies on biocode-fims-commons
project to be accessible and appropriately formatted configuration files.
```
buildConfig.sh {project}
```

# Initializing and Processing Data

Using the runFiles script we have the option to initialize, process, and load data.  
An example of the runFiles script, using the npn project and the data directory npn_paper, 
to initialize data is:
```
./runFiles.sh init npn npn_paper 
```

An example of the runFiles script, for processing data is:
```
./runFiles.sh processAll npn npn_paper 
```

An example of the runFiles script, for loading data into a namespace called my_namespace is:
```
./runFiles.sh loadAll npn npn_paper my_namespace
```

# Blazegraph Data Tools

example SPARQL query, referencing sparql as part of request
```
curl -X POST -H 'Accept: text/csv' http://localhost:9999/blazegraph/namespace/test/sparql --data-urlencode 'query=SELECT * { ?s ?p ?o } LIMIT 1'  > foo
```

example SPARQL query, referencing sparql contained in a file and redirecting output
```
curl -X POST -H 'Accept: text/csv' http://localhost:9999/blazegraph/namespace/pheno_paper/sparql --data-urlencode query@test.sparql  > test.output
```

Create a namespace.  This is an automated script for creating a namespace, createNamespace.sh, 
which sets up our default parameters for all namespaces.  This ensure we always have the 
same namespace. Namespaces can also be created in the blazegraph front end.
```
createNamespace.sh {namespace}
```

Delete a namespace (careful!).  Namespaces can also be deleted in the blazegraph front end.
```
curl -X DELETE -H 'Content-Type: application/xml' http://localhost:9999/blazegraph/namespace/NAMESPACE
```


# ElasticSearch / FIMS Data Tools
FIMS has a ppo project loaded with all PPO data in it, which is indexed by elasticsearch.  
Returned from this query is a file handle which you can download using wget.
Queries can be sent through FIMS and to ES like:
```
curl http://www.plantphenology.org/rest/v1/projects/query/csv?q=%2BplantStructurePresenceTypes:%22http:%2F%2Fpurl.obolibrary.org%2Fobo%2FPPO:0003010%22+%2Bgenus:Acer
```

Loading data into ES using the esLoader.py script
```
esLoader.py [-h] [--drop-existing] data_dir

Script to load local elasticsearch instance with reasoned data

positional arguments:
  data_dir         the directory containing the reasoned data to load

optional arguments:
  -h, --help       show this help message and exit
  --drop-existing  this flag will drop all existing data with the same
                   "source" value.
```

Checking on progress of loading:
```
curl 'http://localhost:9200/_cat/indices?v'
```
