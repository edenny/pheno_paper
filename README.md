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

# Step 1: Create application ontology

The first step is creating the application ontology file which is built especially 
for annotating incoming data sources with relevant PPO terms.   Occassionally other terms for other 
ontologies will be added to the PPO core set of terms which are useful for annotating incoming instance data.
This step should be performed infrequently, and will affect all incoming data sources.  The process for building the 
ingest file  draws from the [ontopilot] (https://github.com/stuckyb/ontopilot) application.

```
  mkdir build
  cd build # and remove files if doing a fresh build
  make -f ../Makefile imports # build the imports
  make -f ../Makefile  #build the ontology and writes to ontology/ppo_ingest.owl)
```		
# Step 2: Create FIMS configuration file(s) 

The second step involves building a Bicode FIMS configuration file for each project.  The FIMS
configuration file specifies the validation rules and how the data will be triplified later.

You will need to read the documentation for creating Configurator configuration files at under the [Biocode FIMS Configurator Repository] (https://github.com/biocodellc/biocode-fims-configurator) and create the appropriate directories locally.

E.g. for npn first time only create the following directories and populate with the correct configuration files.
```
  mkdir npn
  mkdir npn/config
```

Now you you will need to run the configurator, pointing the Makefile to the appropriate directory where the biocode-fims-configurator lives:
```
  cd build
  make -f ../Makefile configurator project_name="{project_name}"
```

Once the configurator does its work and we have succesfully built a configuration you should push 
the completed config file to github (or wherever it should be accessed on the web)
 
# Step 3: Pre-processing 

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

# Step 4: Triplification

Triplifying FIMS data is done using the [ppo-fims java code-base](https://github.com/biocodellc/ppo-fims) which loads tabular data into a temporary SQLITE database, runs a series of validation rules on the data itself, and, if it passes, calls D2RQ for creating RDF triples from the loaded data.  

```
  cd build
  make -f ../Makefile ppo-fims-triples file_name={input file location} output_directory={directory to send output to} configuration_file={FIMS configuration file location}
```

# Step 5: Reasoning

We use the Ontopilot project to pre-reason data sources.  The current (and temporary! process) is to run this through the ppo_pre_reasoner (called through a shell script).  Note that for this step we need to check out the following repositories:

https://github.com/plantphenoontology/ppo_pre_reasoner/

https://github.com/stuckyb/ontopilot  (for now, use the elk_pipeline branch)

Once these repositories are installed you can call the following commands.  You will need to adjust path settings in bin/runReasoner.sh
```
  cd build
  make -f ../Makefile reasoner project_name=npn file_name=test.csv.n3
```

# Step 6: Data Storage / Indexing

*ElasticSearch* 

Reasoned data going to ElasticSearch

*SPARQL Endpoint *

Reasoned data also going int SPARQL

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


