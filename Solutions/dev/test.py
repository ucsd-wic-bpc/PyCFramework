################################################################################
# Filename: test.py
# Author:   Brandon Milton
#           http://brandonio21.com
# Date:     July 2, 2015
# 
# This file serves as a replacement for test.sh. It compiles and runs all 
# user inputted solutions against test cases.
#
# Usage:
#   $ python test.py <problem> <user>
#   
################################################################################
import argparse
import os
import json
import sys

"""
This script tests a user's problem against sample input and corner-case input
as well as generates output for generated cases.
"""

DEFINITIONS_FILE = os.path.dirname(os.path.abspath(__file__)) + "/conf/definitions.json"
LANGUAGES_FILE = os.path.dirname(os.path.abspath(__file__)) + "/conf/languages.json"

# Declare the script arguments
parser = argparse.ArgumentParser(description=("Tests users' solutions"
                                            "against various inputs"))
parser.add_argument('problem', metavar='P', nargs=1, 
                    help="The problem of the user's solution that is tested")
parser.add_argument('name', metavar='N', nargs='+', 
                    help="The people whose solutions will be tested")
parser.add_argument('--skipsample', action='store_true',
                    help="Do not test the user's solution against sample input")
parser.add_argument('--skipcorner', action='store_true',
                    help=("Do not test the user's solution against"
                        "corner-case input"))
parser.add_argument('--skipvalidation', action='store_true',
                    help=("Do not validate the properties files before loading"
                        "them"))

# Handle the script arguments
args = parser.parse_args()

# Load the definitions from the definitions file
if not os.path.isfile(DEFINITIONS_FILE):
    print("Error: Definitions file {} cannot be found.".format(DEFINITIONS_FILE))
    sys.exit(1)
if not os.path.isfile(LANGUAGES_FILE):
    print("Error: Langauges file {} cannot be found.".format(LANGUAGES_FILE))
    sys.exit(1)

with open(DEFINITIONS_FILE) as f:
    definitionContents = f.read()
with open(LANGUAGES_FILE) as f:
    languageContents = f.read()

definitions = json.loads(definitionContents)
languages = json.loads(languageContents)

def get_source_extension(languageBlock):
    if 'compileExtension' in languageBlock:
        return languageBlock['compileExtension']
    else:
        return languageBlock['runExtension']

def test_solution(problem, user, skipSample, skipCorner):
    # First check to make sure that the user exists
    userPath = os.path.dirname(os.path.abspath(__file__)) + "/" + user
    writersPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['writers_directory']

    if not os.path.isdir(userPath) or not os.path.islink(writersPath + "/" + user):
        print("{} is not a valid user".format(user))
        return False

    # Now check to make sure that the user has source code for the problem
    for possibleSolution in os.listdir(userPath):
        for languageBlock in languages['languages']:
            if possibleSolution == (definitions['solution_naming']
                                    .replace('{problem}', problem) + "." + 
                                    get_source_extension(languageBlock)):
                print(possibleSolution)

        
test_solution(args.problem[0], args.name[0], args.skipsample, args.skipcorner)
