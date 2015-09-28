################################################################################
# Filename: util/pycexception.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     27 September 2015
#
# Used to keep track of error messages for PyCFramework
################################################################################

class PyCException(Exception):

    def __init__(self, message):
        self.message = message
