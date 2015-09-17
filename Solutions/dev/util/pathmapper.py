################################################################################
# Filename: pathmapper.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains the PathMapper class, which is used to keep track of certain paths
################################################################################
from util import fileops

class PathMapper:
    CONFIG_DIR = 'conf'

    _definitionsObject = None
    _languagesObject = None
    _variablesObject = None

    _rootPath = None

    @classmethod
    def set_root_path(cls, rootPath):
        """
        Initializes the path instance variable which is used as a base path
        """
        cls._rootPath = rootPath

    @classmethod
    def get_config_path(cls):
        """
        Returns the full configuration directory path
        """
        return fileops.join_path(cls._rootPath, cls.CONFIG_DIR)
