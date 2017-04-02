#!/bin/python
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

inputDir = os.curdir + '../data/npn/input'
outputDir = '../data/npn/output_csv' 
mainIndexName = 'record_id'


# python program to read NPN files, stored in directories 
# The NPN files have been downloaded from the NPN database
# and are stored in the NPN format using comma separated values

# 1. Read the status_intensity_observation_data CSV file in each directory
#Observation_ID
#Update_Datetime
#Site_ID
#Latitude
#Longitude
#Elevation_in_Meters
#State
#Species_ID
#Genus
#Species
#Common_Name
#Kingdom
#Individual_ID
#Phenophase_ID
#Phenophase_Description
#Observation_Date
#Day_of_Year
#Intensity_Category_ID
#Intensity_Value
#Abundance_Value
#Lower_Count
#Upper_Count
#Removing the following since i will only be taking status = 1
#Phenophase_Status

# apply an lower count value where there is no intensity value and phenophase_status is 1
def status1NoIntensity(row):
    if (row['Phenophase_Status'] == 1 and row['Intensity_Value'] == '-9999'):
        return 1
    else:
        # return default value
        return row['lower_count']

# apply an upper count value where there is no intensity value and phenophase_status is 0
def status0NoIntensity(row):
    if (row['Phenophase_Status'] == 0 and row['Intensity_Value'] == '-9999'):
        return 0
    else:
        # return default value
        return row['upper_count']

#2. Write Output to the output directory

# initialize directory path
if (os.path.exists(outputDir)):
    shutil.rmtree(outputDir)
os.makedirs(outputDir)

framesDict = {}
# Loop each directory off of input directory
for dirname in os.listdir(inputDir):
    # make sure we're just dealing with PEP directories
    if (dirname.startswith('datasheet_') and dirname.endswith("zip") == False):
        print "processing " + dirname
        # loop all filenames in directory
        onlyfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
        for filename in onlyfiles:
            # phenology data frame
            if (filename == 'status_intensity_observation_data.csv'):
                # Read the incoming data
                df = pd.read_csv(dirname+'/'+filename, sep=',', header=0)
                # Add an index name 
                df.index.name = mainIndexName
                # Filter the data frame for phenophase_status == 1 (only looking at things that are present)
                #df = df.loc[df['Phenophase_Status'] == 1]
                # Drop the phenophase_status column
                #df = df.drop('Phenophase_Status',1)
                # Intensity Value Mappings
                # This section maps all Intensity_Value values to lower/upper counts and lower/upper percentages
                df['lower_count'] = ''
                df['upper_count'] = ''
                df['lower_percent'] = ''
                df['upper_percent'] = ''
                # map lower counts
                equiv = {'1,001 to 10,000':1001, '101 to 1,000':101, '11 to 100':11, '3 to 10':3, 'Less than 3':0, 'Little':1, 'Lots':1, 'More than 10':11, 'More than 10,000':10001, 'Some':1, '25-49%':'', '5-24%':'', '50-74%':'', '75-94%':'', '95% or more':'', 'Less than 25%':'', 'Less than 5%':''}
                df['lower_count'] = df['Intensity_Value'].map(equiv)
                # map upper counts
                equiv = {'1,001 to 10,000':10000, '101 to 1,000':1000, '11 to 100':100, '3 to 10':10, 'Less than 3':2, 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':'', '5-24%':'', '50-74%':'', '75-94%':'', '95% or more':'', 'Less than 25%':'', 'Less than 5%':''}
                df['upper_count'] = df['Intensity_Value'].map(equiv)
                # map lower percents
                equiv = {'1,001 to 10,000':'', '101 to 1,000':'', '11 to 100':'', '3 to 10':'', 'Less than 3':'', 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':25, '5-24%':5, '50-74%':50, '75-94%':75, '95% or more':95, 'Less than 25%':0, 'Less than 5%':0}
                df['lower_percent'] = df['Intensity_Value'].map(equiv)
                # map upper percents
                equiv = {'1,001 to 10,000':'', '101 to 1,000':'', '11 to 100':'', '3 to 10':'', 'Less than 3':'', 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':49, '5-24%':24, '50-74%':74, '75-94%':94, '95% or more':100, 'Less than 25%':24, 'Less than 5%':4}
                df['upper_percent'] = df['Intensity_Value'].map(equiv)

                # In cases where the Intensity_Value = -9999 and Phenophase_Status = 0 the 'upper count' should be 0
                df['upper_count'] = df.apply(status0NoIntensity,axis=1)
                # In cases where the Intensity_Value = -9999 and Phenophase_Status = 1 the 'lower count' should be 1
                df['lower_count'] = df.apply(status1NoIntensity,axis=1)

                # create output filename
                output_filename = outputDir + '/' + dirname.split("_")[1] + '.csv'
                # write to CSV
                df.to_csv(output_filename,sep=',', mode='a', header=True)
