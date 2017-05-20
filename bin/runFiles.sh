#!/bin/bash
# runFiles.sh
# A Bash script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.
usage="
#==========================================================
Script to pre-process, triplify, and reason over phenology data sources 
#==========================================================

Usage: runFiles.sh {option} {project} {dataDir} {namespace}
    project         Name of project. Corresponds to FIMS configuration
		    file and preProcessing script locations
    dataDir         The data processing directory 
    namespace       Optional: for loading only
    option          Select an option for running:
        init        Pre-process files, reading incoming formats and 
		    converting to read to ingest CSV
        process     Process selected files: split, triplify, reason, 
		    post-process
        processAll  Process all available files without user input: 
		    split, triplify, reason, post-process
        clean       Remove files from output directories except input 
		    and output_csv
        load        Load selected files to SPARQL endpoint.  With this 
                    option also must specify namespace
        loadAll     Load all available files to SPARQL endpoint without 
		    user input.  With this option also must specify namespace

"

# Arguments
if [[ $1 == '-h' ]] || [ "$#" -lt 1 ] || [ "$#" -gt 4 ]; then
   printf "$usage"
   exit 1
fi

# option corresponds to optional processing options
option=$1
# project is the short name of the project we are working with (e.g. npn, pep725)
project=$2
# data_dir corresponds to where the project data directory lives. each project
# may have more than one data directory location
data_dir=$3
namespace=$4

curdir=$PWD

# replace [project] appearing in properties file with project variable
function prop {
    grep -w "${1}" $curdir/build.properties|cut -d'=' -f2 | sed "s/\[project\]/$project/g"
}
# replace [data_dir] appearing in properties file with data_dir variable
function prop_data {
    grep -w "${1}" $curdir/build.properties|cut -d'=' -f2 | sed "s/\[data_dir\]/$data_dir/g"
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

    for file in ${split_files[@]}
    do
	echo $(prop 'ontopilot') inference_pipeline \
		-i $(prop_data 'output_unreasoned_dir')$file.ttl \
		-o $(prop_data 'output_reasoned_dir')$file.ttl\
	        -c $(prop 'reasoner_config') \
		2> $(prop_data 'output_reasoned_dir')$file.ttl.err
	$(prop 'ontopilot') inference_pipeline \
		-i $(prop_data 'output_unreasoned_dir')$file.ttl \
		-o $(prop_data 'output_reasoned_dir')$file.ttl \
	        -c $(prop_data 'reasoner_config') \
		2> $(prop_data 'output_reasoned_dir')$file.ttl.err

	echo "    writing $(prop_data 'output_reasoned_dir')$file.ttl"
    done
}

