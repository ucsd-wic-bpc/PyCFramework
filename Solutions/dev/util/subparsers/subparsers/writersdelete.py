################################################################################
# Filename: util/subparsers/subparsers/writersdelete.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     10 March 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers delete
################################################################################
from util.writer import Writer
from util.perror import PyCException
import sys

SUBPARSER_KEYWORD = 'delete'

def operate(args):
    """
    Takes the passed in args and delegates to proper functionality. This is set
    as the executable function when the `writers delete` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Check to see if we should launch in interactive mode or not
    if args.writer_names is None or len(args.writer_names) == 0:
        delete_users_interactively(showHint=args.showhint)
    else:
        delete_users(args.writer_names)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the "delete" subparser to a given subparsers object and delegates 
    delete functionality to the operate() function

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to
                      add the "add" subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    deleteParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                                parents=[parentParser])
    deleteParser.add_argument('writer_names', nargs='*')
    deleteParser.add_argument('--showhint', action='store_true')
    deleteParser.set_defaults(func=operate)

def delete_users(writerNames: list):
    """
    Deletes each user whose name is given in the provided list of writer names.
    If any of the users do not exist, a joint error message is provided.

    Arguments:
    writerNames: list - The list of writer names to delete
    """
    invalidWriters = []
    for writer in writerNames:
        writerToDelete = Writer.load_from_folder(writer)
        if writerToDelete is None:
            invalidWriters.append(writer)
            continue

        writerToDelete.delete()

    if len(invalidWriters) > 0:
        raise PyCException('Error: {} are invalid writers'.format(str(invalidWriters)))

def delete_users_interactively(showHint=False):
    """
    Deletes the users whose names were provided via the interactive session,
    delineated by newlines of course.
    """
    if showHint:
        print("Enter writer names to delete, one per line, EOF to complete")

    delete_users(sys.stdin.read().splitlines())
