################################################################################
# Filename: solution.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains information and functions pertaining to the Solution class
################################################################################
from util import fileops
from util.definitions import Definitions
from util.variables import Variables

class Solution:
    NAMING_DEFINITION_KEY = 'solution_naming'

    def __init__(self, solutionPath='', problemNumber=-1, solutionWriter=None,
            solutionLanguage=None):
        self._path = solutionPath
        self.problemNumber = problemNumber
        self.solutionWriter = solutionWriter
        self.solutionLanguage = solutionLanguage

    def get_output(self) -> str:
        """
        Runs the solution file given by self._path by delegating to its languages execute.
        Returns output printed to stdout
        """
        # If the solution was never given a language, output is blank
        if self.solutionLanguage is None:
            return ''

        return self.solutionLanguage.execute_path(self._path)

    @staticmethod
    def is_solution_file(path):
        """
        Checks to see if basename of file matches solution naming scheme from definitions
        """
        filename = fileops.get_basename_less_extension(path)
        return Definitions.get_value_matcher(NAMING_DEFINITION_KEY).matches(path)

    @staticmethod
    def load_from_path(path):
        """
        Creates a new Solution object from a file at path and returns it
        """
        newSolution = Solution(solutionPath=path)
        filename = fileops.get_basename_less_extension(path)
        filenameMatcher = Definitions.get_value_matcher(NAMING_DEFINITION_KEY)
        newSolution.problemNumber = filenameMatcher.get_variable_value(filename, 
                Variables.get_variable_key_name(Variables.NAME_PROBLEM_NUMBER))
        newSolution.solutionWriter = fileops.get_basename(fileops.get_parent_dir(path))
