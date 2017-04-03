################################################################################
# Filename: util/subparses/writers.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     16 December 2015
#
# Contains logic for the subparser that is invoked when calling 
#  $ ./runner.py writers
################################################################################
from util.subparsers.subparsers import writerslist as writersListSubparser
from util.subparsers.subparsers import writerstodo as writersTodoSubparser
from util.subparsers.subparsers import writersadd as writersAddSubparser
from util.subparsers.subparsers import writersedit as writersEditSubparser
from util.subparsers.subparsers import writersdelete as writersDelSubparser
from util.subparsers.subparsers import writersassign as writersAssignSubparser

from util.subparsers.subparsers import writerslist as writersListSubparser
from util.subparsers.subparsers import writerstodo as writersTodoSubparser

SUBPARSER_KEYWORD = 'writers'

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `writers` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Display a warning to the user
    print('Error: No writer submodule provided. Use --help for more information')

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the writers subparser to a given subparsers object and delegates writer
    functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to add
                      the writers subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags
    """
    writerParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    writerParser.set_defaults(func=operate)
    subparsers = writerParser.add_subparsers()
    writersListSubparser.add_to_subparser_object(subparsers, parentParser)
    writersTodoSubparser.add_to_subparser_object(subparsers, parentParser)
    writersAddSubparser.add_to_subparser_object(subparsers, parentParser)
    writersEditSubparser.add_to_subparser_object(subparsers, parentParser)
    writersDelSubparser.add_to_subparser_object(subparsers, parentParser)
    writersAssignSubparser.add_to_subparser_object(subparsers, parentParser)
