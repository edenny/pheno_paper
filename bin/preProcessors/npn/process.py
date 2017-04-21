#!/bin/python
# this script reads NPN files that have been downloaded and stored in input
# directories and performs necessary pre-processing steps before triplification
# can occur.
import argparse
import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

# some global variables to set before beginning
#inputDir = os.curdir + '/../data/npn/input'
#outputDir = '../data/npn/output_csv' 
#outputSplitDir = '../data/npn/output_csv_split' 
#mainIndexName = 'record_id'

class processNPN:
    def __init__(self, inputDir, outputDir ):
        self.inputDir = inputDir
        self.outputDir = outputDir 
        self.mainIndexName = 'record_id'

        # initialize directory path
        if (os.path.exists(self.outputDir)):
            shutil.rmtree(self.outputDir)
        os.makedirs(self.outputDir)

    # apply an lower count value where there is no intensity value and phenophase_status is 1
    def status1NoIntensity(self,row):
        if (row['Phenophase_Status'] == 1 and row['Intensity_Value'] == '-9999'):
            return 1
        else:
            # return default value
            return row['lower_count']
    
    # apply an upper count value where there is no intensity value and phenophase_status is 0
    def status0NoIntensity(self,row):
        if (row['Phenophase_Status'] == 0 and row['Intensity_Value'] == '-9999'):
            return 0
        else:
            # return default value
            return row['upper_count']
    
    def process(self):
        framesDict = {}
        # Loop each directory off of input directory
        for dirname in os.listdir(self.inputDir):
            # make sure we're just dealing with the proper directories 
            if (dirname.startswith('datasheet_') and dirname.endswith("zip") == False ):
                outputfilename = dirname
                dirname = self.inputDir + '/' + dirname
                # loop all filenames in directory
                onlyfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
                for filename in onlyfiles:
                    # phenology data frame
                    if (filename == 'status_intensity_observation_data.csv'):
                        # Read the incoming data
			# Chunking files into bits of 100000 gets around memory issues
                        tp = pd.read_csv(dirname+'/'+filename, sep=',', header=0,iterator=True, chunksize=100000)
			# put them back together
			df = pd.concat(tp, ignore_index=True)

                        # Add an index name 
                        df.index.name = self.mainIndexName
                        # This section maps all Intensity_Value values to lower/upper counts and lower/upper percentages
                        df['lower_count'] = ''
                        df['upper_count'] = ''
                        df['lower_percent'] = ''
                        df['upper_percent'] = '' 
                        # map lower counts
                        equiv = {'1,001 to 10,000':1001, '101 to 1,000':101, '11 to 100':11, '3 to 10':3, 'Less than 3':0, 'Little':1, 'Lots':1, 'More than 10':11, 'More than 10,000':10001, 'Some':1, '25-49%':'', '5-24%':'', '50-74%':'', '75-94%':'', '95% or more':'', 'Less than 25%':'', 'Less than 5%':'','-9999':''}
                        df['lower_count'] = df['Intensity_Value'].map(equiv)
                        # map upper counts
                        equiv = {'1,001 to 10,000':10000, '101 to 1,000':1000, '11 to 100':100, '3 to 10':10, 'Less than 3':2, 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':'', '5-24%':'', '50-74%':'', '75-94%':'', '95% or more':'', 'Less than 25%':'', 'Less than 5%':'','-9999':''}
                        df['upper_count'] = df['Intensity_Value'].map(equiv)
                        # map lower percents
                        equiv = {'1,001 to 10,000':'', '101 to 1,000':'', '11 to 100':'', '3 to 10':'', 'Less than 3':'', 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':.25, '5-24%':.05, '50-74%':.50, '75-94%':.75, '95% or more':.95, 'Less than 25%':.0, 'Less than 5%':.0,'-9999':''}
                        df['lower_percent'] = df['Intensity_Value'].map(equiv)
                        # map upper percents
                        equiv = {'1,001 to 10,000':'', '101 to 1,000':'', '11 to 100':'', '3 to 10':'', 'Less than 3':'', 'Little':'', 'Lots':'', 'More than 10':'', 'More than 10,000':'', 'Some':'', '25-49%':.49, '5-24%':.24, '50-74%':.74, '75-94%':.94, '95% or more':1.00, 'Less than 25%':.249, 'Less than 5%':.049,'-9999':''}
                        df['upper_percent'] = df['Intensity_Value'].map(equiv)
    
                        # In cases where the Intensity_Value = -9999 and Phenophase_Status = 0 the 'upper count' should be 0
                        df['upper_count'] = df.apply(self.status0NoIntensity,axis=1)
                        # In cases where the Intensity_Value = -9999 and Phenophase_Status = 1 the 'lower count' should be 1
                        df['lower_count'] = df.apply(self.status1NoIntensity,axis=1)
                        df['Source'] = 'NPN'
    
    		        # Normalize Date to just Year. we don't need to store actual date because we use only Year + DayOfYear
    		        df['Year'] = pd.DatetimeIndex(df['Observation_Date']).year
    
    		        # Create ScientificName
    		        df['ScientificName'] = df['Genus'] + ' ' + df['Species']
    
                        # create output filename by removing first part of filename (datasheet_)
                        output_filename = outputfilename.split("_")[1] 
                        output_filename_fullpath = self.outputDir + output_filename + '.csv'
    
                        # write to CSV output directory
                        print "    writing " + output_filename_fullpath
                        df.to_csv(output_filename_fullpath,sep=',', mode='a', header=True)

# Argument parser
parser = argparse.ArgumentParser(description='NPN Parser')
parser.add_argument('input_dir',  help='the input directory')
parser.add_argument('output_dir', help='the output directory to store CSV results')

# argparser parser automatically checks for correct input from the command line
args = parser.parse_args()
#input_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/input/'
#output_csv_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/output_csv/'

p = processNPN(args.input_dir,args.output_dir)
p.process()
