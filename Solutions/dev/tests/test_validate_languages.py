################################################################################
# Filename: conf_langauges.py
# Author:   Brandon Milton
#           http://brandonio21.com
# Date:     July 2, 2015
# 
# Test that verifies that the languages configuration file is configured 
# properly. If test fails, something is wrong in language config file.
################################################################################
import json
import os
import re
import unittest

# Settings
LANGUAGES_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conf', 'languages.json')
VARIABLES_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conf', 'variables.json')
necessaryFields = [('language', str), ('runExtension', str), ('runCommand', str), ('runArguments', list)]

class TestValidateLanguages(unittest.TestCase):
    def test_structure(self):
        """ Make sure that the languages configuration follows the required structure """
        with open(LANGUAGES_SETTINGS_FILE, 'r') as openLangFile:
            languageDict = json.loads(openLangFile.read())

        self.assertTrue(isinstance(languageDict, dict))
        self.assertTrue('languages' in languageDict)
        self.assertTrue(isinstance(languageDict['languages'], list))
        for languageBlock in languageDict['languages']:
            self.assertTrue(isinstance(languageBlock, dict))

    def test_necessary_fields(self):
        """ Make sure that each language block has the required fields """
        with open(LANGUAGES_SETTINGS_FILE, 'r') as openLangFile:
            languageDict = json.loads(openLangFile.read())

        for languageBlock in languageDict['languages']:
            for necessaryTuple in necessaryFields:
                self.assertTrue(necessaryTuple[0] in languageBlock)
                self.assertTrue(isinstance(languageBlock[necessaryTuple[0]], necessaryTuple[1]))
                if isinstance(languageBlock[necessaryTuple[0]], list):
                    self.assertTrue(all(isinstance(element, str) for element in languageBlock[necessaryTuple[0]]))

    def test_valid_variables(self):
        """ Make sure that all variables in language blocks are valid """
        with open(LANGUAGES_SETTINGS_FILE, 'r') as openLangFile:
            languageDict = json.loads(openLangFile.read())

        with open(VARIABLES_SETTINGS_FILE, 'r') as openVarFile:
            variablesContents = json.loads(openVarFile.read())

        variablePattern = re.compile(r'{[^{^}]*}')
        for languageBlock in languageDict['languages']:
            for dictKey, dictContents in languageBlock.items():
                if isinstance(dictContents, list):
                    for contents in dictContents:
                        variables = variablePattern.findall(str(contents))
                        if len(variables) > 0:
                            for variable in variables:
                                valid = False
                                for variableKey, variableItem in variablesContents.items():
                                    if variable == variableItem:
                                        valid = True
                                        break
                            self.assertTrue(valid)
                else:
                    variables = variablePattern.findall(str(dictContents))
                    if len(variables) > 0:
                        for variable in variables:
                            valid = False
                            for variableKey, variableItem in variablesContents.items():
                                if variable == variableItem:
                                    valid = True
                                    break
                        self.assertTrue(valid)
