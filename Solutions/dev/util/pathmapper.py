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

    def __init__(self, rootPath):
        """
        Initializes the path instance variable which is used as a base path
        """
        self._rootPath = rootPath

    def get_config_path(self):
        """
        Returns the full configuration directory path
        """
        return fileops.join_path(self._rootPath, self.CONFIG_DIR)
