#!/bin/bash

# arg1 (project)
export project_name=$1
# arg2 (file_name)
export file_name=$2

# data directory
export data_dir="/Users/jdeck/IdeaProjects/pheno_paper/data/"$project_name"/"
#export base_ontology_file=$data_dir"output_unreasoned_n3/1485013283920.csv.n3"
export base_ontology_file=$data_dir"output_unreasoned_n3/"$file_name
export ontopilot="/Users/jdeck/IdeaProjects/ontobuilder/bin/ontopilot.py"

export ppo_pre_reasoner_dir="/Users/jdeck/IdeaProjects/ppo_pre_reasoner/"
export project_file=$ppo_pre_reasoner_dir"project.conf"

# the input file to use for the ppo_pre_reasoner
# the output file to use for the ppo_pre_reasoner
export ontology_file="Outgoing/"$file_name".owl"
export ontology_file_copyfrom="Outgoing/"$file_name"-reasoned.owl"
export ontology_file_copyto=$data_dir"output_reasoned_owl/"$file_name".owl"


# do some replacements on the project configuration file
# this is a hack, just waiting for standard in/out features on ontopilot
sed -i 's|^base_ontology_file =.*|base_ontology_file = '$base_ontology_file'|' $project_file
sed -i 's|^ontology_file =.*|ontology_file = '$ontology_file'|' $project_file
sed -i 's|^reasoner =.*|reasoner = hermit |' $project_file

# cd to the ppo_pre_reasoner directory
cd $ppo_pre_reasoner_dir

# execute the pre-reasoner command
echo "processing " $base_ontology_file
$ontopilot --reason make ontology

echo "copying to " $ontology_file_copyto
cp $ontology_file_copyfrom $ontology_file_copyto

cd $data_dir

