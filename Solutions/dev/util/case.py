################################################################################
# Filename: util/case.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     06 October 2015
#
# Contains information pertaining to test cases
################################################################################
from util import fileops
from util.variables import Variables
from util.definitions import Definitions

class CaseType:
    SAMPLE = 0
    CORNER_CASE = 1
    GENERATED = 2

    SAMPLE_STRING_KEY = 'sample_case_type'
    CORNER_STRING_KEY = 'corner_case_type'
    GENERATED_STRING_KEY = 'generated_case_type'

    @staticmethod
    def from_string(string):
        if string == Definitions.get_value(CaseType.SAMPLE_STRING_KEY):
            return CaseType.SAMPLE
        elif string == Definitions.get_value(CaseType.CORNER_STRING_KEY):
            return CaseType.CORNER_CASE
        else:
            return CaseType.GENERATED

class Case:
    NAMING_DEFINITION_KEY = 'case_naming'
    CASES_JSON_KEY = 'cases'

    def __init__(self, caseType, problemNumber, caseNumber, inputContents):
        self.caseType = caseType
        self.problemNumber = problemNumber
        self.caseNumber = caseNumber
        self.inputContents = inputContents

class KnownCase(Case):

    def __init__(self, caseType, problemNumber, caseNumber, inputContents, 
            outputContents):
        super().__init__(caseType, problemNumber, caseNumber, inputContents)
        self.outputContents = outputContents

    @staticmethod
    def from_case(case, outputContents):
        return KnownCase(case.caseType, case.problemNumber, case.caseNumber,
                case.inputContents, outputContents)


def get_cases_from_json_file(path):

    # Get the problem number from the path
    filename = fileops.get_basename_less_extension(path)
    filenameMatcher = Definitions.get_value_matcher(Case.NAMING_DEFINITION_KEY)
    problemNumber = filenameMatcher.get_variable_value(filename,
            Variables.get_variable_key_name(Variables.NAME_PROBLEM_NUMBER))
    caseType = filenameMatcher.get_variable_value(filename,
            Variables.get_variable_key_name(Variables.NAME_CASE_TYPE))

    return get_cases_from_json(fileops.get_json_dict(path), problemNumber,
            CaseType.from_string(caseType))


def get_cases_from_json(json, problemNumber, caseType):
    caseList = []

    for caseNumberStr, caseContents in json[Case.CASES_JSON_KEY].items():
        caseObject = Case(caseType, problemNumber, int(caseNumberStr), 
                caseContents['input'])
        if 'output' in caseContents:
            caseList.append(KnownCase.from_case(caseObject, caseContents['output']))
        else:
            caseList.append(caseObject)

    return caseList
