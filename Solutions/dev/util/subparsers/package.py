################################################################################
# Filename: util/subparsers/package.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     05 January 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py package
################################################################################
from util.pathmapper import PathMapper
from util import fileops, case
from util.fileops import FileType
from util.definitions import Definitions

SUBPARSER_KEYWORD = "package"
CONFIGURATION_FILE = "package.json"

TYPES_KEY = 'types'
config = {}

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This is
    set as the executable function when the `package` subparser is used

    Arguments:
    args: Namespace - The arguments passed in via CLI
    """
    package(args.paths, args.config, args.layout)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the package subparser to a given subparsers object and delegates 
    package functionality to the operate() function

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to add
                      the test subparser to
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags
    """
    packageParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    packageParser.add_argument('paths', nargs='+')
    packageParser.add_argument('--config')
    packageParser.add_argument('--layout')
    packageParser.set_defaults(func=operate)

def load_config_file(path=None):
    if path is None:
        path = fileops.join_path(PathMapper.get_config_path(), 
                CONFIGURATION_FILE)

    config = fileops.get_json_dict(path)

def package_case(caseName: str, caseDir: str, cases: list, namingScheme:str):
    inputPath = fileops.join(caseDir, 'input')
    outputPath = fileops.join(caseDir, 'output')
    fileops.make(inputPath, FileType.DIRECTORY)
    fileops.make(outputPath, FileType.DIRECTORY)
    for case in cases:
        if case.get_case_string() == caseName:
            inputNamingDict = {
                    'input_output' : 'input',
                    'caseType' : caseName,
                    'number' : case.caseNumber
                    }
            outputNamingDict = {
                    'input_output' : 'output',
                    'caseType' : caseName,
                    'number' : case.caseNumber
                    }

def package_type(packagePath: str, cases: list, packageType: dict):
    for typeName, typeDetailsDict in packageType.items():
        for case in typeDetailsDict['cases']:
            casePath = fileops.join_path(packagePath, case)
            fileops.make(casePath, FileType.DIRECTORY)
            package_case(case, casePath, cases, typeDetailsDict['naming'])

def package(savePaths: list, configFilePath: str=None, layout: str=None):
    load_config_file(path=configFilePath)
    global config

    # Ensure layout is provided
    if len(config) > 1 and layout is None:
        raise Exception('Error: Must choose a package layout using --layout')
    if not layout in config:
        raise Exception('Error: {} is an invalid layout'.format(layout))

    for path in savePaths:
        fileops.make(path, FileType.DIRECTORY)

        for problemNumber, caseList in case.get_all_cases().items():
            problemDirName = Definitions.get_value('solution_naming').format(
                    **{'problem' : problemNumber})
            problemPath = fileops.join_path(path, problemDirName)
            fileops.make(problemPath, FileType.DIRECTORY)
            for packageTypeName, packageType in config[layout][TYPES_KEY].items():
                package_type(problemPath, caseList, packageType)
