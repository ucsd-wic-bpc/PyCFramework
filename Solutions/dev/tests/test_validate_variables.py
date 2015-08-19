import unittest
import os
import json

VARIABLES_DEFINITIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'conf', 'variables.json')

class VariableValidationTest(unittest.TestCase):


    def test_simple_dictionary(self):
        """ Make sure variables are a simple dictionary with a one-to-one mapping """
        with open(VARIABLES_DEFINITIONS_FILE, 'r') as openVarFile:
            variablesDict = json.loads(openVarFile.read())


        self.assertTrue(isinstance(variablesDict, dict))
        for variableKey, variableItem in variablesDict.items():
            self.assertTrue(isinstance(variableKey, str))
            self.assertFalse(isinstance(variableItem, list))
            self.assertFalse(isinstance(variableItem, dict))

    def test_curly_braces(self):
        """ Make sure variables are surrounded with curly braces """
        with open(VARIABLES_DEFINITIONS_FILE, 'r') as openVarFile:
            variablesDict = json.loads(openVarFile.read())

        for variableKey, variableItem in variablesDict.items():
            self.assertTrue(variableItem[0] == '{')
            self.assertTrue(variableItem[len(variableItem) - 1] == '}')
