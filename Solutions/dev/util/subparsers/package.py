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
COMPRESSION_KEYWORD = 'compression'
CONFIGURATION_FILE = "packages.json"

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
    """
    Loads the config file into the global config variable

    Keyword Arguments:
    path: str - The path to load the config from (default: conf/packages.json)
    """
    if path is None:
        path = fileops.join_path(PathMapper.get_config_path(), 
                CONFIGURATION_FILE)

    global config
    config = fileops.get_json_dict(path)

def _generate_case_naming_dict(ioType: str, caseName: str, caseNumber: int):
    """
    Generates a small file naming dictionary to replace naming variables that
    might be found in the namingScheme configuration.

    Arguments:
    ioType: str     - Whether this is the case's input or output (valid: 'input','output')
    caseName: str   - The type of the case (e.g corner, sample)
    caseNumber: int - The case number

    Return:
    The formatting dictionary
    """
    if not ioType == 'input' and not ioType == 'output':
        raise Exception('Code Error: ioType is {}. Valid values are "input" or "output"'.format(ioType))

    return { 'input_output' : ioType, 'caseType' : caseName, 'number' : caseNumber }

def package_case(caseName: str, caseDir: str, cases: list, namingScheme:str):
    """
    Packages a specific case type into the given directory, splitting input
    and output into their own directories.

    Arguments:
    caseName: str - The name of the case type to package
    caseDir: str  - The directory to package the case into
    cases: list   - The list of possible cases to package
    namingScheme: str - The naming scheme to follow for each file. 
                        Possible variables are {input_output},{caseType},{number}
    """
    inputPath = fileops.join_path(caseDir, 'input')
    outputPath = fileops.join_path(caseDir, 'output')
    fileops.make(inputPath, FileType.DIRECTORY)
    fileops.make(outputPath, FileType.DIRECTORY)

    for case in [c for c in cases if c.get_case_string() == caseName]:
        inputNamingDict = _generate_case_naming_dict('input', caseName, case.caseNumber)
        outputNamingDict = _generate_case_naming_dict('output', caseName, case.caseNumber)

        inputFilePath = fileops.join_path(inputPath, namingScheme.format(**inputNamingDict))
        outputFilePath = fileops.join_path(outputPath, namingScheme.format(**outputNamingDict))

        fileops.write_file(inputFilePath, case.inputContents)
        fileops.write_file(outputFilePath, case.outputContents)

def compress_case(caseName: str, casePath: str, compressionDict: dict):
    if compressionDict is None: return

    if compressionDict['enabled']:
        if compressionDict['method'] == 'zip':
            fileops.zipdir(casePath, '{}.zip'.format(casePath))

def package_type(packagePath: str, cases: list, packageType: dict, compressionDict: dict):
    for case in packageType['cases']:
        casePath = fileops.join_path(packagePath, case)
        fileops.make(casePath, FileType.DIRECTORY)
        package_case(case, casePath, cases, packageType['naming'])
        compress_case(case, casePath, compressionDict)

def _get_compression_from_layout_dict(layoutDict: dict):
    if COMPRESSION_KEYWORD in layoutDict:
        return layoutDict[COMPRESSION_KEYWORD]
    else:
        return None

def package_into_path(path: str, layoutDict: dict):
    for problemNumber, caseList in case.get_all_cases().items():
        problemDirName = Definitions.get_value('solution_naming').format(
                **dict(problem=problemNumber))
        problemPath = fileops.join_path(path, problemDirName)
        fileops.make(problemPath, FileType.DIRECTORY)

        for packageTypeName, packageType in layoutDict[TYPES_KEY].items():
            package_type(problemPath, caseList, packageType, 
                _get_compression_from_layout_dict(layoutDict))

def package(savePaths: list, configFilePath: str=None, layout: str=None):
    load_config_file(path=configFilePath)
    global config

    # Ensure layout is provided
    if len(config) > 1 and layout is None:
        raise Exception('Error: Must choose a package layout using --layout')
    if len(config) > 1 and not layout in config:
        raise Exception('Error: {} is an invalid layout'.format(layout))

    if len(config) == 1: layout = list(config.keys())[0]
    for path in savePaths:
        fileops.make(path, FileType.DIRECTORY)
        package_into_path(path, config[layout])
