################################################################################
# Filename: pathmapper.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains the PathMapper class, which is used to keep track of certain paths
################################################################################
from util import fileops
from util.definitions import Definitions
from util.variables import Variables
from util.language import Languages

class PathMapper:
    CONFIG_DIR = 'conf'

    def __init__(self, rootPath):
        """
        Initializes the path instance variable which is used as a base path
        """
        self._rootPath = rootPath
        self._definitionsObject = None
        self._languagesObject = None
        self._variablesObject = None

    def get_config_path(self):
        """
        Returns the full configuration directory path
        """
        return fileops.join_path(self._rootPath, self.CONFIG_DIR)

    def get_definitions_object(self):
        """
        Returns a Definitions object pertaining to this path
        """
        if self._definitionsObject is None:
            self._definitionsObject = Definitions(self)

        return self._definitionsObject

    def get_variables_object(self):
        """
        Returns a Variables object pertaining to this path
        """
        if self._variablesObject is None:
            self._variablesObject = Variables(self)

        return self._variablesObject

    def get_languages_object(self):
        """
        Returns a Languages object pertaining to this path
        """
        if self._languagesObject is None:
            self._languagesObject = Languages(self)

        return self._languagesObject

