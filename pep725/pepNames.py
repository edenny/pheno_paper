#!/bin/python
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

outputDir = '../data/pep725/output_csv' 
#outputFileName = "description.csv"

# examine PEP files and create a template description.csv file
# Loop each directory off of the current directory
print "#=============================================================="
print "# Reading input source files"
print "#=============================================================="
files_ = []
for filename in os.listdir(outputDir):
    #field,defined_by
    #if (outputFileName not in filename):
    print "    " + filename
    files_.append(pd.read_csv(outputDir+'/'+filename, sep=',', header=0))
    
# concatenate all files
allDataFrame = pd.concat(files_)
# create a group by
countsDataFrame  = pd.DataFrame(allDataFrame.groupby('scientificname', as_index=False).size())

print "#=============================================================="
print "# Output all unique scientific names (with counts) that were"
print "# found while reading all source files"
print "#=============================================================="
print countsDataFrame

