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

SUBPARSER_KEYWORD = 'writers'
LIST_COMMAND = 'list'
TODO_COMMAND = 'todo'
ADD_COMMAND = 'add'
DELETE_COMMAND = 'delete'
IMPORT_COMMAND = 'import'

def operate(args):
    commandArg = args.command
    if commandArg is None:
        return

    commandPositionals = commandArg[1:]
    command = commandArg[0]

    if command == LIST_COMMAND:
        list_writers(commandPositionals, args)
    elif command == TODO_COMMAND:
        display_todo_for_writer(commandPositionals, args)
    elif command == ADD_COMMAND:
        add_writer(args)
    elif command == DELETE_COMMAND:
        delete_writer(args)
    elif command == IMPORT_COMMAND:
        import_writers(args)
    else:
        invalid_command(args)

def add_to_subparser_object(subparserObject, parentParser):
    writerParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    writerParser.add_argument('command', nargs='*')
    writerParser.set_defaults(func=operate)

def list_writers(writers: list, args):
    writerDetailsList = []
    if len(writers) > 0:
        writerDetailsList = [str(writer) for writer in 
                _form_writer_list_from_names(writers)]
    else:
        writerDetailsList = [str(writer) for writer in Writers.get_all_writers()]

    # TODO: Change this print statement to the new output format
    print('\n'.join(writerDetailsList))

def _form_writer_list_from_names(writerNames:list, skipInvalidWriters=False):
    writerList = []
    for writer in writerNames:
        loadedWriter = Writer.load_from_folder(writer)
        if loadedWriter is None:
            raise PyCException('Error: {} is an invalid Writer'.format(writer))
        else:
            writerList.append(loadedWriter)

    return writerList

def display_todo_for_writer(writers:list, args):
    writerTodoList = []
    if len(writers) > 0:
        writerTodoList = [_get_todo_str_for_writer(writer) for writer in
                _form_writer_list_from_names(writers)]
    else:
        writerTodoList = [_get_todo_str_for_writer(writer) for writer in 
                Writers.get_all_writers()]

    # TODO: Change this print statement to the new output format
    print('\n'.join(writerTodoList))

def _get_todo_str_for_writer(writer):
    return '{}:\n{}'.format(writer.name, '\n'.join(['{} in {}'.format(
        problem[0], problem[1]) for problem in 
        writer.get_assigned_problems_not_started()]))

def add_writer(args):
    print("add")

def delete_writer(args):
    print("delete")

def invalid_command(args):
    print("invalid")

def import_writers(args):
    print("importing")