# Output
# Generate output from reasoned data
function output {
    echo "#=========================================================="
    echo "# Output "
    echo "#=========================================================="

    for file in ${split_files[@]}
    do
        echo java $(prop 'java_options') -jar $(prop 'query_fetcher') \
	    -i $(prop_data 'output_reasoned_dir')$file.ttl \
	    -inputFormat "TURTLE" \
	    -o $(prop_data 'output_reasoned_csv_dir') \
	    -sparql $(prop 'sparql_query') 
        java $(prop 'java_options') -jar $(prop 'query_fetcher') \
	    -i $(prop_data 'output_reasoned_dir')$file.ttl \
	    -inputFormat "TURTLE" \
	    -o $(prop_data 'output_reasoned_csv_dir') \
	    -sparql $(prop 'sparql_query') 
    done
}
# Load 
function load {
    echo "#=========================================================="
    echo "# Load"
    echo "#=========================================================="

    # clean build directory before running
    rm -f $curdir/output/*

    for file in ${split_files[@]}
    do
	echo curl \
                -Dcom.bigdata.rdf.store.DataLoader.bufferCapacity=100000 \
		-Dcom.bigdata.rdf.store.DataLoader.queueCapacity=10 \
 		-sS \
		-X POST \
		-H 'Content-Type:application/xml' \
		--data-binary \
		'@'$(prop_data 'output_reasoned_dir')$file.ttl \
		http://localhost:9999/blazegraph/namespace/$namespace/sparql
	curl \
 		-Dcom.bigdata.rdf.store.DataLoader.bufferCapacity=100000 \
		-Dcom.bigdata.rdf.store.DataLoader.queueCapacity=10 \
		-sS \
		-X POST \
		-H 'Content-Type:application/xml' \
		--data-binary \
		'@'$(prop_data 'output_reasoned_dir')$file.ttl \
		http://localhost:9999/blazegraph/namespace/$namespace/sparql
    done
}
# Triplify 
# execute the triplify process for a list of files
function triplify {
    echo "#=========================================================="
    echo "# Triplify "
    echo "#=========================================================="

    # clean build directory before running
    rm -f $curdir/output/*

    for file in ${split_files[@]}
    do
        echo java $(prop 'java_options') -jar $(prop 'triplifier') \
	    -i $(prop_data 'output_csv_split')$file \
	    -o $(prop_data 'output_unreasoned_dir') \
	    -c $(prop 'triplifier_config') \
	    -w -I $(prop 'import_src')  --prefix ppo:  -F TURTLE
        java $(prop 'java_options') -jar $(prop 'triplifier') \
	    -i $(prop_data 'output_csv_split')$file \
	    -o $(prop_data 'output_unreasoned_dir') \
	    -c $(prop 'triplifier_config') \
	    -w -I $(prop 'import_src')  --prefix ppo:  -F TURTLE
    done
}

function preProcess {
    echo "#=========================================================="
    echo "# Pre-Process"
    echo "#=========================================================="
    echo $(prop 'python') $(prop 'pre_processor_script') \
	 $(prop_data 'input_dir') \
	 $(prop_data 'output_csv_dir')
    $(prop 'python') $(prop 'pre_processor_script') \
	 $(prop_data 'input_dir') \
	 $(prop_data 'output_csv_dir')
}
# Return all of the files that have been split WITHOUT the extension
function getSplitFiles {
    lfilename=$(basename "$inputFilename")
    #just extension
    lextension="${lfilename##*.}"
    #filename w/out extension
    lfilename="${lfilename%.*}"
    # return files without extension
    split_files_all=$(prop_data 'output_csv_split_dir')$lfilename"_*.csv"
    split_files=()
    for file in $split_files_all
    do
        split_files+=($(basename "$file"))
    done

   
}

# Split Files
# Run the file splitting process
# splits incoming files into 50,000 sets numbered _1,_2, etc...
function split {
    echo "#=========================================================="
    echo "# Split Files " 
    echo "#=========================================================="
    echo $(prop 'python') fileSplitter.py  $(prop_data 'output_csv_dir')$inputFilename $(prop_data 'output_csv_split_dir') $(prop 'filesize_limit')
    $(prop 'python') fileSplitter.py  $(prop_data 'output_csv_dir')$inputFilename $(prop_data 'output_csv_split_dir') $(prop 'filesize_limit')
}

function chooseAll {
    cd $(prop_data 'output_csv_dir')
    options=(*)
    cd $curdir
    filesToProcess=()
    print $options
    for i in ${!options[@]}; do 
        filesToProcess+=(${options[i]})
    done
}

# get a list of files in the output directory and let user choose which one to 
# process on
function fileChooser {
    echo "#=========================================================="
    echo "# File Chooser"
    echo "#=========================================================="
    cd $(prop_data 'output_csv_dir')
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

function clean {
    echo "#=========================================================="
    echo "# Cleaning output directories "$project
    echo "#=========================================================="
    rm -f $curdir/output/*
    rm -f $curdir/build/*
    rm -f $(prop_data 'output_unreasoned_dir')*
    rm -f $(prop_data 'output_reasoned_dir')*
    rm -f $(prop_data 'output_reasoned_csv_dir')*
    rm -f $(prop_data 'output_csv_split_dir')*
    rm -f $(prop_data 'output_csv')*
}

function processLoop {
    # loop results from file choosing
    for f in ${filesToProcess[@]}; do
        inputFilename=$f
        split 		# split files
        getSplitFiles	# get all the split files
        triplify		# triplify
        reason		# reason
        output 		# output task
    done
}
# initialize necessary processing directories, if needed
# we don't attempt creation of output_csv since that should be populated to start with!
function init {
    echo "#=========================================================="
    echo "# Initializing and checking directories for "$project
    echo "#=========================================================="
    if [ ! -d $(prop_data 'output_unreasoned_dir') ]; 
    then
        mkdir -p $(prop_data 'output_unreasoned_dir')
    fi
    if [ ! -d $(prop_data 'output_reasoned_dir') ]; 
    then
        mkdir -p $(prop_data 'output_reasoned_dir')
    fi
    if [ ! -d $(prop_data 'output_csv_split_dir') ]; 
    then
        mkdir -p $(prop_data 'output_csv_split_dir')
    fi
    if [ ! -d $(prop_data 'output_reasoned_csv_dir') ]; 
    then
        mkdir -p $(prop_data 'output_reasoned_csv_dir')
    fi
    preProcess
}


# Clean all files
if [ "$option" == "clean" ] ; then
    clean   			
    exit
fi

# initialize files, runs pre-Processor
if [ "$option" == "init" ] ; then
    init   		
    exit
fi

# process files option
if [ "$option" == "process" ] ; then
    fileChooser
    processLoop
    exit
fi

# process files option
if [ "$option" == "processAll" ] ; then
    chooseAll
    processLoop
    exit
fi

# load files option
if [ "$option" == "load" ] ; then
    if  [ "$#" -ne 4 ]; then
	printf "load requires 4 arguments, the last being the namespace"
   	printf "$usage"
   	exit 1
    fi
    fileChooser
    for f in ${filesToProcess[@]}; do
        inputFilename=$f
        getSplitFiles	# get all the split files
        load	
    done
    exit
fi
# load files option
if [ "$option" == "loadAll" ] ; then
    if  [ "$#" -ne 4 ]; then
	printf "load requires 4 arguments, the last being the namespace"
   	printf "$usage"
   	exit 1
    fi
    chooseAll
    for f in ${filesToProcess[@]}; do
        inputFilename=$f
        getSplitFiles	# get all the split files
        load	
    done
    exit
fi
