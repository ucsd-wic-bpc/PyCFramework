################################################################################
# Filename: conf_definitions.py
# Author:   Brandon Milton
#           http://brandonio21.com
# Date:     July 2, 2015
# 
# Test that verifies that the definitions configuration file is configured 
# properly. If test fails, something is wrong in definition config file.
################################################################################
import json
import os
import re
import unittest

# Settings
DEFINITIONS_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        'conf', 'definitions.json')
VARIABLES_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conf', 'variables.json')

class TestValidateDefinitions(unittest.TestCase):

    def test_simple_dictionary(self):
        """ Make sure that definitions config file is a simple dictionary with one-to-one mappings """
        with open(DEFINITIONS_SETTINGS_FILE, 'r') as openDefFile:
            contents = json.loads(openDefFile.read())

        self.assertTrue(isinstance(contents, dict))
        for dictKey, dictContents in contents.items():
            self.assertTrue(isinstance(dictKey, str))
            self.assertFalse(isinstance(dictContents, list))
            self.assertFalse(isinstance(dictContents, dict))

    def test_valid_variables(self):
        """ Make sure all variables used in definitions are included in variables settings file """
        with open(DEFINITIONS_SETTINGS_FILE, 'r') as openDefFile:
            definitionsContents = json.loads(openDefFile.read())
        with open(VARIABLES_SETTINGS_FILE, 'r') as openVarFile:
            variablesContents = json.loads(openVarFile.read())

        variablePattern = re.compile(r'{[^{^}]*}')
        for dictKey, dictContents in definitionsContents.items():
            variables = variablePattern.findall(str(dictContents))
            if len(variables) > 0:
                for variable in variables:
                    valid = False
                    for variableKey, variableItem in variablesContents.items():
                        if variable == variableItem:
                            valid = True
                            break
                    self.assertTrue(valid)
