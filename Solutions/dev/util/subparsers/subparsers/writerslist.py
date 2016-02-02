################################################################################
# Filename: util/subparsers/subparsers/writerslist.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     29 Jan 2016
# 
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers list
################################################################################
from util.parse import NumberParse
from util.writer import Writers
SUBPARSER_KEYWORD = 'list'


def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `writers list` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Parse the problem numbers from the commandline
    problemParser = NumberParse()
    if not args.problems is None:
        problemRange = []
        for problemSet in args.problems:
            problemRange.extend(problemParser.str_to_list_range(problemSet))

        specifiedProblems = list(set(problemRange))
    else:
        specifiedProblems = None


    list_writers(args.writer_directories, specifiedProblems, args.email,
                 args.language, args.writer, args.name)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the list subparser to a given subparsers object and delegates listing
    functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to 
                      add the list subparser to.
    parentParser:   - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    listParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                            parents=[parentParser])
    listParser.add_argument('writer_directories', nargs='*')
    listParser.set_defaults(func=operate)

def list_writers(writerDirectories: list, problems: list, emails: list, 
        languages: list, writerFirstNames: list, writerNames: list):
    """
    Prints the list of writers and their details to the console. Details are
    retrieved using Writer.__str__()

    Arguments:
    writerDirectories: list - A list of directories to print details for
    problems: list          - Only print writers who have completed this problem
    emails: list            - Only print writers with these emails
    languages: list         - Only print writers who know these languages
    writerFirstNames: list  - Only print writers who have one of these firstname
    writerNames: list       - Only print writers who have one of these fullnames
    """
    # First, we assemble the filter dictionary according to the spec in 
    # util/writer.py
    filterDict = {
                    Writers.FILTER_KEY_DIRS:               writerDirectories,
                    Writers.FILTER_KEY_COMPLETED_PROBLEMS: problems,
                    Writers.FILTER_KEY_EMAILS:             emails,
                    Writers.FILTER_KEY_KNOWS_LANGS:        languages,
                    Writers.FILTER_KEY_FIRST_NAMES:        writerFirstNames,
                    Writers.FILTER_KEY_FULL_NAMES:         writerNames
                 }

    print('\n'.join([str(writer) for writer in 
                     Writers.get_writers_from_filter(filterDict)]))
