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

    @staticmethod
    def from_variable_string(varString: str):
        variablePattern = r'{[^{^}]+}'
        return Matcher(re.sub(variablePattern, '.*', varString))
