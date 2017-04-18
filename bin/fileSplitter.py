#!/bin/python
# this script reads NPN files that have been downloaded and stored in input
# directories and performs necessary pre-processing steps before triplification
# can occur.
import argparse
import os
from os import listdir
from os.path import isfile, join
import sys
import shutil
import re

# Argument parser
parser = argparse.ArgumentParser(description='File Splitter')
parser.add_argument('input_filename',  help='the input filename to split')
parser.add_argument('output_directory', help='the output directory to store the results')

# argparser parser automatically checks for correct input from the command line
args = parser.parse_args()

# the split function
def split(
        filehandler, 
        delimiter, 
        row_limit,
        output_name_template, 
        output_path, 
        keep_headers
        ):
    """
    Splits a CSV file into multiple pieces.
    
    A quick bastardization of the Python CSV library.

    Arguments:

        `row_limit`: The number of rows you want in each output file. 10,000 by default.
        `output_name_template`: A %s-style template for the numbered output files.
        `output_path`: Where to stick the output files.
        `keep_headers`: Whether or not to print the headers in each output file.

    Example usage:
    
        >> from toolbox import csv_splitter;
        >> csv_splitter.split(open('/home/ben/input.csv', 'r'));
    
    """
    import csv
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
         output_path,
         output_name_template  % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    print '    writing ' + current_out_path
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
               output_path,
               output_name_template  % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
            print '    writing ' + current_out_path
        current_out_writer.writerow(row)


# split file into components
print "########################"
print "# Split Files " 
print "########################"

# filename without path
filename=os.path.basename(args.input_filename)
# extension
extension=filename.rsplit('.',1)[1]
# filename without extension
filename=filename.rsplit('.',1)[0]

# rn the split command
split(
    open(args.input_filename, 'r'),
    ',',
    50000,
    filename+'_%s.csv',
    args.output_directory,
    True);
