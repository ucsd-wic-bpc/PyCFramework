################################################################################
# Filename: test_definitions.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     16 September 2015
#
# Contains tests for util/definitions.py
################################################################################
import unittest
import os
from unittest import mock
from util.definitions import Definitions
from util.matcher import Matcher
from util.pathmapper import PathMapper

class TestDefinitionsUnit(unittest.TestCase):
    """
    White-Box Unit Test for Definitions.py
    """

    def test_globals(self):
        """
        Ensure Definitions globals are not misvalued in such a way as to cause issues
        """
        self.assertNotEqual(Definitions.DEFINITIONS_FILE, None)
        self.assertIsInstance(Definitions.DEFINITIONS_FILE, str)
        self.assertEqual(Definitions._definitionsDict, None)

    @mock.patch.object(Definitions, 'load_definitions')
    def test_get_value_unit(self, mocked_load_definitions):
        """
        Ensure Definitions.get_value functions properly as a unit
        """
        
        # Before doing anything, definitionsDict should be None and load called
        def setDefDict():
            Definitions._definitionsDict = {}
        mocked_load_definitions.side_effect = setDefDict
        self.assertEqual(Definitions.get_value('invalidKey'), None)
        mocked_load_definitions.assert_called_with()

        # With a good definitions dict, ensure a key inside the dict returns val
        mocked_load_definitions.side_effect = None
        Definitions._definitionsDict = {
                                            'key1' : 'val1',
                                            'key2' : 'val2'
                                       }
        self.assertEqual(Definitions.get_value('key1'), 'val1')
        self.assertEqual(Definitions.get_value('nonkey'), None)
        Definitions._definitionsDict = None

    @mock.patch.object(Definitions, 'get_definitions_filepath')
    @mock.patch('util.definitions.fileops')
    def test_load_definitions(self, mocked_fileops, mocked_get_def_filepath):
        """
        Ensure Definitions.load_definitions properly receives fileops output
        """
        mocked_get_def_filepath.return_value = 'fakepath'
        mocked_fileops.get_json_dict.return_value = {'hello' : 'hi'}

        Definitions.load_definitions()
        self.assertEqual(Definitions._definitionsDict, {'hello' : 'hi'})
        mocked_fileops.get_json_dict.assert_called_with('fakepath')

    @mock.patch.object(PathMapper, 'get_config_path')
    @mock.patch('util.definitions.fileops')
    def test_get_definitions_filepath(self, mocked_fileops, 
            mocked_pathmapper_get_conf_path):
        """
        Ensure Definitions.get_definitions_filepath properly delegates to fileops
        """
        mocked_fileops.join_path.return_value = 'hi'
        mocked_pathmapper_get_conf_path.return_value = 'lol'
        self.assertEqual(Definitions.get_definitions_filepath(), 'hi')
        mocked_fileops.join_path.assert_called_with('lol', Definitions.DEFINITIONS_FILE)

    @mock.patch.object(Definitions, 'get_value')
    @mock.patch.object(Matcher, 'from_variable_string')
    def test_get_value_matcher(self, mocked_matcher_from_var_string, mocked_get_value):
        mocked_get_value.return_value = 'hello'
        mocked_matcher_from_var_string.return_value = 'hi'
        self.assertEqual(Definitions.get_value_matcher('key'), 'hi')
        mocked_get_value.assert_called_with('key')
        mocked_matcher_from_var_string.assert_called_with('hello')

class TestDefinitionsFunctional(unittest.TestCase):
    """
    Black-Box Functional Tests/Acceptance Tests for Definitions.py
    """

    @mock.patch.object(PathMapper, 'get_config_path')
    def test_get_definitions_filepath(self, mocked_pathmapper_get_conf_path):
        """
        Ensure Definitions.get_definitions_filepath works as expected
        """
        mocked_pathmapper_get_conf_path.return_value = 'configPath'
        self.assertEqual(Definitions.get_definitions_filepath(),
                os.path.join('configPath', Definitions.DEFINITIONS_FILE))
