#!/bin/bash
# runFiles.sh
# A Bash script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.

usage="Script to pre-process, triplify, and reason over phenology data sources\n 
Usage:
runFiles.sh {project} {init}
    project = name of project
    init = true|false (defaults to false)\n"

# Arguments
if [ $1 == '-h' ]; then
   printf "$usage"
   exit 1
fi

# project = the short name of the project we are working with (e.g. npn, pep725)
project=$1
# the initialize boolean variable
init=$2

curdir=$PWD

# prop function for adding in script properties
# replace content in square brackets with project variable
function prop {
    grep -w "${1}" $curdir/build.properties|cut -d'=' -f2 | sed "s/\[project\]/$project/g"
}

# Reason
# execute the reasoning process for a list of files
# NOTE: this function will be simplified greatly when ontopilot comes
# up with a separate build task for instance data.  Currently, there
# are coded here several work-arounds to make it work before this happens.
function reason {
    echo "#=========================================================="
    echo "# Reason "
    echo "#=========================================================="
    #The base ontology file could not be found: /Users/jdeck/IdeaProjects/pheno_paper/data/npn/output_unreasoned_n3/test_1.csv.ttl
    files=$1
    for file in $split_files
    do
	# get just the filename
	localFileName=$(basename $file)
	incomingFile=$(prop 'unreasoned_dir')$localFileName.ttl

	# NOTE: Section below is TEMPORARY, until improved pipeline features
	# are in place
	outgoingFile=Outgoing/$localFileName.owl
	reasonedFile=$curdir/build/$localFileName-reasoned.owl
	destinationFile=$(prop 'reasoned_dir')$localFileName.owl

	# clean build directory before running
	rm -f $curdir/build/*

	# adjust configuration file
	sed -i "s|^base_ontology_file =.*|base_ontology_file = $incomingFile|" $(prop 'reasoner_config')
	sed -i "s|^ontology_file =.*|ontology_file = $outgoingFile|" $(prop 'reasoner_config')

	cd $(prop 'ppo_pre_reasoner_dir')
	# run ontopilot
	$(prop 'ontopilot') --reason make ontology \
		-c $(prop 'reasoner_config') \
		2> $outgoingFile.err
	# This should be the new syntax
	#$(prop 'ontopilot') inference_pipeline \
	#	-i $incomingFile \
	#	-o $destinationFile \
	#	-c $(prop 'reasoner_config') 
	#	#2> $outgoingFile.err

	echo "    writing $destinationFile"
	mv $reasonedFile $destinationFile
	cd $curdir

    done
}

# Triplify 
# execute the triplify process for a list of files
function triplify {
    echo "#=========================================================="
    echo "# Triplify "
    echo "#=========================================================="
    files=$1
    # clean build directory before running
    rm -f $curdir/output/*
    for file in $split_files
    do
        java -Xmx4048m -jar $(prop 'triplifier') \
	    -i $file \
	    -o $(prop 'unreasoned_dir') \
	    -c $(prop 'triplifier_config') \
	    -F TURTLE
    done
}

function preProcess {
    echo "#=========================================================="
    echo "# Pre-Process"
    echo "#=========================================================="
    echo python $(prop 'pre_processor_script') \
	 $(prop 'input_dir') \
	 $(prop 'output_csv_dir')
    python $(prop 'pre_processor_script') \
	 $(prop 'input_dir') \
	 $(prop 'output_csv_dir')
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

# Split Files
# Run the file splitting process
# splits incoming files into 50,000 sets numbered _1,_2, etc...
function split {
    python fileSplitter.py \
        $(prop 'output_csv_dir')$inputFilename \
	$(prop 'output_csv_split_dir')
}

# get a list of files in the output directory and let user choose which one to 
# process on
function fileChooser {
    echo "#=========================================================="
    echo "# File Chooser"
    echo "#=========================================================="
    cd $(prop 'output_csv_dir')
    options=(*)
    cd $curdir

    menu() {
        echo "Choose one or more files:"
        for i in ${!options[@]}; do 
            printf "%3d%s) %s\n" $((i+1)) "${choices[i]:- }" "${options[i]}"
        done
        [[ "$msg" ]] && echo "$msg"; :
    }

    prompt="Check an option (again to uncheck, ENTER when done): "
    while menu && read -rp "$prompt" num && [[ "$num" ]]; do
        [[ "$num" != *[![:digit:]]* ]] &&
           (( num > 0 && num <= ${#options[@]} )) ||
        { msg="Invalid option: $num"; continue; }
       	((num--)); msg="${options[num]} was ${choices[num]:+un}checked"
    	[[ "${choices[num]}" ]] && choices[num]="" || choices[num]="+"
    done

    # Assign filenames that were checked to filesToProcess array variable
    filesToProcess=()
    for i in ${!options[@]}; do 
	if [[ ${choices[i]} == "+" ]]
	then
	    filesToProcess+=(${options[i]})
	fi
    done
}

# initialize necessary processing directories, if needed
# we don't attempt creation of output_csv since that should be populated to start with!
function init {
    echo "#=========================================================="
    echo "# Initializing and checking directories for "$project
    echo "#=========================================================="
    if [ ! -d $(prop 'unreasoned_dir') ]; 
    then
        mkdir -p $(prop 'unreasoned_dir')
    fi
    if [ ! -d $(prop 'reasoned_dir') ]; 
    then
        mkdir -p $(prop 'reasoned_dir')
    fi
    if [ ! -d $(prop 'output_csv_split_dir') ]; 
    then
        mkdir -p $(prop 'output_csv_split_dir')
    fi
    preProcess
}

if [ "$init" = true ] ; then
	init   			# initialize
fi
fileChooser 		# fileChooser

# loop results from file choosing
for f in ${filesToProcess[@]}; do
    inputFilename=$f
    split 		# split files
    getSplitFiles	# get all the split files
    triplify		# triplify
    reason		# reason
done
