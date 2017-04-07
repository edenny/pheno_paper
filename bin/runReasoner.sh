#!/bin/bash
# A temporary convenience script for running the ppo_pre_reasoner...
# i built this since running lots of files through the first incarnation
# of the ppo_pre_reasoner required renaming input/output files frequently
# this script takes care of this business, but only until ontopilot gets 
# a command line interface

# command line arguments
export project_name=$1
export file_name=$2
export ontopilot=$3
export ppo_pre_reasoner_dir=$4
export base_input_dir=$5
export output_file=$6

export curdir=$PWD
export base_ontology_file=$base_input_dir$file_name
export project_file=$ppo_pre_reasoner_dir"project.conf"

# the input file to use for the ppo_pre_reasoner
# the output file to use for the ppo_pre_reasoner
export ontology_file="Outgoing/"$file_name".owl"
export ontology_file_copyfrom="Outgoing/"$file_name"-reasoned.owl"
export ontology_file_copyto=$output_file

# do some replacements on the project configuration file
# this is a hack, just waiting for standard in/out features on ontopilot
echo "  updating " $project_file
sed -i 's|^base_ontology_file =.*|base_ontology_file = '$base_ontology_file'|' $project_file
sed -i 's|^ontology_file =.*|ontology_file = '$ontology_file'|' $project_file
# sed -i 's|^reasoner =.*|reasoner = hermit |' $project_file

# cd to the ppo_pre_reasoner directory
echo "  cd " $ppo_pre_reasoner_dir
cd $ppo_pre_reasoner_dir

# execute the pre-reasoner command
echo "  reasoning " $base_ontology_file
$ontopilot --reason make ontology 2> $curdir/$project_name-err.txt

echo "  copying output to " $(pwd)/$ontology_file_copyto
cp $ontology_file_copyfrom $ontology_file_copyto


