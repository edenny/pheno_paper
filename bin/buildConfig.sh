#!/bin/bash
# script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.
                                                                                       
if [ $# -ne 1 ] 
then
   echo "Invalid number of arguments"
   echo "runFiles.sh {project}"
   exit 1
fi

curdir=$PWD
project=$1

# prop function for adding in script properties
# replace content in square brackets with project variable
function prop {
    grep -w "${1}" $curdir/build.properties|cut -d'=' -f2 | sed "s/\[project\]/$project/g"
}


# test the tripflifier process
# This should be run each time configuration file changes
function testTriplifier {
    echo "#=========================================================="
    echo "# Triplify Test"
    echo "# Igorning input file and using default test file for projec "
    echo "# which resides in tests directory"
    echo "#=========================================================="
    # triplify test sources
    java -Xmx4048m -jar ./ppo-fims-triples.jar \
        -i $(prop 'tests_input_dir')$project-test.csv \
	-o $(prop 'tests_actual_output_dir') \
	-c $(prop 'triplifierConfig') \
	-F N3
    # compare output
    python runTriplifierTest.py \
        $(prop 'tests_actual_output_dir')$project-test.csv.nt \
	$(prop 'tests_expected_output_dir')$project-test.csv.nt
}

function buildConfig {
    echo "#=========================================================="
    echo "# Build Configuration"
    echo "#=========================================================="
    $(prop 'configurator') \
 	-d $(prop 'configuratorRoot') \
	-b $(prop 'ppo_ontology') \
	-o $(prop 'triplifierConfig') \
        -n 
}
# Builder
# builds config file
buildConfig

# Tests
# The following tests are built for each project to test output from the triplification
# process.  The reasoning process is not tested here but has its own set of tests
# Uncommient the following line to enable tests
testTriplifier

