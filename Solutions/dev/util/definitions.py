################################################################################
# Filename: definitions.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains information for parsing the definitions file
################################################################################
from util import fileops

class Definitions:
    _definitionsDict = None
    DEFINITIONS_FILE = 'definitions.json'

    @classmethod
    def get_value(cls, key):
        """
        Gets the value of the definition given by key
        """
        if _definitionsDict is None:
            cls.load_definitions()

        if not key in cls._definitionsDict:
            return None
        else:
            return cls._definitionsDict[key]

    @classmethod
    def load_definitions(cls):
        """
        Load the definitions dictionary from the definitions file
        """
        cls._definitionsDict = fileops.get_json_dict(Definitions.get_definitions_filepath())

    @staticmethod
    def get_definitions_filepath(pathMapper):
        """
        Gets the filepath of the definitions file based on a given path mapper
        """
        return fileops.join_path(pathMapper.get_config_path, DEFINITIONS_FILE)

    @classmethod
    def get_value_matcher(cls, key):
        """
        Gets a matcher object for the definition value given by key
        """
        return Matcher.from_variable_string(cls.get_value(key))
