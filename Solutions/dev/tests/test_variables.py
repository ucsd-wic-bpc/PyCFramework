################################################################################
# Filename: test_variables.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     17 September 2015
#
# Contains tests for util/variables.py
################################################################################
import unittest
from unittest import mock
from util.variables import Variables

class TestVariables(unittest.TestCase):

    def test_init(self):
        """
        Ensure Variables.__init__ sets variables properly
        """
        testVariables = Variables('pathmappah')
        self.assertEqual(testVariables._variablesDict, None)
        self.assertEqual(testVariables._pathMapper, 'pathmappah')

    @mock.patch.object(Variables, 'get_variables_filepath')
    @mock.patch('util.variables.fileops')
    def test_load_variables(self, mocked_variables_fileops, 
            mocked_variables_get_variables_filepath):
        """
        Ensure Variables.load_variables delegates to fileops properly
        """
        mocked_variables_fileops.get_json_dict.return_value = {'hello' : 'hi'}
        mocked_variables_get_variables_filepath.return_value = 'tshirt'
        testVariables = Variables(None)
        testVariables.load_variables()
        self.assertEqual(testVariables._variablesDict, {'hello' : 'hi'})
        mocked_variables_fileops.get_json_dict.assert_caled_with('tshirt')
        mocked_variables_get_variables_filepath.assert_called_with()

    @mock.patch('util.variables.fileops')
    def test_get_variables_filepath(self, mocked_variables_fileops):
        """
        Ensure Variables.get_variables_filepath delegates to PathMapper and fileops
        """
        mocked_variables_fileops.join_path.return_value = 'leaves'
        mockedPathMapper = mock.MagicMock()
        mockedPathMapper.get_config_path.return_value = 'fake_config_path'
        testVariables = Variables(mockedPathMapper)
        self.assertEqual(testVariables.get_variables_filepath(), 'leaves')
        mocked_variables_fileops.join_path.assert_called_with('fake_config_path', 
                Variables.VARIABLES_FILE)

    @mock.patch.object(Variables, 'load_variables')
    def test_get_variable_key(self, mocked_load_variables):
        """
        Ensure Variables.get_variable_key properly calls to the variables dict
        """
        # Ensure that before a dict exists, it is created
        testVariables = Variables(None)
        def setVarDict():
            testVariables._variablesDict = {}
        mocked_load_variables.side_effect = setVarDict
        self.assertEqual(testVariables.get_variable_key('varName'), None)
        mocked_load_variables.assert_called_with()

        # Ensure that if a dict exists and key exists, it is returned
        mocked_load_variables.side_effect = None
        testVariables._variablesDict = {'key' : '{varVal}',
                                        'key2': '{varVal2}'}
        self.assertEqual(testVariables.get_variable_key('key'), '{varVal}')

        # Ensure that if the key doesnt exist, none is returned
        self.assertEqual(testVariables.get_variable_key('nonkey'), None)

    @mock.patch.object(Variables, 'get_variable_key')
    def test_get_variable_key_name(self, mocked_get_variable_key):
        """
        Ensure Variables.get_variable_key_name properly eliminates curly braces
        """
        # Ensure proper operation from expected input
        testVariables = Variables(None)
        mocked_get_variable_key.return_value = '{variable}'
        self.assertEqual(testVariables.get_variable_key_name('name'), 'variable')
        mocked_get_variable_key.assert_called_with('name')

        # Ensure missing curly brace non-operate
        mocked_get_variable_key.return_value = '{variable'
        self.assertEqual(testVariables.get_variable_key_name('name'), '{variable')
        mocked_get_variable_key.assert_called_with('name')

        # Ensure missing key
        mocked_get_variable_key.return_value = None
        self.assertEqual(testVariables.get_variable_key_name('name'), None)
        mocked_get_variable_key.assert_called_with('name')
