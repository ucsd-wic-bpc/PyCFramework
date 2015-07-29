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
#   <user> is one or more name
#   <problem> is a single problem number, or a range. Range patterns are:
#       3      - A single number
#       +3     - All problems greater than 3
#       -3     - All problems less than 3
#       1-3    - All problems within the inclusive range 1-3
################################################################################
import argparse
import os
import json
import sys
import subprocess
import shutil
from tests.unit import conf_languages
from tests.unit import conf_definitions

"""
This script tests a user's problem against sample input and corner-case input
as well as generates output for generated cases.
"""

DEFINITIONS_FILE = os.path.dirname(os.path.abspath(__file__)) + "/conf/definitions.json"
LANGUAGES_FILE = os.path.dirname(os.path.abspath(__file__)) + "/conf/languages.json"
VARIABLES_FILE = os.path.dirname(os.path.abspath(__file__)) + "/conf/variables.json"

# Declare the script arguments
parser = argparse.ArgumentParser(description=("Tests users' solutions"
                                            "against various inputs"))
parser.add_argument('problem',  nargs=1, 
                    help="The problem of the user's solution that is tested")
parser.add_argument('name',  nargs='+', 
                    help="The people whose solutions will be tested")
parser.add_argument('--skipsample', action='store_true',
                    help="Do not test the user's solution against sample input")
parser.add_argument('--skipcorner', action='store_true',
                    help=("Do not test the user's solution against"
                        " corner case input"))
parser.add_argument('--skipvalidation', action='store_true',
                    help=("Do not validate the properties files before loading"
                        " them"))

# Handle the script arguments
args = parser.parse_args()

# Load the definitions from the definitions file
if not os.path.isfile(DEFINITIONS_FILE):
    print("Error: Definitions file {} cannot be found.".format(DEFINITIONS_FILE))
    sys.exit(1)
if not os.path.isfile(LANGUAGES_FILE):
    print("Error: Langauges file {} cannot be found.".format(LANGUAGES_FILE))
    sys.exit(1)
if not os.path.isfile(VARIABLES_FILE):
    print("Error: Variables file {} cannot be found".format(VARIABLES_FILE))
    sys.exit(1)

# Run validation tests
if not args.skipvalidation and not conf_languages.run_tests():
    print(("Validation tests for the languages configuration file failed."
        " This means that there was an error within your conf/languages.json"
        " file. Cannot continue"))
    sys.exit(1)
if not args.skipvalidation and not conf_definitions.run_tests():
    print(("Validation tests for the definitions configuration file failed."
        " This means that there was an error within your conf/definitions.json"
        " file. Cannot continue"))
    sys.exit(1)
if not args.skipvalidation and not conf_variables.run_tests():
    print(("Validation tests for the variables configuration file failed."
        " This means that there was an error within your conf/variables.json"
        " file. Cannot continue"))
    sys.exit(1)


# At this point, the configurations pass validation tests. Load them in
with open(DEFINITIONS_FILE) as f:
    definitionContents = f.read()
with open(LANGUAGES_FILE) as f:
    languageContents = f.read()
with open(VARIABLES_FILE) as f:
    variableContents = f.read()

definitions = json.loads(definitionContents)
languages = json.loads(languageContents)
variables = json.loads(variableContents)

# The RunResults Class keeps track of a group of "runs", which are essentially
# tests run on a specific problem and specific cases.
class RunResults:
    def __init__(self, runs):
        self.runs = runs

    def add_run(self, run):
        self.runs.append(run)

# The run class keeps track of the test that was run, the correct output,
# and what the user output
class Run:
    def __init__(self, userOutput, correctOutput, inputFile):
        self.userOutput = userOutput
        self.correctOutput = correctOutput
        self.inputFile = inputFile

# Function returns the extension of the source code file
def get_source_extension(languageBlock):
    if 'compileExtension' in languageBlock:
        return languageBlock['compileExtension']
    else:
        return languageBlock['runExtension']

