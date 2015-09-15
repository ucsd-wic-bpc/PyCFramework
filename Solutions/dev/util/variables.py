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
    _variablesDict = None
    VARIABLES_FILE = 'variables.json'

    #### VARAIBLE NAMES
    NAME_PROBLEM_NUMBER = 'problem_number'

    @classmethod
    def load_variables(cls):
        """
        Load the variables dictionary from the variables file
        """
        cls._variablesDict = fileops.get_json_dict(Variables.get_variables_filepath())

    @staticmethod
    def get_variables_filepath(pathMapper):
        """
        Gets the filepath of the variables file based on a given path mapper
        """
        return fileops.join_path(pathMapper.get_config_path, VARIABLES_FILE)

    @classmethod
    def get_variable_key(cls, variableName: str) -> str:
        """
        Gets a {variable}-style key for a certain variable name, None if nonexistent
        """
        if cls._variablesDict is None:
            cls.load_variables()

        if not variableName in cls._variablesDict:
            return None
        else:
            return cls._variablesDict[variableName]

    @classmethod
    def get_variable_key_name(cls, variableName: str) -> str:
        """
        Gets a {variable}-style key without {} for a certain variable name. 
        None if nonexistent
        """
        variableKey = cls.get_variable_key(variableName)

        # Parse out the {} if they exist. If not, return just the var
        if not variableKey is None and variableKey[0] == '{' and variableKey[-1] == '}':
            return variableKey[1:-1]
        elif not variableKey is None:
            return variableKey
        else:
            return None
