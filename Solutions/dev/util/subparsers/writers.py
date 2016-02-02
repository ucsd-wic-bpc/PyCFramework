################################################################################
# Filename: util/subparses/writers.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     16 December 2015
#
# Contains logic for the subparser that is invoked when calling 
#  $ ./runner.py writers
################################################################################
from util.writer import Writer, Writers
from util.perror import PyCException
from util import fileops
from util.pathmapper import PathMapper
from util.language import Languages
from util.definitions import Definitions
from random import shuffle
from collections import deque

from util.subparsers.subparsers import writerslist as writersListSubparser
from util.subparsers.subparsers import writerstodo as writersTodoSubparser

SUBPARSER_KEYWORD = 'writers'
ADD_COMMAND    = 'add'
EDIT_COMMAND   = 'edit'
DELETE_COMMAND = 'delete'
IMPORT_COMMAND = 'import'
ASSIGN_COMMAND = 'assign'

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `writers` subparser is used

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # Differentiate between writers command and additional args
    commandArg = args.command
    if commandArg is None or len(commandArg) == 0:
        # TODO: Switch to new output format
        print('Error: No command word was provided for writers module')
        return

    commandPositionals = commandArg[1:]
    command = commandArg[0]

    if command == ADD_COMMAND:
        add_writer(commandPositionals, args)
    elif command == DELETE_COMMAND:
        delete_writer(commandPositionals, args)
    elif command == IMPORT_COMMAND:
        import_writers(commandPositionals)
    elif command == EDIT_COMMAND:
        edit_writer(commandPositionals[0], args.name, args.email, args.language)
    elif command == ASSIGN_COMMAND:
        assign_problems(commandPositionals, args.problems, args.language)
    else:
        #TODO: Change this print statement to the new output format
        print('Error: {} is not a valid writers command'.format(command))

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
    writerParser.add_argument('command', nargs='*')
    writerParser.set_defaults(func=operate)
    subparsers = writerParser.add_subparsers()
    writersListSubparser.add_to_subparser_object(subparsers, parentParser)
    writersTodoSubparser.add_to_subparser_object(subparsers, parentParser)


def _form_writer_list_from_names(writerNames:list, skipInvalidWriters=False):
    """
    Private function to load all writers whose names are provided. 

    Arguments:
    writerNames: list - The list of writer names to load

    KeywordArguments:
    skipInvalidWriters - If true, simply skip invalid writers. If false, raise
                         an exception. (Default False)

    Return:
    A list of loaded Writer objects corresponding to the names provided
    """
    writerList = []
    for writer in writerNames:
        loadedWriter = Writer.load_from_folder(writer)
        if loadedWriter is None:
            raise PyCException('Error: {} is an invalid Writer'.format(writer))
        else:
            writerList.append(loadedWriter)

    return writerList

def display_todo_for_writer(writers:list, args):
    """
    Prints the list of writers and the problems they have yet to complete to
    the console. 

    Arguments:
    writers: list   - The list of writer names to print. If empty, print all.
    args: Namespace - Any additional arguments that may be used for global flags
    """
    writerTodoList = []
    if not writers is None and len(writers) > 0:
        writerTodoList = [_get_todo_str_for_writer(writer) for writer in
                _form_writer_list_from_names(writers)]
    else:
        writerTodoList = [_get_todo_str_for_writer(writer) for writer in 
                Writers.get_all_writers()]

    # TODO: Change this print statement to the new output format
    print('\n'.join(writerTodoList))

def _get_todo_str_for_writer(writer):
    """
    Gets a todo string for the given writer, where each problem is delineated
    with a new line

    Arguments:
    writer: Writer - The writer whose todo list should be returned.

    Return:
    A string containing the writer's name and the problems they have yet to 
    complete
    """
    return '{}:\n{}'.format(writer.name, '\n'.join(['{} in {}'.format(
        problem[0], problem[1]) for problem in 
        writer.get_assigned_problems_not_started()]))

def add_writer(writers: list, args):
    """
    Creates the specified new writers if they do not exist.

    Arguments:
    writers: list   - The list of writer names to create. If more than one name
                      is declared, create writers without additional details. If
                      only one name is declared, additional details (name, email,
                      languages) may be provided via global flags.
    args: Namespace - Any additional arguments that may be used for global flags
    """
    # Always create the writer without additional details
    _quick_create_writers(writers)

    # Add additional details if there is only one writer specified
    if len(writers) == 1:
        edit_writer(writers[0], args.name, args.email, args.language)

def _quick_create_writers(writers: list):
    """
    Private function.
    Creates the specified new writers with no additional details if they do
    not already exist.

    Arguments:
    writers: list - The list of writer names to create
    """
    for writer in writers:
        if Writers.writer_exists(writer):
            raise PyCException('Error: Writer {} already exists'.format(writer))
        
        mappedWriterPath = PathMapper.get_mapped_path(writer)
        newWriter = Writer(writerPath=mappedWriterPath)
        try:
            newWriter.create()
        except Exception as e:
            raise PyCException('Error: Could not create writer {}'.format(writer))

