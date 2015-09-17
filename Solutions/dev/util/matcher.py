################################################################################
# Filename: matcher.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains information pertaining to the Matcher object, a special re wrapper
################################################################################
import re

class Matcher:
    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def matches(self, string: str) -> bool:
        return not self._pattern.match(string) is None

    def get_variable_value(self, string: str, var: str) -> str:
        """
        Applies the matcher's pattern to the given string to get the value of the variable var

        :param string: The string to look for the variable's value in
        :param var:    The name of the variable (Which should have been within {})

        Returns None if variable not in string, otherwise returns variable value
        """
        matchObject = self._pattern.match(string)
        if matchObject is None:
            return None

        groupDict = matchObject.groupdict()
        if not var in groupDict:
            return None
        else:
            return groupDict[var]

    @staticmethod
    def from_variable_string(varString: str):
        variablePattern = r'{[^{^}]+}'
        variableMatches = re.findall(variablePattern, varString)
        while len(variableMatches) > 0:
            varString = re.sub(variablePattern, '(?P<{0}>.*)'.format(variableMatches[0][1:-1]), 
                    varString, count=1)
            variableMatches = re.findall(variablePattern, varString)

        return Matcher(varString)
