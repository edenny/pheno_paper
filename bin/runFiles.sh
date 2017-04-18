#!/bin/bash
# script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.
                                                                                       
if [ $# -ne 2 ] 
then
   echo "Invalid number of arguments"
   echo "runFiles.sh {project} {filename.csv}"
   exit 1
fi

curdir=$PWD
project=$1
inputFilename=$2

# prop function for adding in script properties
# replace content in square brackets with project variable
function prop {
    grep -w "${1}" $curdir/build.properties|cut -d'=' -f2 | sed "s/\[project\]/$project/g"
}

#echo $(prop 'app.server.address')

# execute the reasoning process for a list of files
# NOTE: this function will be simplified greatly when ontopilot comes
# up with a separate build task for instance data.  Currently, there
# are coded here several work-arounds to make it work before this happens.
function reason {
    echo "########################"
    echo "# Reason "
    echo "########################"
    #The base ontology file could not be found: /Users/jdeck/IdeaProjects/pheno_paper/data/npn/output_unreasoned_n3/test_1.csv.ttl
    files=$1
    for file in $split_files
    do
	# get just the filename
	localFileName=$(basename $file)
	incomingFile=$(prop 'unreasoned_dir')$localFileName.ttl

	#outgoingFile=$(prop 'reasoned_dir')$localFileName.owl
	#reasonedFile=$(prop 'reasoned_dir')$localFileName-reasoned.owl
	outgoingFile=Outgoing/$localFileName.owl
	reasonedFile=$curdir/build/$localFileName-reasoned.owl
	destinationFile=$(prop 'reasoned_dir')$localFileName.owl

	# adjust configuration file
	sed -i "s|^base_ontology_file =.*|base_ontology_file = $incomingFile|" $(prop 'reasonerConfig')
	sed -i "s|^ontology_file =.*|ontology_file = $outgoingFile|" $(prop 'reasonerConfig')

	cd $(prop 'ppo_pre_reasoner_dir')
	# run ontopilot
	$(prop 'ontopilot') --reason make ontology \
		-c $(prop 'reasonerConfig') \
		2> $outgoingFile.err

	echo "    writing $destinationFile"
	mv $reasonedFile $destinationFile
	cd $curdir

    done
}

# execute the triplify process for a list of files
function triplify {
    echo "########################"
    echo "# Triplify "
    echo "########################"
    files=$1
    #for file in "${files[@]}"
    for file in $split_files
    do
        java -Xmx4048m -jar ./ppo-fims-triples.jar \
	    -i $file \
	    -o $(prop 'unreasoned_dir') \
	    -c $(prop 'triplifierConfig') \
	    -F TURTLE
    done
}

# test the tripflifier process
# This should be run each time configuration file changes
function testTriplifier {
    echo "########################"
    echo "# Triplify Test"
    echo "# Igorning input file and using default test file for projec "
    echo "# which resides in tests directory"
    echo "########################"
    # triplify test sources
    java -Xmx4048m -jar ./ppo-fims-triples.jar \
        -i $(prop 'tests_input_dir')$project-test.csv \
	-o $(prop 'tests_actual_output_dir') \
	-c $(prop 'triplifierConfig') \
	-F N-TRIPLE
    # compare output
    python runTriplifierTest.py \
        $(prop 'tests_actual_output_dir')$project-test.csv.nt \
	$(prop 'tests_expected_output_dir')$project-test.csv.n3
}

# Return all of the files that have been split WITHOUT the extension
function getSplitFiles {
    lfilename=$(basename "$inputFilename")
    #just extension
    lextension="${lfilename##*.}"
    #filename w/out extension
    lfilename="${lfilename%.*}"
    # return files without extension
    split_files=$(prop 'output_csv_split_dir')$lfilename"_*.csv"
}

# run the file splitting process
function split {
    python fileSplitter.py \
        $(prop 'output_csv_dir')$inputFilename \
	$(prop 'output_csv_split_dir')
}

#project=$2
#inputFilename=1485012823554.csv
#inputFilename=test.csv

# Tests
# The following tests are built for each project to test output from the triplification
# process.  The reasoning process is not tested here but has its own set of tests
# Uncommient the following line to enable tests
#
#testTriplifier

# Split Files
# splits incoming files into 50,000 sets numbered _1,_2, etc...
split

# Fetch Split Files into split_files global array
getSplitFiles 

# Triplify Files
triplify 

# Reason on Files
reason 
