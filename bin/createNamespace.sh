#!/bin/bash
usage="
#==========================================================
Script to easily create a namespace in blazegraph
#==========================================================

Usage: createNamespace.sh {namespace}
    namespace       The namespace to be created.  uses default params defined
	            in this file.

"

# Arguments
if [[ $1 == '-h' ]] || [ "$#" -lt 1 ] || [ "$#" -gt 1 ]; then
   printf "$usage"
   exit 1
fi
NAMESPACE=$1
LOAD_PROP_FILE=/tmp/load.properties

cat <<EOT >> $LOAD_PROP_FILE
com.bigdata.rdf.sail.namespace=$NAMESPACE
com.bigdata.rdf.store.AbstractTripleStore.quads=false
com.bigdata.rdf.store.AbstractTripleStore.textIndex=true
com.bigdata.search.FullTextIndex.fieldsEnabled=true
com.bigdata.rdf.store.DataLoader.bufferCapacity=100000
com.bigdata.rdf.store.DataLoader.queueCapacity=10
EOT

curl -X POST --data-binary @${LOAD_PROP_FILE} --header 'Content-Type:text/plain' http://localhost:9999/blazegraph/namespace

rm -f $LOAD_PROP_FILE
