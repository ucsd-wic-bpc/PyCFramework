################################################################################
# Filename: test_solution.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     17 September 2015
#
# Contains tests for util/solution.py
################################################################################
import unittest
from unittest import mock
from util.solution import Solution
from util.definitions import Definitions
from util.variables import Variables
from util.language import Languages
from nose.plugins.deprecated import DeprecatedTest

class TestSolution(unittest.TestCase):

    def test_globals(self):
        """
        Ensure Solution globals are not misvalued
        """
        self.assertNotEqual(Solution.NAMING_DEFINITION_KEY, None)

    def test_init(self):
        """
        Ensure Solution.__init__ properly sets instance variables
        """
        testSolution = Solution(solutionPath='path', problemNumber=3,
                solutionWriter='Brandon', solutionLanguage='lang')
        self.assertEqual(testSolution._path, 'path')
        self.assertEqual(testSolution.problemNumber, 3)
        self.assertEqual(testSolution.solutionWriter, 'Brandon')
        self.assertEqual(testSolution.solutionLanguage, 'lang')

    @mock.patch.object(Definitions, 'get_value_matcher')
    @mock.patch('util.solution.fileops')
    def test_is_solution_file(self, mocked_solution_fileops, 
            mocked_definitions_get_value_matcher):
        """
        Ensure Solution.is_solution_file delegates to Matcher's match
        """
        mocked_solution_fileops.get_basename_less_extension.return_value = 'basename'
        mockedMatcher = mock.MagicMock()
        mockedMatcher.matches.return_value = True
        mocked_definitions_get_value_matcher.return_value = mockedMatcher


        self.assertTrue(Solution.is_solution_file('Problem1.cpp'))
        mocked_solution_fileops.get_basename_less_extension.assert_called_with('Problem1.cpp')
        mocked_definitions_get_value_matcher.assert_called_with(Solution.NAMING_DEFINITION_KEY)
        mockedMatcher.matches.assert_called_with('basename')

    @mock.patch.object(Languages, 'get_language_from_extension')
    @mock.patch.object(Variables, 'get_variable_key_name')
    @mock.patch.object(Definitions, 'get_value_matcher')
    @mock.patch('util.solution.fileops')
    def test_load_from_path(self, mocked_solution_fileops, mocked_def_val_match,
            mocked_variables_get_var_key_name, mocked_languages_from_ext):
        """
        Ensure Solution.load_from_path calls necessary functions and returns
        """
        raise DeprecatedTest
        mocked_solution_fileops.get_basename_less_extension.return_value = 'filename'
        mockedValMatcher = mock.MagicMock()
        mockedValMatcher.get_variable_value.return_value = 'lol'
        mocked_def_val_match.return_value = mockedValMatcher
        mocked_variables_get_var_key_name.return_value = 'keyname'
        mocked_solution_fileops.get_parent_dir.return_value = 'parent'
        mocked_solution_fileops.get_basename.return_value = 'basename'
        mocked_solution_fileops.get_extension.return_value = 'extension'
        mocked_languages_from_ext.return_value = 'lang'

        createdSolution = Solution.load_from_path('path')
        self.assertEquals(createdSolution._path, 'path')
        self.assertEquals(createdSolution.problemNumber, 'lol')
        self.assertEquals(createdSolution.solutionWriter, 'basename')
        self.assertEquals(createdSolution.solutionLanguage, 'lang')

        mocked_solution_fileops.get_basename_less_extension.assert_called_with('path')
        mocked_def_val_match.assert_called_with(Solution.NAMING_DEFINITION_KEY)
        mocked_variables_get_var_key_name.assert_called_with(Variables.NAME_PROBLEM_NUMBER)
        mockedValMatcher.get_variable_value.assert_called_with('filename',
                'keyname')
        mocked_solution_fileops.get_parent_dir.assert_called_with('path')
        mocked_solution_fileops.get_basename.assert_called_with('parent')
        mocked_solution_fileops.get_extension.assert_called_with('path')
        mocked_languages_from_ext.assert_calle_with('extension')
