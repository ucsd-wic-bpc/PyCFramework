################################################################################
# Filename: tests/test_case.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 October 2015
#
# Contains tests for util/case.py
################################################################################
import unittest
from util.case import CaseType, Case, KnownCase
from util.pathmapper import PathMapper
from util.definitions import Definitions
from util import case
from unittest import mock

class TestCaseType(unittest.TestCase):

    def test_globals(self):
        """
        Ensure none of CaseType's global variables are None
        """
        self.assertNotEqual(CaseType.SAMPLE, None)
        self.assertNotEqual(CaseType.CORNER_CASE, None)
        self.assertNotEqual(CaseType.GENERATED, None)
        self.assertNotEqual(CaseType.SAMPLE_STRING_KEY, None)
        self.assertNotEqual(CaseType.CORNER_STRING_KEY, None)
        self.assertNotEqual(CaseType.GENERATED_STRING_KEY, None)

    @mock.patch.object(Definitions, 'get_value')
    def test_from_string(self, mocked_definitions_get_value):
        """
        Ensure CaseType.from_string functions as expected
        """
        keyDict = {
                CaseType.SAMPLE_STRING_KEY: 'sample',
                CaseType.CORNER_STRING_KEY: 'corner'
                }
        mocked_definitions_get_value.side_effect = lambda x: keyDict[x] if x in keyDict else 'generated'
        self.assertEquals(CaseType.from_string('sample'), CaseType.SAMPLE)
        self.assertEquals(CaseType.from_string('corner'), CaseType.CORNER_CASE)
        self.assertEquals(CaseType.from_string('generated'), CaseType.GENERATED)

class TestCase(unittest.TestCase):
    
    def test_globals(self):
        """
        Ensure none of Case's global varibales are None
        """
        self.assertNotEqual(Case.NAMING_DEFINITION_KEY, None)
        self.assertNotEqual(Case.CASES_JSON_KEY, None)

    def test_init(self):
        """
        Ensure Case.__init__ sets instance variables properly
        """
        testCase = Case('caseType', 'problemNumber', 'caseNumber', 'input')
        self.assertEqual(testCase.caseType, 'caseType')
        self.assertEqual(testCase.problemNumber, 'problemNumber')
        self.assertEqual(testCase.caseNumber, 'caseNumber')
        self.assertEqual(testCase.inputContents, 'input')

class TestKnownCase(unittest.TestCase):

    def test_init(self):
        """
        Ensure KnownCase.__init__ sets instance variables properly
        """
        knownCase = KnownCase('caseType', 'problemNumber', 'caseNumber', 'input',
                'output')
        self.assertEqual(knownCase.caseType, 'caseType')
        self.assertEqual(knownCase.problemNumber, 'problemNumber')
        self.assertEqual(knownCase.caseNumber, 'caseNumber')
        self.assertEqual(knownCase.inputContents, 'input')
        self.assertEqual(knownCase.outputContents, 'output')

    def test_from_case(self):
        """
        Ensure KnownCase.from_case properly extracts information from a Case object
        """
        testCase = mock.MagicMock(spec=Case, caseType='caseType', 
                problemNumber='problemNumber', caseNumber='caseNumber',
                inputContents='input')
        testKnownCase = KnownCase.from_case(testCase, 'output')
        self.assertEqual(testKnownCase.caseType, 'caseType')
        self.assertEqual(testKnownCase.problemNumber, 'problemNumber')
        self.assertEqual(testKnownCase.caseNumber, 'caseNumber')
        self.assertEqual(testKnownCase.inputContents, 'input')
        self.assertEqual(testKnownCase.outputContents, 'output')

