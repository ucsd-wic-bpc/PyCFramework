#!/usr/bin/env python3

################################################################################
# Filename: runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     24 September 2015
#
# Contains the executable logic for PyCFramework
################################################################################
import sys
import os
import argparse
from util.pathmapper import PathMapper
from util.writer import Writer, Writers
from util.perror import PyCException
from util import fileops
from util.fileops import FileType
from util.pcargparse import PCArgParseFactory
from util import case
from util.case import CaseType
from util.case import KnownCase
from util.definitions import Definitions
from util.language import Languages
from util.parse import NumberParse
from util.variables import Variables
from util.subparsers import writers as writersSubparser
from util.subparsers import test as testSubparser

def parse_arguments(arguments, output=sys.stdout):
    argParser = PCArgParseFactory.get_argument_parser(output)
    # Create a base parser to handle all the generic flags
    baseParser = argparse.ArgumentParser(add_help=False)
    baseParser.add_argument('--writer', help='The writer to operate on')
    baseParser.add_argument('--name', help='The name of the writer being operated on')
    baseParser.add_argument('--email', help='The email of the writer being operated on')
    baseParser.add_argument('--language', nargs='+', help='The name of the language being operated on')
    baseParser.add_argument('--problems', nargs='+', help='The number of the problem to operate on')
    baseParser.add_argument('--verbose', action='store_true', help='Display verbose output')
    argParser = argparse.ArgumentParser(parents=[baseParser], add_help=False)
    argParser.add_argument('--generateHackerrankZip', help='Generate the ZIP file containing HR I/O')
    argParser.add_argument('--help', action='store_true')
    argParser.add_argument('--diff', action='store_true', help='Show the diff of incorrect solutions')
    argParser.add_argument('--file', action='store_true', help='Save outputs to file')
    subparsers = argParser.add_subparsers()
    writersSubparser.add_to_subparser_object(subparsers, baseParser)
    testSubparser.add_to_subparser_object(subparsers, baseParser)

    if len(arguments) == 0:
        argParser.print_help()
        return None
    else:
        try:
            args = argParser.parse_args(arguments)
            if args.func:
                args.func(args)
            else:
                print(":P")
        except Exception as e: 
            print(str(e))
            return None 
        if args.help:
            argParser.print_help()
            return None

        return args

def solution_passes_case(solution, case):
    solutionOutput = solution.get_output(case.inputContents)

    if not isinstance(case, KnownCase):
        return (True, solutionOutput)

    return (solutionOutput == case.outputContents, solutionOutput)


def handle_optional_args(arguments, output=sys.stdout) -> int:
    """
    Handles optional args given by arguments. 

    :returns: 0 is args processed, 1 if no args processed
    """
    # If arguments is None, only the help flag was provided
    if arguments is None:
        return 0

    elif arguments.generateHackerrankZip:
        generate_hackerrank_zip(arguments.generateHackerrankZip)
        return 0
    
    return 1

def generate_hackerrank_zip(directory):
    # The goal is to generate a ZIP file containing 
    # General zip should include sample and general
    # Corner zip should include sample and corner
    if not fileops.exists(directory, FileType.DIRECTORY):
        os.mkdir(directory)

    # Look through all cases
    for caseProblemNumber, caseObjectList in case.get_all_cases().items():
        problemDir = fileops.join_path(directory, 'Problem{}'.format(caseProblemNumber))
        caseTypes = [CaseType.SAMPLE, CaseType.CORNER_CASE, CaseType.GENERATED]
        if not fileops.exists(problemDir, FileType.DIRECTORY):
            os.mkdir(problemDir)
        for caseType in caseTypes:
            caseString = CaseType.to_string(caseType)
            caseDir = fileops.join_path(problemDir, caseString)
            inputDir = fileops.join_path(caseDir, 'input')
            outputDir = fileops.join_path(caseDir, 'output')
            if not fileops.exists(caseDir, FileType.DIRECTORY):
                os.mkdir(caseDir)
            if not fileops.exists(inputDir, FileType.DIRECTORY):
                os.mkdir(inputDir)
            if not fileops.exists(outputDir, FileType.DIRECTORY):
                os.mkdir(outputDir)

        # Move individual cases into the problem files
        for caseObject in caseObjectList:
            relevantDir = fileops.join_path(problemDir, caseObject.get_case_string())
            inputDir = fileops.join_path(relevantDir, 'input')
            outputDir = fileops.join_path(relevantDir, 'output')
            inputFile = fileops.join_path(inputDir, 'input{}.txt'.format(caseObject.caseNumber))
            outputFile = fileops.join_path(outputDir, 'output{}.txt'.format(caseObject.caseNumber))
            fileops.write_file(inputFile, caseObject.inputContents)
            if isinstance(caseObject, KnownCase):
                fileops.write_file(outputFile, caseObject.outputContents)

        for caseType in caseTypes:
            caseString = CaseType.to_string(caseType)
            fileops.zipdir(fileops.join_path(problemDir, caseString),
                    fileops.join_path(problemDir, '{}.zip'.format(caseString)))

def get_test_results(writer, problemNumber, includeDiffs=False, writeOutput=False):
    results = []

    outputList = []
    for caseProblemNumber, caseObjectList in case.get_all_cases(problemNumber=problemNumber).items():
        problemSolutions = writer.get_solutions(caseProblemNumber)
        for solution in problemSolutions:
            try:
                solution.compile()
            except ExecutionError as e:
                results.append('Solution Failed to Compile: {} {} {} {} ${}\n{}'.format(
                    solution.solutionWriter, solution.problemNumber,
                    solution.solutionLanguage.name, caseObject.get_case_string().title(),
                    caseObject.caseNumber, ''))
                continue
            for caseObject in caseObjectList:
                solutionResults = solution_passes_case(solution, caseObject)
                outputList.append(solutionResults[1])

                if not solutionResults[0]:
                    results.append( 'Incorrect Solution: {} {} {} {} #{}\n{}'.format(
                        solution.solutionWriter, solution.problemNumber,
                        solution.solutionLanguage.name, caseObject.get_case_string().title(),
                        caseObject.caseNumber, 
                        caseObject.get_output_diff(solutionResults[1]) if includeDiffs else ''))

    if writeOutput:
        write_output_list(writer, solution, caseObject, 
                outputList, includeDiffs)
    return results

def write_output_list(writer, solution, case, solutionOutputList, includeDiffs=False):
    namingScheme = Definitions.get_value('output_naming')
    formatDict = {
            Variables.get_variable_key_name(Variables.NAME_PROBLEM_NUMBER) : solution.problemNumber,
            Variables.get_variable_key_name(Variables.NAME_CASE_TYPE) : case.get_case_string(),
            Variables.get_variable_key_name(Variables.NAME_LANGUAGE) : solution.solutionLanguage.name
            }
    namingScheme = namingScheme.format(**formatDict)
    outFile = '{}.{}'.format(namingScheme, Definitions.get_value('output_file_ending'))
    if includeDiffs:
        diffFile = '{}.{}'.format(namingScheme, 'diff')
        writer.delete_file(diffFile)

    writer.delete_file(outFile)

    for output in solutionOutputList:
        if includeDiffs:
            writer.append_file(diffFile, case.get_output_diff(output))

        writer.append_file(outFile, output)

def main(arguments, out=sys.stdout):
    # Set the path
    PathMapper.set_root_path(os.path.dirname(os.path.abspath(__name__)))

    try:
        parsedArgs = parse_arguments(arguments, output=out)
        if handle_optional_args(parsedArgs, output=out) == 0:
            return 0
    except PyCException as e:
        out.write(e.message)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