# Replaces the variables of a specific language block.
def replace_language_vars_individual(string, problemFile, directory):
    filenameWithoutExtension = os.path.splitext(problemFile)[0]
    return (string.replace(variables['filename'], problemFile)
            .replace(variables['filename_less_extension'], filenameWithoutExtension)
            .replace(variables['directory'], directory))

# Replaces the variables of all language blocks by finding the language blocks
# and delegating functionality to the above replace_language_vars_individual
def replace_language_vars(languageBlock, problemFile, directory):
    for key, languageItem in languageBlock.items():
        if isinstance(languageItem, list):
            for i in range(0, len(languageItem)):
                languageItem[i] = replace_language_vars_individual(languageItem[i], problemFile, directory)
        else:
            languageBlock[key] = replace_language_vars_individual(languageItem, problemFile, directory)
    return languageBlock
                

# Compile a solution given its language block with correct paths
def compile_solution(convertedLanguageBlock):
    # Check if the solution needs compiling and compile if it does
    if 'compileExtension' in convertedLanguageBlock:
        compileCommand = []
        compileCommand.append(convertedLanguageBlock['compileCommand'])
        compileCommand.extend(convertedLanguageBlock['compileArguments'])
        if not subprocess.call(compileCommand) == 0:
            return False
    return True

# Run a rolution and return its RunResults.
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
            if not os.path.isfile(outputFile):
                outputFileContents = output
            else:
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
    userOutputDirectory = userPath + "/" + definitions['output_directory']
    writersPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['writers_directory']
    testPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['test_directory']
    problemString = definitions['solution_naming'].replace('{problem}', str(problem))

    if not os.path.isdir(userPath) or not os.path.islink(writersPath + "/" + user):
        print("{} is not a valid user".format(user))
        return False

    # Check to make sure the user output directory exists
    if not os.path.isdir(userOutputDirectory):
        os.makedirs(userOutputDirectory)

    # Get all valid input test files
    inputFileList = []
    sampleFile = (testPath + "/" + problemString + definitions['sample_case_extension']
                + '.' + definitions['input_file_ending'])
    cornerFile = (testPath + "/" + problemString + definitions['corner_case_extension']
                + '.' + definitions['input_file_ending'])
    generatedFile = (testPath + "/" + problemString + definitions['generated_case_extension']
                + '.' + definitions['input_file_ending'])

    if not skipSample and os.path.isfile(sampleFile):
        inputFileList.append(sampleFile)
    if not skipCorner and os.path.isfile(cornerFile):
        inputFileList.append(cornerFile)
    if os.path.isfile(generatedFile):
        inputFileList.append(generatedFile)

    # Now check to make sure that the user has source code for the problem
    numSolutions = 0
    numCorrectSolutions = 0
    for possibleSolution in os.listdir(userPath):
        for languageBlock in languages['languages']:
            if possibleSolution == (definitions['solution_naming']
                                    .replace(variables['problem_number'], str(problem)) + "." + 
                                    get_source_extension(languageBlock)):
                convertedLanguageBlock = replace_language_vars(languageBlock, possibleSolution, userPath)
                numSolutions += 1
                if compile_solution(convertedLanguageBlock):
                    results = run_solution(convertedLanguageBlock, userPath + "/output",
                                inputFileList)
                    numCorrectRuns = 0
                    for run in results.runs:
                        itemType = "SAMPLE" if run.inputFile == sampleFile else "CORNER"
                        if not run.userOutput == run.correctOutput:
                            print(("FAILED {}: {}'s problem {} solution in {}"
                                .format(itemType, user, problem, convertedLanguageBlock['language'])))
                        else: 
                            numCorrectRuns += 1
                            saveOutputFile = (userPath + "/" + definitions['output_directory'] + "/" + 
                                    os.path.basename(run.inputFile).replace(definitions['input_file_ending'],
                                    definitions['output_file_ending']))
                            with open(saveOutputFile, 'w+') as saveObject:
                                saveObject.write(run.userOutput)

                    if numCorrectRuns == len(results.runs):
                        numCorrectSolutions += 1


                            
    if numSolutions == 0:
        print("{} Does not have problem {}!".format(user, problem))
        return False
    elif numCorrectSolutions == numSolutions:
        return True
    else:
        return False

