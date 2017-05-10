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

class processNPN:
    def __init__(self, inputDir, outputDir ):
        self.inputDir = inputDir
        self.outputDir = outputDir 
        self.mainIndexName = 'record_id'

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
			count = 0
			chunkSize = 100000
                        tp = pd.read_csv(dirname+'/'+filename, sep=',', header=0,iterator=True, chunksize=chunkSize,dtype=object)

			#masterDF = pd.DataFrame()
			#result = []
			writeHeader=True
			for df in tp:

			    # put them back together
			    #df = pd.concat(tp, ignore_index=True)

                            # Add an index name 
                            df.index.name = self.mainIndexName

                            # Translate values from intensity_values.csv file 
                            cols = ['value','lower_count','upper_count','lower_percent','upper_percent']
                            # translate values
                            df = self.translate(self.cur_dir +'/intensity_values.csv',cols,'value',df,'Intensity_Value')
    

			    # attempting to convert intensity value to simple integer to make df.loc calls later
			    # more memory efficent
			    # first fill nan values to 'unsure' in case this is blank
			    #df['Phenophase_Status'].fillna(-1,inplace=True)
			    #df['Phenophase_Status'] = (df['Phenophase_Status']).astype(int)
			    #df['intensity_boolean'] = 1
                            #df.loc[(df.Intensity_Value == '-9999') ,'intensity_boolean'] = 0
			    #df['intensity_boolean'] = (df['intensity_boolean']).astype(int)

                            # set upper/lower counts for cases of no intensity value
                            df.loc[(df.Intensity_Value == '-9999') & (df.Phenophase_Status == '0'),'upper_count'] = 0
                            #df.loc[(df.intensity_boolean == 0) & (df.Phenophase_Status == 0),'upper_count'] = 0
                            df.loc[(df.Intensity_Value == '-9999') & (df.Phenophase_Status == '1'),'lower_count'] = 1
                            #df.loc[(df.intensity_boolean == 0) & (df.Phenophase_Status == 1),'lower_count'] = 1
			
                            df['Source'] = 'NPN'
    
    		            # Normalize Date to just Year. we don't need to store actual date because we use only Year + DayOfYear
    		            df['Year'] = pd.DatetimeIndex(df['Observation_Date']).year
    
    		            # Create ScientificName
    		            df['ScientificName'] = df['Genus'] + ' ' + df['Species']
			    count = count + chunkSize
			    print "    processed " + str(chunkSize) + " of " + str(count) + " and appending to outputfile"

			    #result.append(df)
			    #masterDF.append(df)
    
  			    # print "    combining dataframes into one"
			    #masterDF = pd.concat(result,ignore_index=True)
                            # create output filename by removing first part of filename (datasheet_)
                            output_filename = outputfilename.split("_")[1] 
                            output_filename_fullpath = self.outputDir + output_filename + '.csv'
    
                            # write to CSV output directory
                            #print "    writing " + output_filename_fullpath
                            df.to_csv(output_filename_fullpath,sep=',', mode='a', header=writeHeader)
			    writeHeader=False

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
