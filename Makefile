# Builds the ontology.  This Makefile is intended for out-of-source builds and
# will refuse to run if executed from the root of the source directory.  To
# build the ontoogy, create a separate build directory and run make from within
# this directory.  E.g., if the source directory is the current directory:
#
# $ mkdir build
# $ cd build
# $ make -f ../Makefile
#

###################################
# Build the FIMS configuration file
###################################
.PHONY: configurator
configurator: 
	$(configurator_bin)/configurator.py -d ../$(project_name)/config/ -b ../ontology/$(ontology_file) \
		-o ../$(project_name)/$(project_name).xml -n 

###################################
# Triplify
###################################
.PHONY: ppo-fims-triples
ppo-fims-triples:
	java -Xmx4048m -jar ../bin/ppo-fims-triples.jar -i $(file_name) -o $(output_directory) -c $(configuration_file) -F $(format)

###################################
# Reason
###################################
.PHONY: reasoner
reasoner:
	../bin/runReasoner.sh $(project_name) $(file_name) $(ontopilot) $(ppo_pre_reasoner_dir) $(base_input_dir) $(output_file)

###################################
# Load
###################################
.PHONY: loader
python_tools := /Users/jdeck/IdeaProjects/biocode-fims-python-tools
fims_uri := http://www.plantphenology.org/rest/v2 
loader:
	$(python_tools)/loader.py -e $(expedition_code) --create --public -u -user $(username) -pass $(password) \
		$(fims_uri) $(project_id) $(file_name)