def edit_writer(writer, writerName, writerEmail, writerLanguageList):
    """
    Changes the details of the provided writer to match the specified details.
    Overwrites all existing details. If a parameter is None, will not edit that
    writer detail.

    Arguments:
    writer: Writer           - The writer whose details need to be changed
    writerName: str          - The new name of the writer
    writerEmail: str         - The new email of the writer
    writerLanguageList: list - The new list of languages (str) that the writer 
                               knows.
    """
    writerObject = Writer.load_from_folder(writer)
    if writer is None:
        raise PyCException('Error: Writer {} does not exist'.format(writer))

    if not writerName is None:
        writerObject.name = writerName

    if not writerEmail is None:
        writerObject.email = writerEmail

    if not writerLanguageList is None:
        writerObject.clear_known_languages()
        writerObject.add_known_language_from_list(writerLanguageList)

    writerObject.save_changes()
    
def delete_writer(writers: list, args):
    """
    Deletes the specified writers by removing their folders and removing them
    from the writers JSON database

    Arguments:
    writers: list   - The list of writer names who should be removed
    args: Namespace - Any additional arguments that may be used for global flags
    """
    for writer in writers:
        writerToDelete = Writer.load_from_folder(writer)
        if writerToDelete is None:
            raise PyCException('Error: {} is an invalid writer'.format(writer))

        writerToDelete.delete()

def _get_filtered_writers(nameContains: str, emailContains: str, knowsLanguages: list):
    """
    A private function that returns a list of writers who follow the provided
    filters. If field is None, all matches are considered.

    Arguments:
    nameContains: str    - The string Writer.name should contain
    emailContains: str   - The string Writer.email should contain
    knowsLanguages: list - The languages the writer should know

    Returns:
    The list of writers matching the given filters
    """
    writerList = Writers.get_all_writers()
    filteredWriterList = []
    for writer in writerList:
        if not nameContains is None:
            if not nameContains in writer.name:
                continue

        if not emailContains is None:
            if not emailContains in writer.email:
                continue

        if not knowsLanguages is None:
            for language in knowsLanguages:
                if not writer.knows_language(language):
                    continue

        filteredWriterList.append(writer)

    return filteredWriterList

def import_writers(csvFiles: list):
    """
    Creates the writers specified by the provided CSV files. The CSV files 
    should follow the format:

    <folder>,<name>,<email>,"<language1>,<language2>"
    <folder>,<name>,<email>,"<language1>,<language2>"

    Arguments:
    csvFiles:list - The list of CSV file paths to import from
    """
    for csvFile in csvFiles:
        relativePath = PathMapper.get_mapped_path(csvFile)
        writerDataList = fileops.parse_csv(relativePath)
        for individualWriterDataChunk in writerDataList:
            _create_writer_from_list(individualWriterDataChunk)

def _create_writer_from_list(datalist: list):
    """
    Private function. Creates a single writer from a list following format:

    ["folder","name","email","language1,language2"]

    Arguments:
    datalist:list - The list of data to load into the writer
    """
    if datalist is None or not len(datalist) == 4:
        raise PyCException('Cannot create writer from datalist {}. Malformatted'
                .format(str(datalist)))

    newWriter = Writer(writerPath = datalist[0], writerName = datalist[1],
            writerEmail = datalist[2])
    newWriter.create()
    splitLanguageList = [languageName.strip() for languageName in datalist[3].split(',')]
    newWriter.add_known_language_from_list(splitLanguageList)

def assign_problems(writerNames: list, problemNumbers: list, languageNames: list):
    """
    Assigns problems to the given writers following the given filters. If
    no filters are provided, assigns all problems to all writers

    Arguments:
    writerNames: list    - The list of writers to assign problems to
    problemNumbers: list - The problems to assign
    languageNames: list  - The languages to assign
    """
    #TODO: Improve this so that problems can be assigned dynamically using filters
    loadedWriterList = []
    # First, load all writers
    if writerNames is None or len(writerNames) == 0:
        loadedWriterList = Writers.get_all_writers()
    else:
        for writerName in writerNames:
            loadedWriter = Writer.load_from_folder(writerName)
            if loadedWriter is None:
                raise PyCException('Error: {} is an invalid writer'.format(writerName))
            else:
                loadedWriterList.append(loadedWriter)

    for writer in loadedWriterList:
        writer.unassign_all_problems()


    # Now, get the problem numbers
    problemNumbers = []
    if problemNumbers is None or len(problemNumbers) == 0:
        problemNumbers = list(range(1, Definitions.get_value('problem_count')+1))
        shuffle(problemNumbers)
    # TODO: Make problems flag get the correct problems

    # Now, get the languages
    languages = []
    if languageNames is None:
        languages = Languages.get_all_language_names()
    # TODO: Make languages flag get the correct languages

    writerQueue = deque(loadedWriterList)

    for language in languages:
        for problemNumber in problemNumbers:
            skippedWriters = deque()
            i = 0
            while i < Definitions.get_value('complete_threshold'):
                if len(writerQueue) == 0:
                    while not len(skippedWriters) == 0:
                        writerQueue.append(skippedWriters.popleft())
                    break

                writer = writerQueue.popleft()
                if writer.knows_language(language):
                    writer.add_assigned_problem(problemNumber, language)
                    skippedWriters.append(writer)
                else:
                    skippedWriters.appendleft(writer)
                    i -= 1

                if i == (Definitions.get_value('complete_threshold')-1):
                    while not len(skippedWriters) == 0:
                        writerQueue.append(skippedWriters.popleft())

                i += 1
