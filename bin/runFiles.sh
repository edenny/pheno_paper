#!/bin/bash
# script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.

# Set paths--- these may need to be adjusted depending on your environment
ontopilot=../ontopilot/bin/ontopilot.py
ppo_pre_reasoner=../../ppo_pre_reasoner
tests_input_directory=../tests/triplifier_input
tests_actual_output_directory=../tests/triplifier_actual_output
tests_expected_output_directory=../tests/triplifier_expected_output
root_data_directory=../pheno_paper/data
unreasoned_directory=output_unreasoned_n3
reasoned_directory=output_reasoned_owl
initial_csv_directory=output_csv
incoming_csv_directory=output_csv_split

# execute the reasoning process for a list of files
function reason {
    echo "########################"
    echo "# Reason "
    echo "########################"
    files=$1

    # run the loop
    for file in "${files[@]}"
    do
	localFileName=$(basename $file)
        # reason
        make -f ../Makefile reasoner project_name=$project file_name=$localFileName.ttl ontopilot=$ontopilot ppo_pre_reasoner_dir=$ppo_pre_reasoner/ base_input_dir=$root_data_directory/$project/$unreasoned_directory/ output_file=$root_data_directory/$project/$reasoned_directory/$localFileName.owl
    done
}

# execute the triplify process for a list of files
function triplify {
    echo "########################"
    echo "# Triplify "
    echo "########################"
    files=$1

    # run the loop
    for file in "${files[@]}"
    do
        # triplify
        #make -f ../Makefile ppo-fims-triples file_name=../$root_data_directory/$project/$incoming_csv_directory/$file output_directory=../$root_data_directory/$project/$unreasoned_directory/ configuration_file=../$project/$project.xml format=TURTLE
        make -f ../Makefile ppo-fims-triples file_name=$file output_directory=../$root_data_directory/$project/$unreasoned_directory/ configuration_file=../$project/$project.xml format=TURTLE
    done
}

# test the tripflifier process
# This should be run each time configuration file changes
function testTriplifier {
    # triplify test sources
    make -f ../Makefile ppo-fims-triples file_name=$tests_input_directory/$project-test.csv output_directory=$tests_actual_output_directory/ configuration_file=../$project/$project.xml format=N-TRIPLE
    # compare output
    python runTriplifierTest.py $tests_actual_output_directory/$project-test.csv.n3 $tests_expected_output_directory/$project-test.csv.n3
}

# Return all of the files that have been split
function getSplitFiles {
    getSplitFilesInputFilename=../$root_data_directory/$project/$incoming_csv_directory/$inputFilename
    cmd=$getSplitFilesInputFilename"_*.csv"
    split_files=($cmd)
}

# run the file splitting process
function split {
    splitFilesInputFilename=../$root_data_directory/$project/$initial_csv_directory/$inputFilename
    outputDirectory=../$root_data_directory/$project/$incoming_csv_directory
    python fileSplitter.py $splitFilesInputFilename $outputDirectory
}

project=npn
#inputFilename=1485012823554.csv
inputFilename=test.csv

# Tests
# The following tests are built for each project to test output from the triplification
# process.  The reasoning process is not tested here but has its own set of tests
# Uncommient the following line to enable tests
#
# testTriplifier

# Split Files
# We set a maximum limit of 50,000 records for each incoming file
# The file splitter takes incoming files and splits into 50,000 sets numbered _1,_2, etc...
split

# Fetch Split Files
# Once files have been split, fetch a listing of the splitting process into the split_files 
# global array.  This global is used for triplifying and reasoning.
getSplitFiles 

# Triplify Files
triplify $split_files

# Reason on Files
reason $split_files
