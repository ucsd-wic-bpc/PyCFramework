################################################################################
# Filename: util/subparsers/subparsers/writersadd.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     09 March 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers add
################################################################################
from util.writer import Writers, Writer
from util.perror import PyCException
from util.pathmapper import PathMapper
import sys
SUBPARSER_KEYWORD = 'add'



def operate(args):
    """
    Takes the passed in args and delegates to proper functionality. This is set
    as the executable function when the `writers add` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Should we launch interactive mode?
    if args.writer_names is None or len(args.writer_names) == 0:
        add_users_interactively()
    elif len(args.writer_names) == 1:
        add_user_quick(args.writer_names[0])
        #TODO: Delegate to the EDIT subparser to edit this user with details
    else:
        # Create users with the names provided
        add_users_quick(args.writer_names)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the "add" subparser to a given subparsers object and delegates add 
    functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to
                      add the "add" subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global glags.
    """
    addParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                            parents=[parentParser])

    # Add the writer names positional. If this turns out to be an empty list,
    # interactive mode will be launched. Else, the given writers will be created
    addParser.add_argument('writer_names', nargs='*')
    addParser.set_defaults(func=operate)

def add_user_quick(userName: str):
    """
    Adds a user by simply creating their folder and adding their entry to the
    writers.json dict. If the writer exists, an exception is thrown.

    Arguments:
    userName: str - The writer name to create
    """
    if Writers.writer_exists(userName):
        raise PyCException('Error: Writer {} already exists'.format(userName))
    
    mappedWriterPath = PathMapper.get_mapped_path(userName)
    newWriter = Writer(writerPath=mappedWriterPath)
    try:
        newWriter.create()
    except Exception as e:
        raise PyCException('Error: Could not create writer{}'.format(userName))

def add_users_quick(userList: list):
    """
    Adds many users by simply creating their folders and adding their entries
    to the writers.json dict. If a writer exists, an exception is thrown.

    Arguments:
    userList: list - The writer names to create
    """
    invalidUsers = []
    for user in userList:
        try:
            add_user_quick(user)
        except PyCException:
            invalidUsers.append(user)

    if len(invalidUsers) > 0:
        raise PyCException('Error: Writers {} already exist'.format(invalidUsers))

def add_users_interactively():
    """
    Adds many users by allowing the user to interactively create information
    in the same way that it would be parsed from the CSV file using "import".
    """
    print(("Enter user information, one per line, in the following template:\n"
        'folder,"full name","email","language1,language2"'))
    userInput = sys.stdin.read()
    # TODO: Delegate to import module
    print(userInput)
