################################################################################
# Filename: definitions.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains information for parsing the definitions file
################################################################################
from util import fileops
from util.matcher import Matcher
from util.pathmapper import PathMapper

class Definitions:
    DEFINITIONS_FILE = 'definitions.json'
    _definitionsDict = None

    @classmethod
    def get_value(cls, key):
        """
        Gets the value of the definition given by key
        """
        if cls._definitionsDict is None:
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
        cls._definitionsDict = fileops.get_json_dict(cls.get_definitions_filepath())

    @classmethod
    def get_definitions_filepath(cls):
        """
        Gets the filepath of the definitions file based on the path mapper
        """
        return fileops.join_path(PathMapper.get_config_path(), Definitions.DEFINITIONS_FILE)

    @classmethod
    def get_value_matcher(cls, key):
        """
        Gets a matcher object for the definition value given by key
        """
        return Matcher.from_variable_string(cls.get_value(key))
