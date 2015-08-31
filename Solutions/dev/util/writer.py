################################################################################
# Filename: writer.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     30 August 2015
# 
# This file contains all information pertaining to solution writers
################################################################################
import fileops

class Writer:
    DATAFILE_PATH = 'data.json'
    DATAFILE_NAME_FIELD = 'name'
    DATAFILE_EMAIL_FIELD = 'email'

    def __init__(self, writerEmail='', writerName='', writerPath=''):
        self.name = writerName
        self.email = writerEmail
        self._path = writerPath
        self._solutions = {} 

    def _get_datafile_path(self):
        """
        Return the path of the data file for this writer. 
        """
        return fileops.join_path(self._path, [DATAFILE_PATH])

    def get_solutions(self, problemNumber):
        """
        Get list of solution for specified problem
        """
        return self._solutions[problemNumber] if problemNumber in self._solutions else []

    def get_all_solutions(self):
        """
        Get list of all user completed solutions
        """
        return [problems for problemNumber, problems in self._solution.items()]

    @classmethod
    def load_from_path(cls, path):
        """
        Loads a writer and all their solutions from a specified path
        """
        loadedWriter = Writer(writerPath=path)

        # Check if writer directoroy exists. If not, return nothing
        if not fileops.exists(path, fileops.FileType.DIRECTORY):
            return None

        # Load the user data from the data file
        dataDictionary = fileops.get_json_dict(loadedWriter._get_datafile_path)

        # Populate the data if available
        # Load name
        if DATAFILE_NAME_FIELD in dataDictionary:
            loadedWriter.name = dataDictionary[DATAFILE_NAME_FIELD]

        # Load email
        if DATAFILE_EMAIL_FIELD in dataDictionary:
            loadedWriter.email = dataDictionary[DATAFILE_EMAIL_FIELD]

        # 
