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


# execute the triplify and reason functions for a given project and list of files
function runLoop {
    project=$1
    files=$2
    # run the loop
    for file in "${files[@]}"
    do
        # triplify
        make -f ../Makefile ppo-fims-triples file_name=../data/$project/output_csv/$file output_directory=../data/$project/output_unreasoned_n3/ configuration_file=../$project/$project.xml
        # reason
        make -f ../Makefile reasoner project_name=$project file_name=$file.n3 ontopilot=../ontopilot/bin/ontopilot.py ppo_pre_reasoner_dir=../../ppo_pre_reasoner/ base_input_dir=../pheno_paper/data/$project/output_unreasoned_n3/ output_file=../pheno_paper/data/$project/output_reasoned_owl/$file.owl
    done
}

# call the runLoop function with project_name and array of files
#files=( 1485012823554.csv  1485013283920.csv )
#runLoop npn $files
files=( Betula-20000.csv  Helianthus-20000.csv )
runLoop pep725 $files
