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
from util.writer import Writer, Writers
from util.perror import PyCException
from util import fileops
from util.pcargparse import PCArgParseFactory
from util import case
from util.case import KnownCase
from util.definitions import Definitions
from util.language import Languages

def parse_arguments(arguments, output=sys.stdout):
    argParser = PCArgParseFactory.get_argument_parser(output)
    argParser.add_argument('--name', help='The name of the writer being operated on')
    argParser.add_argument('--email', help='The email of the writer being operated on')
    argParser.add_argument('--language', help='The name of the language being operated on')
    argParser.add_argument('--createWriter', help='Create a new writer with specified info')
    argParser.add_argument('--listWriter',help='List the problems that a writer has completed')
    argParser.add_argument('--deleteWriter', help='Remove the specified writer')
    argParser.add_argument('--addLanguage', help='Add a language to the specified writer')
    argParser.add_argument('--assignProblems', action='store_true', help='Assign problems to writers')
    argParser.add_argument('--todo', help='List the problems that a given writer has yet to do')
    argParser.add_argument('--help', action='store_true')
    argParser.add_argument('--diff', action='store_true', help='Show the diff of incorrect solutions')
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
        except Exception: return None 
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
        raise PyCException('Error: {} is an invalid writer'.format(writerFolder))
    else:
        writerToDelete.delete()

def solution_passes_case(solution, case):
    solutionOutput = solution.get_output(case.inputContents)

    if not isinstance(case, KnownCase):
        return (True, solutionOutput)

    return (solutionOutput == case.outputContents, solutionOutput)

def add_language_to_writer(writerFolder, languageName):
    if languageName is None:
        raise PyCException('Error: Must specify a language')

    writer = Writer.load_from_folder(writerFolder)
    if writer is None:
        raise PyCException('Error: {} is an invalid writer'.format(writerFolder))

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
    
    return 1

def get_test_results(writer, problemNumber, includeDiffs=False):
    results = []

    for caseProblemNumber, caseObjectList in case.get_all_cases(problemNumber=problemNumber).items():
        problemSolutions = writer.get_solutions(caseProblemNumber)
        for solution in problemSolutions:
            for caseObject in caseObjectList:
                solutionResults = solution_passes_case(solution, caseObject)
                if not solutionResults[0]:
                    results.append( 'Incorrect Solution: {} {} {} {} #{}\n{}'.format(
                        solution.solutionWriter, solution.problemNumber,
                        solution.solutionLanguage.name, caseObject.get_case_string(), 
                        caseObject.caseNumber, 
                        caseObject.get_output_diff(solutionResults[1]) if includeDiffs else ''))

    return results

def handle_positional_args(arguments, output=sys.stdout):
    # Check if user did something wrong
    if arguments is None or arguments.writerFolder is None:
        PCArgParseFactory.get_argument_parser(output).print_help()
        return

    # Now we need to load the writer that the user specified
    writer = Writer.load_from_folder(arguments.writerFolder)
    if writer is None:
        raise PyCException('Error: {} is an invalid writer'.format(arguments.writerFolder))

    # If no problem was specified, test all solutions
    testResults = get_test_results(writer, arguments.problemNumber, arguments.diff)
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
