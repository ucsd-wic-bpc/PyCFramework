################################################################################
# Filename: util/subparsers/subparsers/writersedit.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     09 March 2016
# 
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers edit
################################################################################
from util.perror import PyCException
from util.writer import Writer
SUBPARSER_KEYWORD = 'edit'

def operate(args):
    """
    Takes the passed in args and delegates to proper functionality. This is set
    as the executable function when the `writers edit` subparser is used.

    Arguments:
    args: Namespace - The arguments passed in via CLI
    """
    #TODO: Add an interactive mode
    if args.writer_path is None:
        raise PyCException('Error: No writer folder provided')

    def replace_list_with_none_if_empty(list):
        if list is None: return list
        if len(list) == 0:
            return None
        else:
            return list[0]

    edit_writer_information(args.writer_path, 
            replace_list_with_none_if_empty(args.name), 
            replace_list_with_none_if_empty(args.email),
            args.language)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the "edit" subparser to a given subparsers object and delegates edit
    functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to
                      add the edit subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    editParser = subparserObject.add_parser(SUBPARSER_KEYWORD,
                                                parents=[parentParser])

    # Add the path to the writer folder as a positional
    editParser.add_argument('writer_path')
    editParser.set_defaults(func=operate)

def edit_writer_information(writerFolderPath: str, writerName: str, 
    writerEmail:str, writerLanguageList: list):
    """
    Changes the details of the writer located in the provided folder to match
    the specified details. Overwrites all existing details. If a parameter
    is None, will not edit that writer detail.

    Arguments:
    writerFolderPath: str    - The path to the writer whose details need to be 
                               changed.
    writerName: str          - The new name of the writer
    writerEmail: str         - The new email of the writer
    writerLanguageList: list - The new list of language names (str) that the
                               writer knows.
    """
    writerObject = Writer.load_from_folder(writerFolderPath)
    if writerObject is None:
        raise PyCException('Error: Writer {} does not exist'.format(writerFolderPath))

    if not writerName is None:
        writerObject.name = writerName

    if not writerEmail is None:
        writerObject.email = writerEmail

    if not writerLanguageList is None:
        writerObject.clear_known_languages()
        writerObject.add_known_language_from_list(writerLanguageList)

    writerObject.save_changes()
