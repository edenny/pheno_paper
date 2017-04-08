#!/bin/python
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

inputDir = os.curdir + '/../data/pep725/input'
outputDir = '../data/pep725/output_csv' 
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
countries = { 
    'AT':'Austria',
    'BA':'Bosnia and Herzegovina',
    'CH':'Switzerland',
    'CZ':'Czech Republic',
    'DE':'Germany',   
    'FI':'Finland',   
    'HR':'Croatia',   
    'IE':'Ireland',   
    'IP':'IPG',   
    'LT':'Lithuania',
    'LV':'Latvia',
    'ME':'Montenegrin Republic',
    'NL':'Netherlands',   
    'NO':'Norway',    
    'PL':'Poland',
    'SE':'Sweden',
    'SI':'Slovenia',
    'SK':'Slovakia',
    'UK':'United Kingdom'
}
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
# Loop each directory off of the current directory
for dirname in os.listdir(inputDir):
    # make sure we're just dealing with PEP directories
    if (dirname.startswith('PEP') and dirname.endswith("tar") == False):
        # obtain country code from directory name pattern
        countrycode = dirname.split("_")[1]
        # obtain country name from countrycode
        countryname = countries.get(countrycode)

        dirname = inputDir + '/' + dirname
        print "processing " + dirname
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
                #list_.append(phenologyDataFrame)
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
        merged_all['countryname'] = countryname
        merged_all['lower_count'] = 1
        # merged_all['phenophase_status'] = 'urn:occurring'

        # add to dictionary of lists
        if genus not in framesDict:
            framesDict[genus] = list()
        framesDict[genus].append(merged_all)

# Finish up by looping each genus
for genusName,genusDataFrames in framesDict.iteritems():
    allDataFrame=pd.concat(genusDataFrames)
    allDataFrame.reset_index(drop=True,inplace=True)
    allDataFrame.index.name = mainIndexName
    outputFilename = outputDir + '/' + genusName + '.csv'

    # only print header if there is no file right now
    if (not os.path.exists(outputFilename)):
        printHeader = True
    else:
        printHeader = False

    print 'writing output to ' + outputFilename
    # name output files according to genus
    allDataFrame.to_csv(outputFilename ,sep=',', mode='a', header=printHeader)

