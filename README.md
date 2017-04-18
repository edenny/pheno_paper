# Phenology Paper Processing Steps

This repository contains all of the scripts for processing the data sources for a Plant
Phenology Paper, looking at Birch and Common Sunflower datasources coming from  the NPN
and PEP725 projects.  This process covers the complete life-cycle of the project, covering building
an application ontology, building the Field Information Management (FIMS) validation and configuration
files, pre-processing data sources, creating triples from pre-processed data sources, and finally
reasoning over the triples.

Note that while this repository is focused specifically on two datasets, i've excluded 
the actual data from the actual repository since they are too large to handle through git.
I've chosen to store them locally in a directory called "data" and have added this directory to the 
.gitignore file. 

# Step 1: Create FIMS configuration file(s) 

The second step involves building a Bicode FIMS configuration file for each project.  The FIMS
configuration file specifies the validation rules and how the data will be triplified later.

You will need to read the documentation for creating Configurator configuration files at under the [Biocode FIMS Configurator Repository] (https://github.com/biocodellc/biocode-fims-configurator) and create the appropriate directories locally.

E.g. for npn first time only create the following directories and populate with the correct configuration files.
```
  mkdir npn
  mkdir npn/config
```

Now you you will need to run the configurator, calling the buildConfig.sh script and 
passing in your project name.  Note that you must first adjust local variables in build.properties:
```
  cd bin
  ./buildConfig.sh npn
```

Once the configurator does its work and we have succesfully built a configuration you should push 
the completed config file to github (or wherever it should be accessed on the web)
 
# Step 2: Pre-processing 

The data from NPN and PEP725 will need some modifications to make them
suitable for turning in to RDF triples.  This step is necessary as the incoming source data is 
stored in formats that are not easily parseable and contain assumptions about the data itself which need to be made explicit.

Run the [NPN file pre-processing script] (https://github.com/jdeck88/pheno_paper/blob/master/npn/npnProcessFiles.py)

```
  python npnProcessFiles.py
```

Unpack the PEP725 file downloads using [PEP725 unpacker script] https://github.com/jdeck88/pheno_paper/blob/master/pep725/pepProcessTar.sh) and then run the [PEP725 pre-processing script] (https://github.com/jdeck88/pheno_paper/blob/master/pep725/pepProcessFiles.py)

```
  ./pepProcessTar.sh
  python pepProcessFiles.py
```

# Step 3: Splitting, Triplifying, and Reasoning

These three steps can be run at once using the bin/runFiles.sh script, like:
```
  cd bin
  ./runFiles.sh <project> <filename>
```

*Splitting data* is done using a python script called fileSplitter.py and called from the runFiles.sh script (above).  The file splitter splits incoming CSV files into 50,000 records or less. 


*Triplifying FIMS* data is done using the [ppo-fims java code-base](https://github.com/biocodellc/ppo-fims) which loads tabular data into a temporary SQLITE database, runs a series of validation rules on the data itself, and, if it passes, calls D2RQ for creating RDF triples from the loaded data.  


*Reasoning* is done using the Ontopilot project to pre-reason data sources.  The current (and temporary! process) is to run this through the ppo_pre_reasoner (called through a shell script).  Note that for this step we need to check out the following repositories:

https://github.com/plantphenoontology/ppo_pre_reasoner/

https://github.com/stuckyb/ontopilot  (for now, use the elk_pipeline branch)


# Step 4: Data Storage / Indexing

*SPARQL Endpoint *

Reasoned data is being loaded into a BlazeGraph SPARQL endpoint at http://data.plantphenology.org/  ..  Email the owner of this repository if you would like access to this host if you want to try out queries.  Note that we do not yet have a stable namespace for loaded SPARQL queries so you should be careful about using the most up to date namespace for loaded data.  One can use the GUI interface for running queries, or instead issue SPARQL by calling the blazegraph REST API.

A very simple SPARQL command to get data back from this endpoint for the pheno_paper3 namespace is here:

```
curl -X POST http://data.plantphenology.org/blazegraph/namespace/pheno_paper3/sparql --data-urlencode 'query=SELECT * { ?s ?p ?o } LIMIT 1' -H 'Accept:text/csv'
```

A more complex curl statement that returns flowering time, day of year, and year for Genus = "Helianthus":

```
curl -X POST http://data.plantphenology.org/blazegraph/namespace/pheno_paper3/sparql -H 'Accept:text/csv' --data-urlencode 'query=prefix dwc: <http://rs.tdwg.org/dwc/terms/> prefix obo: <http://purl.obolibrary.org/obo/>  SELECT  ?startDayOfYear ?year ?latitude ?longitude ?wholePlant WHERE {    ?wholePlant dwc:genus "Helianthus"^^<http://www.w3.org/2001/XMLSchema#string> . optional{?wholePlant dwc:specificEpithet "annuus"^^<http://www.w3.org/2001/XMLSchema#string>} . ?wholePlant obo:RO_0000086 ?plantStructurePresence . ?plantStructurePresence rdf:type obo:PPO_0003010 . ?plantStructurePresence obo:PPO_0001007 ?measurementDatum . ?measurementDatum obo:OBI_0000312 ?phenologyObservingProcess . ?phenologyObservingProcess rdf:type obo:PPO_0002000 . ?phenologyObservingProcess dwc:startDayOfYear ?startDayOfYear . ?phenologyObservingProcess dwc:year ?year . ?phenologyObservingProcess dwc:decimalLatitude ?latitude . ?phenologyObservingProcess dwc:decimalLongitude ?longitude . } ORDER BY ?startDayOfYear ?year'
```

Here is the SPARQL in the above statement:

```
prefix dwc: <http://rs.tdwg.org/dwc/terms/> 
prefix obo: <http://purl.obolibrary.org/obo/>  
SELECT  ?startDayOfYear ?year ?latitude ?longitude ?wholePlant 
WHERE {    
	?wholePlant dwc:genus "Helianthus"^^<http://www.w3.org/2001/XMLSchema#string> . 
	optional{ ?wholePlant dwc:specificEpithet "annuus"^^<http://www.w3.org/2001/XMLSchema#string> } . 

	# wholePlant 'hasQuality' some plantStructurePresence
	?wholePlant obo:RO_0000086 ?plantStructurePresence . 

	# search for flower heads present
	?plantStructurePresence rdf:type obo:PPO_0003010 . 

	# plantStructurePresence 'has quality measurement' some measurementDatum
	?plantStructurePresence obo:PPO_0001007 ?measurementDatum . 
	
	# measurementDatum 'is_specified_output_of' some phenologyObservingProcess
	?measurementDatum obo:OBI_0000312 ?phenologyObservingProcess . 

	# set the type for phenologyObservingProcess and return properties
	?phenologyObservingProcess rdf:type obo:PPO_0002000 . 
	?phenologyObservingProcess dwc:startDayOfYear ?startDayOfYear . 
	?phenologyObservingProcess dwc:year ?year . 
	?phenologyObservingProcess dwc:decimalLatitude ?latitude . 
	?phenologyObservingProcess dwc:decimalLongitude ?longitude . 
} ORDER BY ?startDayOfYear ?year'
```
*ElasticSearch* 

Data loading into ElasticSearch still under development... nothing to report here for now.

# NOTES

Configuration files for projects are stored off of the root path and are named according to the source they were derived from.
Each directory contains a configuration file and has a different purpose.

{project} 

Contains pre-processing code and FIMS configuration file generation code.
Contains a full set of classes, relations between classes, and all of the annotations needed to describe the data.  This configuration results in the 
most complex view of the data of all of the configurations and contains multiple defined relations.  

{project}_direct

Contains pre-processing code and FIMS configuration file generation code. The assumption behind the "direct" here is that no inferencing 
will be run on this data, and instead, we will directly map presence/absence classes for "trait present" / "trait absent" instead of 
marking "trait presence" and using measurement datums to infer whether the trait is present or not.  This method requires the logic to be
handled by the creator of the instance data creater and uses the ontology merely as a "dictionary" of terms to apply to source data.

{project}_short
Contains pre-processing code and FIMS configuration file generation code.
Contains only two classes: plantStructurePresence and measurementDatum.  All of the Annotation properties from the source data
are contained these classes. 

{project}_mini
Contains pre-processing code and FIMS configuration file generation code.
Contains only two classes: plantStructurePresence and measurementDatum.  Only the Datatype properties are included here  that are absolutely necessary for inferencing to happen (counts and percents)
are contained these classes. 


