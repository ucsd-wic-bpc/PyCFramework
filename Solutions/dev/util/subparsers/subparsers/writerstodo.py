################################################################################
# Filename: util/subparsers/subparsers/writerstodo.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     01 Feb 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers todo
################################################################################
from util.parse import NumberParse
from util.writer import Writers
SUBPARSER_KEYWORD = 'todo'

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This is
    set as the executable function when `writers todo` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Parse the problem numbers from commandline
    problemParser = NumberParse()
    if not args.problems is None:
        specifiedProblems = problemParser.str_list_to_uniq_range(args.problems)
    else:
        specifiedProblems = None

    todo_writers(args.writer_directories, specifiedProblems, args.email,
            args.language, args.writer, args.name)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the todo subparser to a given subparsers object and delegates todo
    functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to add
                      the todo subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    todoParser = subparserObject.add_parser(SUBPARSER_KEYWORD,
                                            parents=[parentParser])
    todoParser.add_argument('writer_directories', nargs='*')
    todoParser.set_defaults(func=operate)

def todo_writers(writerDirectories: list, problems: list, emails: list,
        languages: list, writerFirstNames: list, writerNames: list):
    """
    Prints the list of what solutions a writer has yet to complete to the 
    console. 

    Arguments:
    writerDirectories: list - A list of directories to print details for
    problems: list          - Only print writers who have todo this problem
    emails: list            - Only print writers with these emails
    languages: list         - Only print writers who have to complete a problem
                              in these languages
    writerFirstNames: list  - Only print writers who have one of these firstname
    writerNames: list       - Only print writers who have one of these fullnames
    """
    # First, we assemble the filter dictionary according to the spec found in
    # util/writer.py
    filterDict = {
                    Writers.FILTER_KEY_DIRS:               writerDirectories,
                    Writers.FILTER_KEY_TODO_PROBLEMS:      problems,
                    Writers.FILTER_KEY_EMAILS:             emails,
                    Writers.FILTER_KEY_TODO_LANGS:        languages,
                    Writers.FILTER_KEY_FIRST_NAMES:        writerFirstNames,
                    Writers.FILTER_KEY_FULL_NAMES:         writerNames
                 }

    print('\n'.join([_get_todo_str_for_writer(writer) for writer in
                     Writers.get_writers_from_filter(filterDict)]))

def _get_todo_str_for_writer(writer):
    """
    Gets a todo string for the given writer, where each problem is delineated
    with a newline

    Arguments:
    writer: Writer - The writer whose todo list should be returned

    Return:
    A string containing the writer's name and the problems they have yet to 
    complete.
    """
    return '{}:\n{}'.format(writer.name, '\n'.join(['{} in {}'.format(
                            problem[0], problem[1]) for problem in
                            writer.get_assigned_problems_not_started()]))
