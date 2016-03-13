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
from util.subparsers.subparsers import writersedit as editSubparser
from util import fileops
import sys
SUBPARSER_KEYWORD = 'add'

def operate(args):
    """
    Takes the passed in args and delegates to proper functionality. This is set
    as the executable function when the `writers add` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # If the user specified 'fromcsvs', only add from the CSV files
    if not args.csvfilepaths is None and len(args.csvfilepaths) > 0:
        for filepath in args.csvfilepaths[0]:
            import_writers_from_csv_file_path(filepath)

        return

    # Should we launch interactive mode?
    if args.writer_names is None or len(args.writer_names) == 0:
        add_users_interactively(showhint = args.showhint)
    elif len(args.writer_names) == 1:
        add_user_quick(args.writer_names[0])
        editSubparser.edit_writer_information(args.writer_names[0],
                editSubparser.replace_list_with_none_if_empty(args.name),
                editSubparser.replace_list_with_none_if_empty(args.email),
                args.language)
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
                      useful for global flags.
    """
    addParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                            parents=[parentParser])

    # Add the writer names positional. If this turns out to be an empty list,
    # interactive mode will be launched. Else, the given writers will be created
    addParser.add_argument('writer_names', nargs='*')
    addParser.add_argument('--fromcsvs', action='append', dest='csvfilepaths',
            nargs='+')
    addParser.add_argument('--showhint', action='store_true')
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

def add_users_interactively(showhint=False):
    """
    Adds many users by allowing the user to interactively create information
    in the same way that it would be parsed from the CSV file using "import".
    """
    if showhint:
        print(("Enter user information, one per line, in the following template:\n"
            'folder,"full name","email","language1,language2"'))
    import_writers_from_csv_descriptor(sys.stdin)

def import_writers_from_csv_file_path(csvFilePath):
    """
    Imports the writers from a CSV file path
    """
    realPath = PathMapper.get_mapped_path(csvFilePath)
    with open(realPath, 'r') as csvFileDescriptor:
        import_writers_from_csv_descriptor(csvFileDescriptor)

def import_writers_from_csv_descriptor(csvFileDescriptor):
    """
    Imports the writers from a CSV file descriptor
    """
    writerDetailsList = fileops.parse_csv_from_file_descriptor(csvFileDescriptor)
    for individualWriterDataChunk in writerDetailsList:
        _create_writer_from_list(individualWriterDataChunk)

def _create_writer_from_list(datalist: list):
    # TODO: Change CSV implementation to use dict reader for better handling of 
    # missing information
    """
    Private function. Creates a single writer from a list following the format:

    ["folder","name","email","language1,language2"]

    Arguments:
    datalist: list - The list of data to load into the writer
    """
    # First, verify that the data list is OK
    if datalist is None or not len(datalist) == 4:
        raise PyCException('Cannot create writer from datalist {}. Malformed'
                .format(str(datalist)))

    newWriter = Writer(writerPath=datalist[0],writerName=datalist[1],
            writerEmail=datalist[2])
    newWriter.create()
    splitLanguageList = [languageName.strip() for languageName in datalist[3].split(',')]
    newWriter.add_known_language_from_list(splitLanguageList)
