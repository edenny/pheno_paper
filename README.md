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
  %mkdir build
  %cd build # and remove files if doing a fresh build
  %make -f ../Makefile imports # build the imports
  %make -f ../Makefile  #build the ontology and writes to ontology/ppo_ingest.owl)
```		
# Step 2: Create FIMS configuration file(s) 

The second step involves building a Bicode FIMS configuration file for each project.  The FIMS
configuration file specifies the validation rules and how the data will be triplified later.

You will need to read the documentation for creating Configurator configuration files at under the [Biocode FIMS Configurator Repository] (https://github.com/biocodellc/biocode-fims-configurator) and create the appropriate directories locally.

E.g. for npn first time only create the following directories and populate with the correct configuration files.
```
  %mkdir npn
  %mkdir npn/config
```

Now you you will need to run the configurator, pointing the Makefile to the appropriate directory where the biocode-fims-configurator lives:
```
  %cd build
  %make -f ../Makefile configurator project_name="{project_name}"
```

Once the configurator does its work and we have succesfully built a configuration you should push 
the completed config file to github (or wherever it should be accessed on the web)
 
# Step 3: Pre-processing 

The data from NPN and PEP725 will need some modifications to make them
suitable for turning in to RDF triples.  This step is necessary as the incoming source data is 
stored in formats that are not easily parseable and contain assumptions about the data itself which need to be made explicit.

Run the [NPN file pre-processing script] (https://github.com/jdeck88/pheno_paper/blob/master/npn/npnProcessFiles.py)

```
  %python npnProcessFiles.py
```

Unpack the PEP725 file downloads using [PEP725 unpacker script] https://github.com/jdeck88/pheno_paper/blob/master/pep725/pepProcessTar.sh) and then run the [PEP725 pre-processing script] (https://github.com/jdeck88/pheno_paper/blob/master/pep725/pepProcessFiles.py)

```
  %./pepProcessTar.sh
  %python pepProcessFiles.py
```

# Step 4: Triplification

Triplifying FIMS data is done using the [ppo-fims java code-base](https://github.com/biocodellc/ppo-fims) which loads tabular data into a temporary SQLITE database, runs a series of validation rules on the data itself, and, if it passes, calls D2RQ for creating RDF triples from the loaded data.   The general structure for the RDF triples is first configured by FIMS (in step 2) and then is run through the [D2RQ] (http://d2rq.org/) engine for the actual triple creation. Coming is an executable java application for this step but for now, this can be run inside yoru Java IDE and running the generateTriplesForPaper main class.

# Step 5: Reasoning

We use the Ontopilot project to pre-reason data sources.  The current (and temporary! process) is to run this through our makefile:

```
  %cd build
  %make -f ../Makefile reasoner project_name=npn file_name=test.csv.n3
```
