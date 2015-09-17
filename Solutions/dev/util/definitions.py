################################################################################
# Filename: definitions.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains information for parsing the definitions file
################################################################################
from util import fileops
from util.matcher import Matcher

class Definitions:
    DEFINITIONS_FILE = 'definitions.json'

    def __init__(self, pathMapper):
        self._definitionsDict = None
        self._pathMapper = pathMapper

    def get_value(self, key):
        """
        Gets the value of the definition given by key
        """
        if self._definitionsDict is None:
            self.load_definitions()

        if not key in self._definitionsDict:
            return None
        else:
            return self._definitionsDict[key]

    def load_definitions(self):
        """
        Load the definitions dictionary from the definitions file
        """
        self._definitionsDict = fileops.get_json_dict(self.get_definitions_filepath())

    def get_definitions_filepath(self):
        """
        Gets the filepath of the definitions file based on the path mapper
        """
        return fileops.join_path(self._pathMapper.get_config_path(), Definitions.DEFINITIONS_FILE)

    def get_value_matcher(self, key):
        """
        Gets a matcher object for the definition value given by key
        """
        return Matcher.from_variable_string(self.get_value(key))
