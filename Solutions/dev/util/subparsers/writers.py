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

def operate(args):
    commandArg = args.command
    if commandArg is None:
        return

    if commandArg == LIST_COMMAND:
        list_writer(args)
    elif commandArg == TODO_COMMAND:
        display_todo_for_writer(args)
    elif commandArg == ADD_COMMAND:
        add_writer(args)
    elif commandArg == DELETE_COMMAND:
        delete_writer(args)
    else:
        invalid_command(args)

def add_to_subparser_object(subparserObject, parentParser):
    writerParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    writerParser.add_argument('command')
    writerParser.set_defaults(func=operate)

def list_writer(args):
    writerDetailsList = []
    if args.writer:
        writerDetailsList = [str(writer) for writer in 
                _parse_delinieated_writer_name_list(args.writer, ',')]
    else:
        writerDetailsList = [str(writer) for writer in Writers.get_all_writers()]

    # TODO: Change this print statement to the new output format
    print('\n'.join(writerDetailsList))

def _parse_delinieated_writer_name_list(string, delimeter):
    writerList = []
    for writer in string.split(delimeter):
        loadedWriter = Writer.load_from_folder(writer)
        if loadedWriter is None:
            raise PyCException('Error: {} is an invalid Writer'.format(writer))
        else:
            writerList.append(loadedWriter)

    return writerList

def display_todo_for_writer(args):
    writerTodoList = []
    if args.writer:
        writerTodoList = [_get_todo_str_for_writer(writer) for writer in 
                _parse_delinieated_writer_name_list(args.writer, ',')]
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
