###############################################################################
# Filename: util/subparsers/validate.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     23 August 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py validate
###############################################################################
import json
from util import fileops
from util.definitions import Definitions

SUBPARSER_KEYWORD = "validate"

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This is
    set as the executable function when the `validate` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    caseList = args.casefiles
    validate_arg_provided_casefiles(caseList)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the validate subparser to a given subparsers object and delegates validate
    functionality to the operate() function

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to add
                      the validate subparser to
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    validateParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    validateParser.add_argument('casefiles', nargs='*')
    validateParser.set_defaults(func=operate)

def validate_arg_provided_casefiles(filePaths: list):
    if filePaths is None or len(filePaths) == 0:
        validate_defined_case_dir()
    else:
        validate_casefiles(filePaths)

def validate_defined_case_dir():
    testDir = Definitions.get_value('test_directory')
    validate_casefiles(fileops.get_files_in_dir(testDir))

def validate_casefiles(filePaths: list):
    """
    If there are items in the provided file paths, ensure that
    they all contain proper JSON. Otherwise, validate all JSON
    case files in the definitions-defined case directory.
    """
    for filePath in filePaths:
        with open(filePath, 'r') as openFile:
            try: 
                testJson = json.loads(openFile.read())
            except Exception as e:
                print("Casefile {} contains JSON issues: {}".format(
                    filePath, e))