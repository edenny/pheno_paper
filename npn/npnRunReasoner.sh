#!/bin/bash

export starting_dir=$PWD
export ppo_pre_reasoner_dir="/Users/jdeck/IdeaProjects/ppo_pre_reasoner/"

export data_dir="/Users/jdeck/IdeaProjects/pheno_paper/data/npn/"
# the input file to use for the ppo_pre_reasoner
#export base_ontology_file=$data_dir"output_unreasoned_n3/1485013283920.csv.n3"
export base_ontology_file=$data_dir"output_unreasoned_n3/test.csv.n3"
# the output file to use for the ppo_pre_reasoner
export ontology_file="Outgoing/test.owl"
export ontology_file_copyfrom="Outgoing/test-reasoned.owl"
export ontology_file_copyto=$data_dir"output_reasoned_owl/test.owl"

export project_file="/Users/jdeck/IdeaProjects/ppo_pre_reasoner/project.conf"

# do some replacements on the project configuration file
# this is a hack, just waiting for standard in/out features on ontopilot
sed -i 's|^base_ontology_file =.*|base_ontology_file = '$base_ontology_file'|' $project_file
sed -i 's|^ontology_file =.*|ontology_file = '$ontology_file'|' $project_file

# cd to the ppo_pre_reasoner directory
cd $ppo_pre_reasoner_dir

# execute the pre-reasoner command
echo "processing " $base_ontology_file
/Users/jdeck/IdeaProjects/ontobuilder/bin/ontopilot.py --reason make ontology

cp $ontology_file_copyfrom $ontology_file_copyto

cd $data_dir

