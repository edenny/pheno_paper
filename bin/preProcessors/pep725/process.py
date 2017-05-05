#!/bin/python
import argparse
import inspect
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re
import csv

mainIndexName = 'record_id'

# python program to read PEP files, stored in directories 
# The PEP files have been downloaded from the PEP725 database
# and are stored in the PEP format, normalized using the "Character-Separated-Value"
# format using semicolons as the separator.

# 1. Read the 3 data files in the directories and create a single record storing the following
# LocationID (PEP_ID) (from *_stations.csv)
# Phenology_description (BBCH) (description field from PEP725_BBCH.csv)
# Year (YEAR) (from PEP725_AT_{name})
# DayOfYear (DAY) (from PEP725_AT_{name})
# Latitude (LAT) (from *_stations.csv)
# Longitude (LON) (from *_stations.csv)
# ElevationInMeters (ALT) (from *_stations.csv)
# LocationName (NAME) (from *_stations.csv)
# Country Name (two digit code parsed from directory or filenames and matched to the following list)
#
# NOTE: the PEP725 data does not come with its own observation identifier as in NPN
# and thus, we create one using the record_id (or main index) for the master dataframe.
# this means, that PEP725 data loads should be processed as a group and NEVER separated

# Argument parser
parser = argparse.ArgumentParser(description='NPN Parser')
parser.add_argument('input_dir',  help='the input directory')
parser.add_argument('output_dir', help='the output directory to store CSV results')

# argparser parser automatically checks for correct input from the command line
args = parser.parse_args()
inputDir = args.input_dir
outputDir = args.output_dir
#input_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/input/'
#output_csv_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/output_csv/'
cur_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))+'/'

# open countries dict file as dictionary
with open(cur_dir+'countries.csv') as f:
        countries  = dict(filter(None, csv.reader(f)))

# open specificEpithets.dict file as dictionary
# this will be used for creating a specificEpithet field 
# using the filename
with open(cur_dir+'specificEpithets.csv') as f:
        specificEpithets = dict(filter(None, csv.reader(f)))

# Genus (taken from the filename of PEP725_AT_{name} (what appears before (...))
#    NOTE: gens names will all be one of the following:
#        "Betula"
#        "Helianthus"
# ScientificName (taken from the filename of PEP725_AT_{name})
#    NOTE: scientific names will all be one of the following:
#        "Betula pendula (B. verrucasa| B. alba)
#        "Betula pubescens"
#        "Helianthus annuus"


#2. Write Output to the output directory
# Two files: 
# A. one for all Betula 
# B. one for all Healianthus 

# initialize directory path
if (os.path.exists(outputDir)):
    shutil.rmtree(outputDir)
os.makedirs(outputDir)

framesDict = {}
allDataFrame = pd.DataFrame() 
# Loop each directory off of the current directory
for dirname in os.listdir(inputDir):
    # make sure we're just dealing with PEP directories
    if (dirname.startswith('PEP') and dirname.endswith("tar") == False):
        # obtain country code from directory name pattern
        countrycode = dirname.split("_")[1]
        # obtain country name from countrycode
        countryname = countries.get(countrycode)

        dirname = inputDir + '/' + dirname
        print "    processing " + dirname
        # loop all filenames in directory
        onlyfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
        #list_ = []
        scientificname = ''
        genus = ''
        for filename in onlyfiles:
            # phenology data frame
            if (filename == 'PEP725_BBCH.csv'):
                phenologyDataFrame = pd.read_csv(dirname+'/'+filename, sep=';', header=0)
                # rename bbch to BBCH so it doesn't duplicate later
                phenologyDataFrame = phenologyDataFrame.rename(columns={'bbch':'BBCH'})

                # strip whitespace from characters in description field
                phenologyDataFrame['description'] = phenologyDataFrame['description'].map(str.strip)
            # location data frame
            elif (filename == 'PEP725_'+countrycode+'_stations.csv'):
                locationDataFrame = pd.read_csv(dirname+'/'+filename, sep=';', header=0)
                #list_.append(locationDataFrame)
            # occurrence data frame
            elif (filename != 'PEP725_README.txt'):
                occurrenceDataFrame = pd.read_csv(dirname+'/'+filename, sep=';', header=0)
                #list_.append(occurrenceDataFrame)

                # extract the scientificname from the filename
                scientificname = filename[10:len(filename)-4].replace("_"," ")

                # map the scientificname to specificEpithet using our dict
                specificEpithet = specificEpithets.get(scientificname)

                # extract genus from scientificname
                genus = scientificname.split(" ")[0]
                genus = genus.split("(")[0]

        # merge frames
        merged_inner1 = pd.merge(left=occurrenceDataFrame,right=locationDataFrame, left_on='PEP_ID', right_on='PEP_ID')
        merged_all = pd.merge(left=merged_inner1,right=phenologyDataFrame, left_on='BBCH', right_on='BBCH')

        # adding the index name, a unique index for each record
        merged_all.index.name = mainIndexName
        # the scientificname is same for everything in this particular file
        merged_all['scientificname'] = scientificname
        merged_all['genus'] = genus
        merged_all['specificEpithet'] = specificEpithet
        merged_all['countryname'] = countryname
        merged_all['Source'] = 'PEP725' 
	#merged_all['Observation_ID'] = merged_all['genus'] + merged_all.index
    	#####################################
	# Deal with lower/upper count fields
    	#####################################
	# Everything in PEP is "present" so it should all be lower_count = 1
        merged_all['lower_count'] = 1
	# Conditionally map count fields.  Some fields are actually "absent".. here we re-map these to upper_count = 0
	#merged_all.loc[merged_all['description'] in  'Sowing', 'upper_count'] = 0
	#merged_all.loc[merged_all['description'] in 'Sowing', 'lower_count'] = 0
	#merged_all.description['Sowing]' loc[merged_all['description'] in 'Sowing', 'lower_count'] = 0
        merged_all['upper_count'] = ''
	merged_all.loc[merged_all.description == 'Sowing', ['lower_count', 'upper_count']] = 0, 0

        # merged_all['phenophase_status'] = 'urn:occurring'

        # add to dictionary of lists
#        if genus not in framesDict:
#            framesDict[genus] = list()
#        framesDict[genus].append(merged_all)

	allDataFrame = allDataFrame.append(merged_all)

outputFilename = outputDir + 'PEP725_ALL.csv'
print '    writing ' + outputFilename
allDataFrame.to_csv(outputFilename ,sep=',', mode='a', header=True)

# Finish up by looping each genus
#for genusName,genusDataFrames in framesDict.iteritems():
#    allDataFrame=pd.concat(genusDataFrames)
#    allDataFrame.reset_index(drop=True,inplace=True)
#    allDataFrame.index.name = mainIndexName
#    outputFilename = outputDir + genusName + '.csv'
#
#    # only print header if there is no file right now
#    if (not os.path.exists(outputFilename)):
#        printHeader = True
#    else:
#        printHeader = False
#
#    print '    writing ' + outputFilename
#    # output single filename
##    allDataFrame.to_csv(outputFilename ,sep=',', mode='a', header=printHeader)
