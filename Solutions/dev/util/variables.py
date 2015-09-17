################################################################################
# Filename: variables.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     14 September 2015
#
# Contains information and functions pertaining to the Variables class, which 
# interacts with the variables file
################################################################################
from util import fileops

class Variables:
    VARIABLES_FILE = 'variables.json'

    #### VARAIBLE NAMES
    NAME_PROBLEM_NUMBER = 'problem_number'

    def __init__(self, pathMapper):
        self._variablesDict = None
        self._pathMapper = pathMapper

    def load_variables(self):
        """
        Load the variables dictionary from the variables file
        """
        self._variablesDict = fileops.get_json_dict(self.get_variables_filepath())

    def get_variables_filepath(self):
        """
        Gets the filepath of the variables file based on a given path mapper
        """
        return fileops.join_path(self._pathMapper.get_config_path(), 
                Variables.VARIABLES_FILE)

    def get_variable_key(self, variableName: str) -> str:
        """
        Gets a {variable}-style key for a certain variable name, None if nonexistent
        """
        if self._variablesDict is None:
            self.load_variables()

        if not variableName in self._variablesDict:
            return None
        else:
            return self._variablesDict[variableName]

    def get_variable_key_name(self, variableName: str) -> str:
        """
        Gets a {variable}-style key without {} for a certain variable name. 
        None if nonexistent
        """
        variableKey = self.get_variable_key(variableName)

        # Parse out the {} if they exist. If not, return just the var
        if not variableKey is None and variableKey[0] == '{' and variableKey[-1] == '}':
            return variableKey[1:-1]
        elif not variableKey is None:
            return variableKey
        else:
            return None
