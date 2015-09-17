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
