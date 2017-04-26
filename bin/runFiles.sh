#!/bin/bash
# runFiles.sh
# A Bash script to manaage splitting, triplifying and reasoning files.  We assume the 
# configuration file has been made and the pre-processing routine has been run.
usage="
#==========================================================
Script to pre-process, triplify, and reason over phenology data sources 
#==========================================================

Usage: runFiles.sh {project} {option}
    project = name of project
    option = options for running. 
         'init' = specifies run initialize script first
"

# Arguments
if [[ $1 == '-h' ]] || [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
   printf "$usage"
   exit 1
fi

# project = the short name of the project we are working with (e.g. npn, pep725)
project=$1
data_dir=$2

# the option variable
init=false
if [ $3 == 'init' ]; then
    init=true
fi

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
		-o $(prop_data 'output_reasoned_dir')$file.owl \
	        -c $(prop 'reasoner_config') \
		2> $(prop_data 'output_reasoned_dir')$file.owl.err
	$(prop 'ontopilot') inference_pipeline \
		-i $(prop_data 'output_unreasoned_dir')$file.ttl \
		-o $(prop_data 'output_reasoned_dir')$file.owl \
	        -c $(prop_data 'reasoner_config') \
		2> $(prop_data 'output_reasoned_dir')$file.owl.err

	echo "    writing $(prop_data 'output_reasoned_dir')$file.owl"
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
        echo java -Xmx4048m -jar $(prop 'query_fetcher') \
	    -i $(prop_data 'output_reasoned_dir')$file.owl \
	    -o $(prop_data 'output_reasoned_csv_dir') \
	    -sparql $(prop 'sparql_query') 
        java -Xmx4048m -jar $(prop 'query_fetcher') \
	    -i $(prop_data 'output_reasoned_dir')$file.owl \
	    -o $(prop_data 'output_reasoned_csv_dir') \
	    -sparql $(prop 'sparql_query') 
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
        echo java -Xmx4048m -jar $(prop 'triplifier') \
	    -i $(prop_data 'output_csv_split')$file \
	    -o $(prop_data 'output_unreasoned_dir') \
	    -c $(prop 'triplifier_config') \
	    -w -I $(prop 'import_src')  --prefix ppo:  -F TURTLE
        java -Xmx4048m -jar $(prop 'triplifier') \
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
    echo python $(prop 'pre_processor_script') \
	 $(prop_data 'input_dir') \
	 $(prop_data 'output_csv_dir')
    python $(prop 'pre_processor_script') \
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
    echo python fileSplitter.py  $(prop_data 'output_csv_dir')$inputFilename $(prop_data 'output_csv_split_dir') $(prop 'filesize_limit')
    python fileSplitter.py  $(prop_data 'output_csv_dir')$inputFilename $(prop_data 'output_csv_split_dir') $(prop 'filesize_limit')
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
    output 		# output task
done
