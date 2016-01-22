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
from util.pathmapper import PathMapper
from nose.plugins.deprecated import DeprecatedTest

class TestVariables(unittest.TestCase):

    def tearDown(self):
        Variables._variablesDict = None

    def test_globals(self):
        """
        Ensure Variable globals are set properly
        """
        self.assertEqual(Variables._variablesDict, None)

    @mock.patch.object(Variables, 'get_variables_filepath')
    @mock.patch('util.variables.fileops')
    def test_load_variables(self, mocked_variables_fileops, 
            mocked_variables_get_variables_filepath):
        """
        Ensure Variables.load_variables delegates to fileops properly
        """
        raise DeprecatedTest
        mocked_variables_fileops.get_json_dict.return_value = {'hello' : 'hi'}
        mocked_variables_get_variables_filepath.return_value = 'tshirt'
        Variables.load_variables()
        self.assertEqual(Variables._variablesDict, {'hello' : 'hi'})
        mocked_variables_fileops.get_json_dict.assert_caled_with('tshirt')
        mocked_variables_get_variables_filepath.assert_called_with()

    @mock.patch.object(PathMapper, 'get_config_path')
    @mock.patch('util.variables.fileops')
    def test_get_variables_filepath(self, mocked_variables_fileops, 
            mocked_pathmapper_get_conf_path):
        """
        Ensure Variables.get_variables_filepath delegates to PathMapper and fileops
        """
        mocked_variables_fileops.join_path.return_value = 'leaves'
        mocked_pathmapper_get_conf_path.return_value = 'fake_config_path'
        self.assertEqual(Variables.get_variables_filepath(), 'leaves')
        mocked_variables_fileops.join_path.assert_called_with('fake_config_path', 
                Variables.VARIABLES_FILE)

    @mock.patch.object(Variables, 'load_variables')
    def test_get_variable_key(self, mocked_load_variables):
        """
        Ensure Variables.get_variable_key properly calls to the variables dict
        """
        # Ensure that before a dict exists, it is created
        def setVarDict():
            Variables._variablesDict = {}
        mocked_load_variables.side_effect = setVarDict
        self.assertEqual(Variables.get_variable_key('varName'), None)
        mocked_load_variables.assert_called_with()

        # Ensure that if a dict exists and key exists, it is returned
        mocked_load_variables.side_effect = None
        Variables._variablesDict = {'key' : '{varVal}',
                                        'key2': '{varVal2}'}
        self.assertEqual(Variables.get_variable_key('key'), '{varVal}')

        # Ensure that if the key doesnt exist, none is returned
        self.assertEqual(Variables.get_variable_key('nonkey'), None)

    @mock.patch.object(Variables, 'get_variable_key')
    def test_get_variable_key_name(self, mocked_get_variable_key):
        """
        Ensure Variables.get_variable_key_name properly eliminates curly braces
        """
        # Ensure proper operation from expected input
        mocked_get_variable_key.return_value = '{variable}'
        self.assertEqual(Variables.get_variable_key_name('name'), 'variable')
        mocked_get_variable_key.assert_called_with('name')

        # Ensure missing curly brace non-operate
        mocked_get_variable_key.return_value = '{variable'
        self.assertEqual(Variables.get_variable_key_name('name'), '{variable')
        mocked_get_variable_key.assert_called_with('name')

        # Ensure missing key
        mocked_get_variable_key.return_value = None
        self.assertEqual(Variables.get_variable_key_name('name'), None)
        mocked_get_variable_key.assert_called_with('name')
