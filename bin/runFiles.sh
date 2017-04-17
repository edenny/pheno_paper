#!/bin/bash
# script to triplify and/or reason over a list of files
# here we assume the configuration file has been made and
# the files have been pre-processed

# careful of relative paths.  The following assumes a structure like:

#>ontopilot
#    >bin
#    	>ontopilot.py
#>ppo_pre_reasoner
#    >Incoming
#    >Outgoing
#>pheno_paper
#    >data
#       >npn
#       >pep725
#    >bin

ontopilot=./ontopilot/bin/ontopilot.py

# execute the triplify and reason functions for a given project and list of files
function runLoop {
    project=$1
    files=$2
    # run the loop
    for file in "${files[@]}"
    do
        # triplify
        make -f ../Makefile ppo-fims-triples file_name=../data/$project/output_csv_split/$file output_directory=../data/$project/output_unreasoned_n3/ configuration_file=../$project/$project.xml format=TURTLE
        # reason
        make -f ../Makefile reasoner project_name=$project file_name=$file.n3 ontopilot=$ontopilot ppo_pre_reasoner_dir=../../ppo_pre_reasoner/ base_input_dir=../pheno_paper/data/$project/output_unreasoned_n3/ output_file=../pheno_paper/data/$project/output_reasoned_owl/$file.owl
    done
}

function runTriplifyTest {
	# run Triplifier
        make -f ../Makefile ppo-fims-triples file_name=../tests/triplifier_input/npntest.csv output_directory=../tests/triplifier_actual_output/ configuration_file=../tests/tests.xml format=N-TRIPLE
	# compare outpt
}

####################
# Tests
####################
runTriplifyTest

####################
# Betula files
####################
#files=( Betula_1.csv Betula_2.csv Betula_3.csv Betula_4.csv Betula_5.csv Betula_6.csv Betula_7.csv )
#runLoop pep725 $files
#files=( 1485012823554_1.csv 1485012823554_2.csv 1485012823554_3.csv 1485012823554_4.csv )
#runLoop npn $files

