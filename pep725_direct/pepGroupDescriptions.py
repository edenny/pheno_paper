#!/bin/python
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

outputDir = 'output_csv' 
outputFileName = "description.csv"

# examine PEP files and create a template description.csv file
# Loop each directory off of the current directory
files_ = []
for filename in os.listdir(outputDir):
    #field,defined_by
    if (outputFileName not in filename):
        print "reading " + filename
        files_.append(pd.read_csv(outputDir+'/'+filename, sep=',', header=0))
    
# concatenate all files
allDataFrame = pd.concat(files_)
# create a group by
countsDataFrame  = pd.DataFrame(allDataFrame.groupby('description', as_index=False).size())

# write fileoutput
filenameToWriteTo = outputDir + "/" + outputFileName
print "writing " + filenameToWriteTo
try:
        os.remove(filenameToWriteTo)
except OSError:
        pass
countsDataFrame.to_csv(filenameToWriteTo, sep=',', mode='a')
