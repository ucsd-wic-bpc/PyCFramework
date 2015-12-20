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

def parse_arguments(arguments, output=sys.stdout):
    argParser = PCArgParseFactory.get_argument_parser(output)
    # Create a base parser to handle all the generic flags
    baseParser = argparse.ArgumentParser(add_help=False)
    baseParser.add_argument('--writer', help='The writer to operate on')
    baseParser.add_argument('--name', help='The name of the writer being operated on')
    baseParser.add_argument('--email', help='The email of the writer being operated on')
    baseParser.add_argument('--language', nargs='*', help='The name of the language being operated on')
    argParser = argparse.ArgumentParser(parents=[baseParser], add_help=False)
    argParser.add_argument('--createWriter', help='Create a new writer with specified info')
    argParser.add_argument('--deleteWriter', help='Remove the specified writer')
    argParser.add_argument('--addLanguage', nargs='+', help='Add a language to the specified writer')
    argParser.add_argument('--assignProblems', action='store_true', help='Assign problems to writers')
    argParser.add_argument('--generateHackerrankZip', help='Generate the ZIP file containing HR I/O')
    argParser.add_argument('--help', action='store_true')
    argParser.add_argument('--diff', action='store_true', help='Show the diff of incorrect solutions')
    argParser.add_argument('--file', action='store_true', help='Save outputs to file')
    argParser.add_argument('--importWriters', help='Import writers from a CSV file in the format of "folder;name;email;lang1,lang2,lang3')
    #argParser.add_argument('--writer', help='The writer to operate on')
    #argParser.add_argument('writerFolder', help='The folder for the writer to operate on',
            #nargs='*')
    argParser.add_argument('--problems', help='The number of the problem to operate on')
    subparsers = argParser.add_subparsers()
    writersSubparser.add_to_subparser_object(subparsers, baseParser)


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

def get_indiv_writer_details(writerFolder):
    writerObject = Writer.load_from_folder(writerFolder)
    if writerObject is None:
        raise PyCException('Error: {} is an invalid Writer'.format(writerFolder))
    else:
        return str(writerObject)

def get_writer_details(writerFolders):
    writerDetails = []
    for writer in writerFolders:
        writerDetails.append(get_indiv_writer_details(writer))

    return '\n'.join(writerDetails)
    
def create_writer(writerFolder, writerName, writerEmail):
    if writerEmail is None:
        raise PyCException('Error: No email specified')

    if writerName is None:
        raise PyCException('Error: No name specified')

    newWriter = Writer(writerPath=writerFolder, writerName=writerName, 
            writerEmail=writerEmail)
    try:
        newWriter.create()
    except Exception as e:
        raise PyCException('Error: Could not create writer')

def delete_writer(writerFolder):
    writerToDelete = Writer.load_from_folder(writerFolder)
    if writerToDelete is None:
        raise PyCException('Error: {} is an invalid writer'.format(writerFolder))
    else:
        writerToDelete.delete()

def solution_passes_case(solution, case):
    solutionOutput = solution.get_output(case.inputContents)

    if not isinstance(case, KnownCase):
        return (True, solutionOutput)

    return (solutionOutput == case.outputContents, solutionOutput)

def add_language_to_writer(writerFolders, languageNames):
    if languageNames is None or len(languageNames) == 0:
        raise PyCException('Error: Must specify a language')

    for writerFolder in writerFolders:
        writer = Writer.load_from_folder(writerFolder)
        if writer is None:
            raise PyCException('Error: {} is an invalid writer'.format(writerFolder))

        for languageName in languageNames:
            writer.add_known_language(languageName)

def assign_problems():
    writerList = Writers.get_all_writers()
    for writer in writerList:
        writer.unassign_all_problems()

    for problemNumber in range(1, Definitions.get_value('problem_count')+1):
        for language in Languages.get_all_language_names():
            assignedCount = 0
            for i in range(0, Definitions.get_value('complete_threshold')):
                if assignedCount >= Definitions.get_value('complete_threshold'):
                    break
            
                writer = get_best_candidate(writerList, language)
                if not writer is None:
                    writer.add_assigned_problem(problemNumber, language)
                    assignedCount += 1

def get_best_candidate(writerList, languageName):
    # First, sort the writer list by assigned problem count
    writerList = sorted(writerList, key=lambda x: x.get_number_assigned_problems())
    for writer in writerList:
        if writer.knows_language(languageName):
            return writer

def get_todo_list(writerFolder):
    writer = Writer.load_from_folder(writerFolder)
    if writer is None:
        raise PyCException('Error: {} is an invalid writer'.format(writerFolder))

    return ['{} in {}\n'.format(problem[0], problem[1]) for problem in writer.get_assigned_problems_not_started()]

def handle_optional_args(arguments, output=sys.stdout) -> int:
    """
    Handles optional args given by arguments. 

    :returns: 0 is args processed, 1 if no args processed
    """
    # If arguments is None, only the help flag was provided
    if arguments is None:
        return 0

    if arguments.listWriter:
        details = get_writer_details(arguments.listWriter)
        for detail in details:
            output.write(detail)
        return 0

    elif arguments.createWriter:
        create_writer(arguments.createWriter, arguments.name, arguments.email)
        return 0

    elif arguments.deleteWriter:
        delete_writer(arguments.deleteWriter)
        return 0

    elif arguments.addLanguage:
        add_language_to_writer(arguments.addLanguage, arguments.language)
        return 0

    elif arguments.assignProblems:
        assign_problems()
        return 0

    elif arguments.todo:
        todoList = get_todo_list(arguments.todo)
        for todo in todoList:
            output.write(todo)
        return 0

    elif arguments.importWriters:
        writerDataList = fileops.parse_csv(arguments.importWriters)
        for dataChunk in writerDataList:
            w = Writer(writerPath = dataChunk[0], writerName = dataChunk[1],
                    writerEmail = dataChunk[2])
            w.create()
            w.add_known_language_from_list(dataChunk[3])
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

def get_problem_list(problemString):
    if problemString is None:
        return [None]

    return NumberParse().str_to_list_range( problemString, 
            int(Definitions.get_value('problem_count')), 1)

def handle_positional_args(arguments, output=sys.stdout):
    # Check if user did something wrong
    if arguments is None:
        PCArgParseFactory.get_argument_parser(output).print_help()
        return

    if arguments.writerFolder is None or len(arguments.writerFolder) == 0:
        arguments.writerFolder = Writers.get_all_writer_names()

    # Now we need to load the writers that the user specified
    for writerFolder in arguments.writerFolder:
        writer = Writer.load_from_folder(writerFolder)
        if writer is None:
            raise PyCException('Error: {} is an invalid writer'.format(writerFolder))

        # If no problem was specified, test all solutions
        problems = get_problem_list(arguments.problems)
        for problem in get_problem_list(arguments.problems):
            testResults = get_test_results(writer, problem, arguments.diff,
                    arguments.file)
            for result in testResults:
                output.write(result)
    
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

    try:
        handle_positional_args(parsedArgs, output=out)
    except PyCException as e:
        out.write(e.message)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
