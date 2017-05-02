#!/bin/python
# this script reads NPN files that have been downloaded and stored in input
# directories and performs necessary pre-processing steps before triplification
# can occur.
import csv
import inspect
import argparse
import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re
import zipfile

# The process for looping the NEON data.
# The NEON data process here assumes we start with a Zip file archive.
# which we first extract in the input directory.  When this archive is 
# extracted it creates a new directory called NEON_obs-phenology-plant
# which itself contains a number of zip files
# NOTE: this may be a brittle structure!
class processNEON:
    def __init__(self, inputDir, outputDir ):
        self.inputDir = inputDir
        self.outputDir = outputDir 
        self.mainIndexName = 'uid'

        self.cur_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))+'/'
        # initialize directory path
        if (os.path.exists(self.outputDir)):
            shutil.rmtree(self.outputDir)
        os.makedirs(self.outputDir)

    # Function to read in a CSV file containing one or more values that we want
    # to use to translate values  for.  using the dataframe's "lookupColumn"
    # as the key
    def translate(self,filename,cols,index_name,dataFrame,lookupColumn):
        # loop all columns
        for column in cols:
            # don't look at index column
            if (column != index_name):
                # read the incoming lookup filename into a dictionary using the 
                # the appropriate columns to assign the dictionary key/value
                with open(filename) as f:
                    thisDict = dict((rows[cols.index(index_name)],rows[cols.index(column)]) \
                            for rows in csv.reader(f))
                    # assign the new column name values based on lookup column name
                    dataFrame[column] = dataFrame[lookupColumn].map(thisDict)
        return dataFrame

    def process(self):
        # The NEON data is extracted to a directory called NEON_obs-phenology-plant
        modifiedInputDir = self.inputDir +  '/NEON_obs-phenology-plant'
        displayHeader = True
        # loop all of the files in the input directory
        for zipFilename in os.listdir(modifiedInputDir):
            # make sure we're just dealing with the proper directories 
            if (zipFilename.endswith(".zip") ):
                # construct the full path to the input zip file
                zipFilefullPath = modifiedInputDir + '/' + zipFilename
                # create a zfile object
                zfile = zipfile.ZipFile(zipFilefullPath)
                # loop all of the files in the input zip file
                for filename in zfile.namelist():
                    # search for the observation data in input
                    if (filename.endswith("phe_statusintensity.csv")):  
                        # succesfully reading this data frame
                        #df = pd.read_csv(zfile.open(filename))

                        # Read the incoming data
		        # Chunking files into bits of 100000 gets around memory issues
                        tp = pd.read_csv(zfile.open(filename), sep=',', header=0,iterator=True, chunksize=100000,dtype=object)
		        # put them back together
		        df = pd.concat(tp, ignore_index=True)

                        # Add an index name 
                        df.index.name = self.mainIndexName

                        # Translate values from intensity_values.csv file 
                        cols = ['value','lower_count','upper_count','lower_percent','upper_percent']
                        # translate values
                        df = self.translate(self.cur_dir +'/intensity_values.csv',cols,'value',df,'phenophaseIntensity')
    
                        # In cases where the phenophaseIntensity = '' 
                        # and Phenophase_Status = 0 the 'upper count' should be 0
                        df.loc[pd.isnull(df['phenophaseIntensity']) & (df.phenophaseStatus == 'no'),'upper_count'] = 0
#                       # In cases where the phenophaseIntensity = ''
                        # and Phenophase_Status = 1 the 'lower count' should be 1
                        df.loc[pd.isnull(df['phenophaseIntensity']) & (df.phenophaseStatus == 'yes'),'lower_count'] = 1
                        df['Source'] = 'NEON'
#    
#    		        # Normalize Date to just Year.
    		        df['Year'] = pd.DatetimeIndex(df['date']).year
    		        df['DayOfYear'] = pd.DatetimeIndex(df['date']).dayofyear
#    
#    		        # Create Genus specificEpithet subSpecificEpithet from scientificname
                        names = df['scientificName'].str.split(' ')
                        df['genus'] = names.str[0]
                        df['specificEpithet'] = names.str[1]
    
#                        # create output filename by removing first part of filename (datasheet_)
                       #output_filename = outputfilename.split("_")[1] 
                        # to one file (probably easier this way)
                        output_filename_fullpath = self.outputDir + 'all_neon.csv'


                        # TODO: grab lat/lng by joining on the *phe_perindividual.csv
                        # file, using the individualID column


                        # write to CSV output directory
                        # TODO: fix this so it actually appends all CSV data to one file
                        print "    writing " + output_filename_fullpath
                        df.to_csv(output_filename_fullpath,sep=',', mode='a', header=displayHeader)
                        displayHeader = False

# Argument parser
parser = argparse.ArgumentParser(description='NEON Parser')
parser.add_argument('input_dir',  help='the input directory')
parser.add_argument('output_dir', help='the output directory to store CSV results')

# argparser parser automatically checks for correct input from the command line
args = parser.parse_args()
#input_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/input/'
#output_csv_dir = '/Users/jdeck/IdeaProjects/pheno_paper/data/npn/output_csv/'

p = processNEON(args.input_dir,args.output_dir)
p.process()
