#!/bin/python
# A simple set-comparison script to test input and output from triplification process

import argparse
import os
import tempfile

# a function to loop and print a set
def loopSet(mySet):
    # convert set to list
    myList = list(mySet)
    for item in myList:
        print "    "+item


# Argument parser
parser = argparse.ArgumentParser(description='Test unreasoned triple output')
parser.add_argument('actual_filename', type=argparse.FileType('r'), help='the file containing the actual results')
parser.add_argument('expected_filename', type=argparse.FileType('r'), help='thie file containing expected results')
#parser.add_argument('actual_filename', help='the file containing the actual results')
#parser.add_argument('expected_filename', help='thie file containing expected results')

# argparser parser automatically checks for correct input from the command line
args = parser.parse_args()

# compare actual and expected filenames
actual=set(line.strip() for line in args.actual_filename.readlines())
expected=set(line.strip() for line in args.expected_filename.readlines())

# compute set differences
notInActual = actual-expected
notInExpected = expected-actual

# print output
print "********************************************************************"
print "* Test frame-work for test data that has been triplified"
print "* These tests operate on files that have been pre-processed and "
print "* then converted into triples, effectively testing the output of the"
print "* triplifier."
print "********************************************************************"

print ""
allPassed=True

if (bool(notInActual)):
    print "* Lines appearing in '" +args.actual_filename.name +"' but not in '"+args.expected_filename.name +"'"
    print "* These are unexpected triples being written."
    loopSet(notInActual)
    allPassed=False
    print ""


if (bool(notInExpected)):
    print "* Lines appearing in '" +args.expected_filename.name +"' but not in '"+args.actual_filename.name +"'"
    print "* These are triples that should have been written, but were not."
    allPassed=False
    loopSet(notInExpected)

if (allPassed):
    print ""
    print "All tests passed!"
    print ""
else:
    print ""
    print "Some tests failed"
    print ""
