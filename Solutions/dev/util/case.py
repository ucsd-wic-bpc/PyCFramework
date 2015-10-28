################################################################################
# Filename: util/case.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     06 October 2015
#
# Contains information pertaining to test cases
################################################################################
from util import fileops
from util.variables import Variables
from util.pathmapper import PathMapper
from util.definitions import Definitions
import difflib

class CaseType:
    """
    An Enum for differentiating between various types of cases
    """
    SAMPLE = 0
    CORNER_CASE = 1
    GENERATED = 2

    SAMPLE_STRING_KEY = 'sample_case_type'
    CORNER_STRING_KEY = 'corner_case_type'
    GENERATED_STRING_KEY = 'generated_case_type'

    @staticmethod
    def from_string(string: str) -> int:
        """
        Converts the CaseType strings defined in the definitions file to
        their respective enum int values. If invalid string, assumed generated

        :param string: The string to convert to enum
        """
        if string == Definitions.get_value(CaseType.SAMPLE_STRING_KEY):
            return CaseType.SAMPLE
        elif string == Definitions.get_value(CaseType.CORNER_STRING_KEY):
            return CaseType.CORNER_CASE
        else:
            return CaseType.GENERATED

    @staticmethod
    def to_string(caseType: int) -> str:
        """
        Converts the casetype enum int into a readable string
        """
        if caseType == CaseType.SAMPLE:
            return Definitions.get_value(CaseType.SAMPLE_STRING_KEY)
        elif caseType == CaseType.CORNER_CASE:
            return Definitions.get_value(CaseType.CORNER_STRING_KEY)
        else:
            return Definitions.get_value(CaseType.GENERATED_STRING_KEY)

class Case:
    """
    Stores a general case object with specific input
    """
    NAMING_DEFINITION_KEY = 'case_naming'
    CASES_JSON_KEY = 'cases'
    CASES_INPUT_KEY = 'input'

    def __init__(self, caseType, problemNumber, caseNumber, inputContents):
        self.caseType = caseType
        self.problemNumber = problemNumber
        self.caseNumber = caseNumber
        self.inputContents = inputContents

    def get_case_string(self):
        return CaseType.to_string(self.caseType)

class KnownCase(Case):
    """
    Stores a general case object with specific input and output
    """
    CASES_OUTPUT_KEY = 'output'

    def __init__(self, caseType, problemNumber, caseNumber, inputContents, 
            outputContents):
        super().__init__(caseType, problemNumber, caseNumber, inputContents)
        self.outputContents = str(outputContents)

    def get_output_diff(self, otherOutput: str) -> str:
        """
        Returns `diff otherOutput self.outputContents`
        """
        return '\n'.join(difflib.ndiff(otherOutput.splitlines(),
            self.outputContents.splitlines())) + '\n'

    @staticmethod
    def from_case(case, outputContents):
        """
        Constructs a KnownCase object from an existing Case object by
        adding on the specified output

        :param case: The case to construct from
        :param outputContents: The output to add
        """
        return KnownCase(case.caseType, case.problemNumber, case.caseNumber,
                case.inputContents, outputContents)

def get_cases_from_json_file(path):
    """
    Return a list of Case objects from a JSON file located at path. Does so
    by extracting extracting the problem number and type from the filename
    and then delegating
    """
    # Get the problem number from the path
    problemTypeTuple = _get_file_problemnumber_type_tuple(path)

    return _get_cases_from_json_file_given_problem_type(path, 
            problemTypeTuple[0], problemTypeTuple[1])

def _get_cases_from_json_file_given_problem_type(path, problemNumber, caseType):
    """
    Return a list of Case object from a JSON file located at path given
    the case type and problem number
    """
    return get_cases_from_json(fileops.get_json_dict(path), problemNumber,
            caseType)

def _get_file_problemnumber_type_tuple(path):
    """
    Extracts the problem number and case type from the file name at path

    :returns: (problemnumber:int, casetype:int)
    """
    filename = fileops.get_basename_less_extension(path)

    # Extract problem number
    filenameMatcher = Definitions.get_value_matcher(Case.NAMING_DEFINITION_KEY)
    problemNumber = filenameMatcher.get_variable_value(filename,
            Variables.get_variable_key_name(Variables.NAME_PROBLEM_NUMBER))

    # Extract case type
    caseType = filenameMatcher.get_variable_value(filename,
            Variables.get_variable_key_name(Variables.NAME_CASE_TYPE))
    if problemNumber is None:
        return None
    return (int(problemNumber), CaseType.from_string(caseType))

    # Return the tuple
    return (int(problemNumber), CaseType.from_string(caseType))

def _get_all_cases(directory, problemNumber=None):
    """
    Looks through directory and creates Case objects from all files in
    the directory.

    :return: A dictionary of cases keyed by the problem number
    """
    cases = {}

    for possibleCaseFile in fileops.get_files_in_dir(directory):
        problemTypeTuple = _get_file_problemnumber_type_tuple(possibleCaseFile)
        if (not problemNumber is None and 
            not problemTypeTuple[0] == int(problemNumber)):
            continue
        if not problemTypeTuple[0] in cases:
            cases[problemTypeTuple[0]] = []
        cases[problemTypeTuple[0]].extend(
                _get_cases_from_json_file_given_problem_type(possibleCaseFile,
                problemTypeTuple[0], problemTypeTuple[1]))

    return cases

def get_all_cases(problemNumber=None):
    """
    Resolves the cases directory from the definitions file and delegates to
    _get_all_cases

    :return: {problemNumber: [Case]}
    """
    return _get_all_cases(fileops.join_path(PathMapper._rootPath, 
        Definitions.get_value('test_directory')), problemNumber=problemNumber)

def get_cases_from_json(json, problemNumber, caseType):
    """
    Create a list of Case objects from the specified json with the provided
    problem number and case type

    :return: [Case]
    """
    caseList = []

    for caseNumberStr, caseContents in json[Case.CASES_JSON_KEY].items():
        caseObject = Case(caseType, problemNumber, int(caseNumberStr), 
                _parse_input_json(caseContents[Case.CASES_INPUT_KEY]))
        if KnownCase.CASES_OUTPUT_KEY in caseContents:
            caseList.append(KnownCase.from_case(caseObject, 
                caseContents[KnownCase.CASES_OUTPUT_KEY]))
        else:
            caseList.append(caseObject)

    return caseList

def _parse_output_json(jsonData):
    if not isinstance(jsonData, dict):
        if not isinstance(jsonData, list):
            jsonData = [jsonData]
        return fileops.get_json_string(jsonData)
    else:
        return fileops.get_json_string([jsonData[key] for key in 
            sorted(jsonData.keys())])
