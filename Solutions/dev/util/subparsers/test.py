################################################################################
# Filename: util/subparsers/test.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     20 December 2015
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py test
################################################################################
from util.writer import Writer, Writers
from util import case as CaseManager
from util.language import ExecutionError
from util.case import KnownCase
import difflib

SUBPARSER_KEYWORD = "test"
SHOW_PASSING_KEYWORD = "showpass"

headerPrinted = False

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This is
    set as the executable function when the `test` subparser is used

    Arguments:
    args: Namespace - The arguments pased via CLI
    """
    writerList = args.writers
    test(writerList, args.language, args.problems, args.verbose, args.showpass,
            args.diff)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the test subparser to a given subparsers object and delegates test
    functionality to the operate() function

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to add
                      the test subparser to
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags
    """
    testParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    testParser.add_argument('writers', nargs='*')
    testParser.add_argument('--showpass', action='store_true')
    testParser.add_argument('--diff', action='store_true')
    testParser.set_defaults(func=operate)

def _get_loaded_writers(writerNames: list = None) -> list:
    """
    Loads the writers with the provided names and returns them in a list. 

    Arguments:
    writerNames: list - The list of names to load writers for. If None, all
                        writers are loaded.
    """
    if writerNames is None or len(writerNames) == 0:
        return Writers.get_all_writers()

    loadedWriters = []
    for writerName in writerNames:
        loadedWriter = Writer.load_from_folder(writerName)
        if loadedWriter is None:
            raise PyCException('Error: {} is an invalid writer'.format(writerName))
        else:
            loadedWriters.append(loadedWriter)

    return loadedWriters

def _get_problem_numbers_from_string(problemString: str) -> list:
    """
    Turns a problem string into a list of numbers

    Arguments:
    problemString: str - The string to convert into a list of numbers
    """
    # Check to see if is range
    if '-' in problemString:
        splitProblemString = problemString.split('-')
        return list(range(int(splitProblemString[0]), int(splitProblemString[1])+1))
    else:
        return [int(problemString)]

def _get_unique_problem_numbers_from_list(problemStringList: list) -> list:
    """
    Turns a list of problem strings into a list of unique numbers

    Arguments:
    problemStringList: list - The list of strings to convert
    """
    uniqueProblemSet = set()
    for problemString in problemStringList:
        parsedProblemList = _get_problem_numbers_from_string(problemString)
        uniqueProblemSet = uniqueProblemSet.union(set(parsedProblemList))

    return list(uniqueProblemSet)

def _get_filtered_solutions(writerNames: list, languageNames: list, 
        problemStrings: list) -> list:
    """
    Gets a list of solutions based on the provided filters. If all filters
    are None, a full list of solutions is returned.

    Arguments:
    writerNames: list    - The list of writer names to get solutions for
    languageNames: list  - The list of languages that solutions may be written in
    problemStrings: list - The list of problems solutions may be written for
    """
    # First, get all the loaded writers
    writerList = _get_loaded_writers(writerNames)

    solutionsToTest = []
    # Now get their solutions based on problem filter
    if problemStrings is None:
        for writer in writerList:
            solutionsToTest.extend(writer.get_all_solutions())
    else:
        for problemNumber in _get_unique_problem_numbers_from_list(problemStrings):
            for writer in writerList:
                solutionsToTest.extend(writer.get_solutions(problemNumber))

    # Now filter solutions based on language filter
    if not languageNames is None:
        solutionsToTest[:] = [solution for solution in solutionsToTest if 
                            solution.solutionLanguage.name in languageNames]

    return solutionsToTest

def _test_solution_against_cases(solution, cases:list, outputToStderr: bool,
        printPassingCases: bool, printDiff: bool):
    """
    Tests a single solution against a list of cases and outputs results
    to stdout. 

    Arguments:
    solution    - The solution to test
    cases: list - The list of cases to test the solution against
    """
    # First, print the header
    # Writer    Problem   Language  CaseType    Case#   Status  Message
    formattingStr = "{0: <10}\t{1: <10}\t{2: <10}\t{3: <10}\t{4: <10}\t{5: <10}\t{6}"

    # Compile first
    try:
        solution.compile(verbose=outputToStderr)
    except ExecutionError as e:
        _print_header_if_not_printed()
        print(formattingStr.format(solution.solutionWriter, 
            solution.problemNumber, solution.solutionLanguage.name, "COMPILE",
            "COMPILE", 'FAIL', 'Compile Error'))
        return

    for case in cases:
        if (outputToStderr):
            print("Testing problem {} case {}".format(solution.problemNumber,
                case.caseNumber))

        solutionOutput = ""
        try:
            solutionOutput = solution.get_output(case.inputContents,
                    outputToStderr=outputToStderr)

        except ExecutionError as e:
            _print_header_if_not_printed()
            print(formattingStr.format(solution.solutionWriter,
                solution.problemNumber, solution.solutionLanguage.name, 
                case.get_case_string(), case.caseNumber, 'FAIL',
                e.message))
            continue

        if not isinstance(case, KnownCase):
            continue

        resultsStr = "PASS" if solutionOutput == case.outputContents else "FAIL"
        commentStr = "Correct Solution" if resultsStr == "PASS" else "Incorrect Solution"
        if resultsStr == "PASS" and not printPassingCases:
            if outputToStderr:
                print(">Passed")
            continue

        if outputToStderr:
            print("User Output: {}".format(solutionOutput))
            print("Correct Output: {}".format(case.outputContents))

        _print_header_if_not_printed()
        print(formattingStr.format(solution.solutionWriter,
            solution.problemNumber, solution.solutionLanguage.name,
            case.get_case_string(), case.caseNumber, resultsStr, commentStr))
        
        if printDiff:
            userLines = solutionOutput.splitlines()
            solutionLines = case.outputContents.splitlines()
            for line in difflib.unified_diff(userLines, solutionLines, 
                    lineterm="", fromfile="User Solution", tofile="Correct Solution"):
                print(line)


def test(writerNames: list, languageNames: list, problemStrings: list, 
        outputToStderr: bool, printPassingCases: bool, printDiff: bool):
    """
    Tests solutions based on the arguments provided and outputs results to
    stdout. If all arguments are none, all solutions are tested

    Arguments:
    writerNames: list    - The list of writer names to test solutions for
    languageNames: list  - The list of language names to test solutions for
    problemStrings: list - The list of problem strings to test solutions for
    """
    solutionsToTest = _get_filtered_solutions(writerNames, languageNames, 
            problemStrings)

    # load all the cases
    cases = CaseManager.get_all_cases()


    # Now test all of the solutions
    for solution in solutionsToTest:
        _test_solution_against_cases(solution, cases[int(solution.problemNumber)],
                outputToStderr, printPassingCases, printDiff)

def _print_header_if_not_printed():
    global headerPrinted
    if not headerPrinted:
        formattingStr = "{0: <10}\t{1: <10}\t{2: <10}\t{3: <10}\t{4: <10}\t{5: <10}\t{6}"
        print(formattingStr.format("Writer", "Problem", "Language", "CaseType", "Case", "Status", "Message"))
        headerPrinted = True

