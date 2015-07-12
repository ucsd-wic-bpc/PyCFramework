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
import subprocess

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

class RunResults:
    def __init__(self, runs):
        self.runs = runs

    def add_run(self, run):
        self.runs.append(run)


class Run:
    def __init__(self, userOutput, correctOutput, inputFile):
        self.userOutput = userOutput
        self.correctOutput = correctOutput
        self.inputFile = inputFile

def get_source_extension(languageBlock):
    if 'compileExtension' in languageBlock:
        return languageBlock['compileExtension']
    else:
        return languageBlock['runExtension']

def replace_language_vars_individual(string, problemFile, directory):
    variables = languages['variables']
    filenameWithoutExtension = os.path.splitext(problemFile)[0]
    return (string.replace(variables['filename'], problemFile)
            .replace(variables['filename_less_extension'], filenameWithoutExtension)
            .replace(variables['directory'], directory))

def replace_language_vars(languageBlock, problemFile, directory):
    for key, languageItem in languageBlock.items():
        if isinstance(languageItem, list):
            for i in range(0, len(languageItem)):
                languageItem[i] = replace_language_vars_individual(languageItem[i], problemFile, directory)
        else:
            languageBlock[key] = replace_language_vars_individual(languageItem, problemFile, directory)
    return languageBlock
                

def compile_solution(convertedLanguageBlock):
    # Check if the solution needs compiling and compile if it does
    if 'compileExtension' in convertedLanguageBlock:
        compileCommand = []
        compileCommand.append(convertedLanguageBlock['compileCommand'])
        compileCommand.extend(convertedLanguageBlock['compileArguments'])
        if not subprocess.call(compileCommand) == 0:
            return False
    return True

def run_solution(convertedLanguageBlock, outputDirectory, inputFiles):
    runCommand = []
    runCommand.append(convertedLanguageBlock['runCommand'])
    runCommand.extend(convertedLanguageBlock['runArguments'])
    results = RunResults([])
    for inputFile in inputFiles:
        inputObject = open(inputFile, 'r')
        outputFile = inputFile.replace('.' + definitions['input_file_ending'],
                '.' + definitions['output_file_ending'])
        try:
            output = subprocess.check_output(runCommand, stdin=inputObject).decode("utf-8")
            inputObject.close()
            with open(outputFile) as outputObject:
                outputFileContents = outputObject.read()
            results.add_run(Run(output, outputFileContents, inputFile))
                
        except subprocess.CalledProcessError:
            inputObject.close()
            results.add_run(Run(output, outputFileContents, inputFile))

    return results
    

    
def test_solution(problem, user, skipSample, skipCorner):
    # First check to make sure that the user exists
    userPath = os.path.dirname(os.path.abspath(__file__)) + "/" + user
    writersPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['writers_directory']
    testPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['test_directory']
    problemString = definitions['solution_naming'].replace('{problem}', problem)

    if not os.path.isdir(userPath) or not os.path.islink(writersPath + "/" + user):
        print("{} is not a valid user".format(user))
        return False

    inputFileList = []
    sampleFile = (testPath + "/" + problemString + definitions['sample_case_extension']
                + '.' + definitions['input_file_ending'])
    cornerFile = (testPath + "/" + problemString + definitions['corner_case_extension']
                + '.' + definitions['input_file_ending'])

    if not skipSample and os.path.isfile(sampleFile):
        inputFileList.append(sampleFile)
    if not skipCorner and os.path.isfile(cornerFile):
        inputFileList.append(cornerFile)


    # Now check to make sure that the user has source code for the problem
    numSolutions = 0
    for possibleSolution in os.listdir(userPath):
        for languageBlock in languages['languages']:
            if possibleSolution == (definitions['solution_naming']
                                    .replace('{problem}', problem) + "." + 
                                    get_source_extension(languageBlock)):
                convertedLanguageBlock = replace_language_vars(languageBlock, possibleSolution, userPath)
                numSolutions += 1
                if compile_solution(convertedLanguageBlock):
                    results = run_solution(convertedLanguageBlock, userPath + "/output",
                                inputFileList)
                    for run in results.runs:
                        itemType = "SAMPLE" if run.inputFile == sampleFile else "CORNER"
                        if not run.userOutput == run.correctOutput:
                            print(("FAILED {}: {}'s problem {} solution in {}"
                                .format(itemType, user, problem, convertedLanguageBlock['language'])))
                        else:
                            print(("PASSED {}: {}'s problem {} solution in {}"
                                .format(itemType, user, problem, convertedLanguageBlock['language'])))



        
test_solution(args.problem[0], args.name[0], args.skipsample, args.skipcorner)
