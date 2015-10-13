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
from util.pathmapper import PathMapper
from util.writer import Writer
from util.perror import PyCException
from util import fileops
from util.pcargparse import PCArgParseFactory
from util import case
from util.case import KnownCase

def parse_arguments(arguments, output=sys.stdout):
    argParser = PCArgParseFactory.get_argument_parser(output)
    argParser.add_argument('--name', help='The name of the writer being operated on')
    argParser.add_argument('--email', help='The email of the writer being operated on')
    argParser.add_argument('--createWriter', help='Create a new writer with specified info')
    argParser.add_argument('--listWriter', help='List the problems that a writer has completed')
    argParser.add_argument('--deleteWriter', help='Remove the specified writer')
    argParser.add_argument('--help', action='store_true')
    argParser.add_argument('writerFolder', help='The folder for the writer to operate on',
            nargs='?')
    argParser.add_argument('problemNumber', help='The number of the problem to operate on',
            nargs='?')

    if len(arguments) == 0:
        argParser.print_help()
        return None
    else:
        try:
            args = argParser.parse_args(arguments)
        except Exception:
            return None

        if args.help:
            argParser.print_help()
            return None

        return args

def get_writer_details(writerFolder):
    writerObject = Writer.load_from_folder(writerFolder)
    if writerObject is None:
        raise PyCException('Error: {} is an invalid Writer'.format(writerFolder))
    else:
        return str(writerObject)

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
        raise PyCException('Error: {} is an invalid writer', format(writerFolder))
    else:
        writerToDelete.delete()

def solution_passes_case(solution, case):
    if not isinstance(case, KnownCase):
        return True

    solutionOutput = solution.get_output(case.inputContents)
    return solutionOutput == case.outputContents

def handle_optional_args(arguments, output=sys.stdout):
    # If arguments is None, only the help flag was provided
    if arguments is None:
        return

    if arguments.listWriter:
        details = get_writer_details(arguments.listWriter)
        for detail in details:
            output.write(detail)

    elif arguments.createWriter:
        create_writer(arguments.createWriter, arguments.name, arguments.email)

    elif arguments.deleteWriter:
        delete_writer(arguments.deleteWriter)

def get_test_results(writer, problemNumber):
    results = []

    for caseProblemNumber, caseObjectList in case.get_all_cases(problemNumber=problemNumber).items():
        problemSolutions = writer.get_solutions(caseProblemNumber)
        for solution in problemSolutions:
            for caseObject in caseObjectList:
                if not solution_passes_case(solution, caseObject):
                    results.append( 'Incorrect Solution: {} {} {} Case #{} {}\n'.format(
                        solution.solutionWriter, solution.problemNumber,
                        caseObject.get_case_string(), caseObject.caseNumber, solution.solutionLanguage.name))

    return results

def handle_positional_args(arguments, output=sys.stdout):
    # Check if user did something wrong
    if arguments is None or arguments.writerFolder is None:
        PCArgParseFactory.get_argument_parser(output).print_help()
        return

    # Now we need to load the writer that the user specified
    writer = Writer.load_from_folder(arguments.writerFolder)
    if writer is None:
        raise PyCException('Error: {} is an invalid writer', format(arguments.writerFolder))

    # If no problem was specified, test all solutions
    testResults = get_test_results(writer, arguments.problemNumber)
    for result in testResults:
        output.write(result)

    
def main(arguments, out=sys.stdout):
    # Set the path
    PathMapper.set_root_path(os.path.dirname(os.path.abspath(__name__)))

    try:
        parsedArgs = parse_arguments(arguments, output=out)
        handle_optional_args(parsedArgs, output=out)
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
