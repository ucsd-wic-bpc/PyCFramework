################################################################################
# Filename: test_matcher.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     14 September 2015
#
# Contains tests for the Matcher class at util/matcher.py
################################################################################
import unittest
import unittest.mock
from util.matcher import Matcher

class TestMatcher(unittest.TestCase):

    @unittest.mock.patch('util.matcher.re')
    def test_init(self, mocked_matcher_re):
        """
        Ensure Matcher.__init__ sets instance variables properly
        """
        mocked_matcher_re.compile.return_value = 'babaloo'
        testMatcher = Matcher('pattern')
        self.assertEquals(testMatcher._pattern, 'babaloo')
        mocked_matcher_re.compile.assert_called_with('pattern')

    def test_matches(self):
        """
        Ensure Matcher.matches returns a boolean depending on re.match's value
        """
        testMatcher = Matcher('pattern')
        testMatcher._pattern = unittest.mock.MagicMock()
        testMatcher._pattern.match.return_value = None
        self.assertEquals(testMatcher.matches('string'), False)
        testMatcher._pattern.match.assert_called_with('string')

        testMatcher._pattern.match.return_value = '123'
        self.assertEquals(testMatcher.matches('string'), True)
        testMatcher._pattern.match.assert_called_with('string')

    def test_get_variable_value(self):
        """
        Ensure Matcher.get_variable_value logic flows as intended
        """
        testMatcher = Matcher('pattern')
        testMatcher._pattern = unittest.mock.MagicMock()
        testMatcher._pattern.match.return_value = None
        self.assertEquals(testMatcher.get_variable_value('string', 'var'), None)
        testMatcher._pattern.match.assert_called_with('string')

        matchReturn = unittest.mock.MagicMock()
        testMatcher._pattern.match.return_value = matchReturn
        matchReturn.groupdict = {'var' : 'lol'}
        self.assertEquals(testMatcher.get_variable_value('string', 'var'), 'lol')
        testMatcher._pattern.match.assert_called_with('string')

        matchReturn.groupdict = {'var2' : 'lol'}
        self.assertEquals(testMatcher.get_variable_value('string', 'var'), None)
        testMatcher._pattern.match.assert_called_with('string')
