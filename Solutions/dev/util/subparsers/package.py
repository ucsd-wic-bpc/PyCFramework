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

def _generate_case_naming_dict(ioType: str, caseName: str, caseNumber: int, incrementor: int):
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

    return { 'input_output' : ioType, 'caseType' : caseName, 'number' : caseNumber , 'inc' : incrementor}

def package_case(caseName: str, caseDir: str, cases: list, namingScheme:str, incrementor: int):
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
        inputNamingDict = _generate_case_naming_dict('input', caseName, case.caseNumber, incrementor)
        outputNamingDict = _generate_case_naming_dict('output', caseName, case.caseNumber, incrementor)

        inputFilePath = fileops.join_path(inputPath, namingScheme.format(**inputNamingDict))
        outputFilePath = fileops.join_path(outputPath, namingScheme.format(**outputNamingDict))

        fileops.write_file(inputFilePath, case.inputContents)
        fileops.write_file(outputFilePath, case.outputContents)
        incrementor += 1

    return incrementor

def compress_case(caseName: str, casePath: str, compressionDict: dict):
    """
    Compresses a specific case using the compression method specified in the
    configuration file.

    Arguments:
    caseName: str - The name of the case to compress
    casePath: str - The path of the case to compress
    compressionDict: dict - The dictionary corresponding to the compression
                            settings from the config file
    """
    # If there are no compression settings, dont compress
    if compressionDict is None: return

    if compressionDict['enabled']:
        if compressionDict['method'] == 'zip':
            fileops.zipdir(casePath, '{}.zip'.format(casePath))
        elif compressionDict['method'] == 'targz':
            fileops.tardir(casePath, '{}.tar.gz'.format(casePath))

def package_type(packagePath: str, cases: list, packageType: dict, compressionDict: dict,
        typeName: str):
    """
    Packages a specific case type by first making the directory that it belongs
    in, then packaging its cases, then compressing its cases

    Arguments:
    packagePath: str - The path that the user wants the package to go
    cases: list      - The list of cases that need to be package
    packageType: dict- The configuration file dictionary of package types that
                       need to be made
    compressionDict: dict - The dictionary corresponding to the compression
                            settings from the config file
    """
    incrementor = 0
    for case in packageType['cases']:
        casePath = fileops.join_path(packagePath, typeName)
        fileops.make(casePath, FileType.DIRECTORY)
        incrementor = package_case(case, casePath, cases, packageType['naming'], incrementor)
        compress_case(case, casePath, compressionDict)

def _get_compression_from_layout_dict(layoutDict: dict):
    """
    Instead of throwing a key not found exception, simply return null
    if the compression key is not found in the layout declaration

    Arguments:
    layoutDict: dict - The layout declaration as specified by the user
                       provided config file
    """
    if COMPRESSION_KEYWORD in layoutDict:
        return layoutDict[COMPRESSION_KEYWORD]
    else:
        return None

def package_into_path(path: str, layoutDict: dict):
    """
    Follows the users provided configuration file to package all cases into
    the provided path. Delegates most functionality to other functions.

    Arguments:
    path: str - The path to package into
    layoutDict: dict - The dict provided by the user's configuration
    """
    # Look through all cases...
    for problemNumber, caseList in case.get_all_cases().items():
        # Make the directories for the problem numbers
        problemDirName = Definitions.get_value('solution_naming').format(
                **dict(problem=problemNumber))
        problemPath = fileops.join_path(path, problemDirName)
        fileops.make(problemPath, FileType.DIRECTORY)

        # Go through each type in the config file and package it
        for packageTypeName, packageType in layoutDict[TYPES_KEY].items():
            package_type(problemPath, caseList, packageType, 
                _get_compression_from_layout_dict(layoutDict),
                packageTypeName)

def package(savePaths: list, configFilePath: str=None, layout: str=None):
    """
    The parent function that handles the package subparser call. Loads the
    configuration file and packages into the provided paths

    Arguments:
    savePaths: list - A list of paths to package into
    configFilePath: str - The Alternate configuration file specified by the user
    layout: str - The specific package layout to load
    """
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
