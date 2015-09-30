################################################################################
# Filename: writer.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     30 August 2015
# 
# This file contains all information pertaining to solution writers
################################################################################
from util import fileops
from util.solution import Solution
from util.language import Languages
from util.pathmapper import PathMapper

class Writer:
    DATAFILE_PATH = 'data.json'
    DATAFILE_NAME_FIELD = 'name'
    DATAFILE_EMAIL_FIELD = 'email'

    def __init__(self, writerEmail='', writerName='', writerPath=''):
        self.name = writerName
        self.email = writerEmail
        self._path = writerPath
        self._solutions = {} 

    def __str__(self):
        solutionsString = ''
        for solution in self.get_all_solutions():
            solutionsString += '{}\n'.format(str(solution))

        return 'Directory: {}\nName: {}\nEmail: {}\nSolutions: \n{}\n'.format(
                self._path, self.name, self.email, solutionsString)

    def create(self):
        if self._path is None or self._path == '':
            raise Exception('Cannot create writer without path')

        fileops.make(self._path, fileops.FileType.DIRECTORY)
        fileops.make(self._get_datafile_path(), fileops.FileType.FILE)
        self._write_datafile()

    def delete(self):
        if self._path is None or self._path == '':
            raise Exception('Cannot delete writer without path')

        fileops.remove(self._path, fileops.FileType.DIRECTORY)

    def _write_datafile(self):
        """
        Writes the datafile for this Writer to the filesystem
        """
        datafileDict = {self.DATAFILE_NAME_FIELD : self.name,
                        self.DATAFILE_EMAIL_FIELD: self.email}
        fileops.write_json_dict(self._get_datafile_path(), datafileDict)

    def _get_datafile_path(self) -> str:
        """
        Return the path of the data file for this writer. 
        """
        return fileops.join_path(self._path, self.DATAFILE_PATH)

    def get_solutions(self, problemNumber: int) -> list:
        """
        Get list of solution for specified problem
        """
        return self._solutions[problemNumber] if problemNumber in self._solutions else []

    def get_all_solutions(self) -> list:
        """
        Get list of all user completed solutions
        """
        totalSolutions = []
        for solutionList in [self._solutions[problemNumber] for problemNumber in sorted(self._solutions)]:
            totalSolutions.extend(solutionList)

        return totalSolutions

    def _add_solution(self, solution):
        """
        Add a provided solution to the solution list
        """
        if not solution.problemNumber in self._solutions:
            self._solutions[int(solution.problemNumber)] = [solution]
        else:
            self._solutions[int(solution.problemNumber)].append(solution)

    @classmethod
    def load_from_path(cls, path):
        """
        Loads a writer and all their solutions from a specified path
        """
        # Check if writer directoroy exists. If not, return nothing
        if not fileops.exists(path, fileops.FileType.DIRECTORY):
            return None

        loadedWriter = Writer(writerPath=path)

        # Load the user data from the data file
        dataDictionary = fileops.get_json_dict(loadedWriter._get_datafile_path())

        # Populate the data if available
        # Load name
        if cls.DATAFILE_NAME_FIELD in dataDictionary:
            loadedWriter.name = dataDictionary[cls.DATAFILE_NAME_FIELD]

        # Load email
        if cls.DATAFILE_EMAIL_FIELD in dataDictionary:
            loadedWriter.email = dataDictionary[cls.DATAFILE_EMAIL_FIELD]

        # Load all solutions
        for possibleSolution in fileops.get_files_in_dir(path):
            if Solution.is_solution_file(possibleSolution):
                if not Languages.is_prevalent_extension(fileops.get_extension(possibleSolution)):
                    continue

                solutionObject = Solution.load_from_path(possibleSolution)
                loadedWriter._add_solution(solutionObject)

        return loadedWriter

    @classmethod
    def load_from_folder(cls, folderName):
        """
        Loads a writer from their folder utilizing the pathmapper
        """
        return cls.load_from_path(fileops.join_path(PathMapper._rootPath, folderName))