def compare_generated_outputs(problem, users):
    lastUser = (None, None)
    for user in users:
        userPath = os.path.dirname(os.path.abspath(__file__)) + "/" + user
        problemString = definitions['solution_naming'].replace(variables['problem_number'], str(problem))
        generatedPath = (userPath + "/" + problemString + definitions['generated_case_extension']
                    + '.' + definitions['output_file_ending'])
        if not os.path.isfile(generatedPath):
            output = ""
        else:
            with open(generatedPath) as generatedObject:
                output = generatedObject.read()
        if lastUser[0] == None:
            lastUser = (user, output)
        else:
            if not output == lastUser[1]:
                print("FAILED GENERATED: {}'s problem {} doesn't match {}'s"
                        .format(lastUser[0], problem, user))
                return False
            else:
                lastUser = (user, output)
    return True

def copy_to_final_io(problem, user):
    # Needs to copy sample input, sample output, corner input, corner output, 
    # generated input, and user's generated output.
    testPath = os.path.dirname(os.path.abspath(__file__)) + "/" + definitions['test_directory']
    problemString = definitions['solution_naming'].replace(variables['problem_number'], str(problem))
    userPath = os.path.dirname(os.path.abspath(__file__)) + "/" + user
    finalDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/" + definitions['finalio_directory']
    sampleInputFile = (testPath + "/" + problemString + definitions['sample_case_extension']
            + '.' + definitions['input_file_ending'])
    sampleOutputFile = (testPath + "/" + problemString + definitions['sample_case_extension']
            + '.' + definitions['output_file_ending'])
    cornerInputFile = (testPath + "/" + problemString + definitions['corner_case_extension']
            + '.' + definitions['input_file_ending'])
    cornerOutputFile = (testPath + "/" + problemString + definitions['corner_case_extension']
            + '.' + definitions['output_file_ending'])
    generatedInputFile = (testPath + "/" + problemString + definitions['generated_case_extension']
            + '.' + definitions['input_file_ending'])
    generatedOutputFile = (userPath + "/" + definitions['output_directory'] + "/" +  problemString 
            + definitions['generated_case_extension'] + '.' + definitions['output_file_ending'])

    # Make sure all copy items exist first
    copyList = [sampleInputFile, sampleOutputFile, cornerInputFile, cornerOutputFile,
            generatedInputFile, generatedOutputFile]

    for fileToCopy in copyList:
        print(fileToCopy)
        if not os.path.isfile(fileToCopy):
            print("Ah")
            return False

    # Make sure the FinalIO directory exists. If not, create it:
    if not os.path.isdir(finalDirectory):
        os.makedirs(finalDirectory)

    # Now copy all files
    for fileToCopy in copyList:
        shutil.copy(fileToCopy, finalDirectory)

    return True


# Now parse the arguments to check for specific options
problemCount = definitions['problem_count']
problemsToDo = []
if args.problem[0][0] == '+' or args.problem[0][0] == '-':
        if args.problem[0][0] == '+':
            for i in range(int(args.problem[0][1:]) + 1, problemCount + 1):
                problemsToDo.append(i)
        else:
            for i in range(1, int(args.problem[0][1:])):
                problemsToDo.append(i)
elif '-' in args.problem[0]:
    dashIndex = args.problem[0].index('-')
    for i in range(int(args.problem[0][0:dashIndex]), int(args.problem[0][dashIndex + 1:]) + 1):
        problemsToDo.append(i)
else:
    problemsToDo.append(int(args.problem[0]))


for problem in problemsToDo:
    passingPeople = 0
    for people in args.name:
        if test_solution(problem, people, args.skipsample, args.skipcorner): 
            passingPeople += 1

    if passingPeople == len(args.name):
        # All people passed. This means that their generated solutions can be compared
        if compare_generated_outputs(problem, args.name):
            if not copy_to_final_io(problem, args.name[0]):
                print("Error copying files to the FinalIO directory")
