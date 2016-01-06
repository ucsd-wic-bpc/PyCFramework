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
from util.perror import PyCException

class Writer:
    DATAFILE_PATH = 'data.json'
    DATAFILE_NAME_FIELD = 'name'
    DATAFILE_EMAIL_FIELD = 'email'
    DATAFILE_LANGS_FIELD = 'languages'
    DATAFILE_ASSIGNED_PROBLEMS = 'assigned'

    def __init__(self, writerEmail='', writerName='', writerPath=''):
        self.name = writerName
        self.email = writerEmail
        self._path = writerPath
        self._solutions = {} 
        self.knownLanguages = {} # {language.name : language}
        self.assignedProblems = [] # [(problemNumber, language)]

    def __str__(self):
        solutionsString = ''
        for solution in self.get_all_solutions():
            solutionsString += '{}\n'.format(str(solution))

        return 'Directory: {}\nName: {}\nEmail: {}\nKnown Languages: {}\nAssigned Problems:{}\nSolutions: \n{}\n'.format(
                self._path, self.name, self.email, ', '.join(list(self.knownLanguages.keys())),
                ', '.join(['{} in {}'.format(item[0], item[1]) for item in sorted(self.assignedProblems)]),
                solutionsString)

    def _add_known_language(self, language):
        if not language.name in self.knownLanguages:
            self.knownLanguages[language.name] = language

    def _add_known_language_from_name(self, languageName):
        language = Languages.get_language_by_name(languageName)

        if language is None:
            raise PyCException('Error: {} is not a valid language'.format(languageName))

        self._add_known_language(language)

    def add_known_language(self, languageName):
        self._add_known_language_from_name(languageName)
        self._write_datafile()

    def add_known_language_from_list(self, languageNameList):
        if not isinstance(languageNameList, list):
            return self.add_known_language(languageNameList)

        for languageName in languageNameList:
            self._add_known_language_from_name(languageName)

        self._write_datafile()

    def clear_known_languages(self):
        self.knownLanguages = {}


    def clear_known_languages_and_save(self):
        self.clear_known_languages()
        self.save_changes()

    def knows_language(self, languageName):
        return languageName in self.knownLanguages

    def add_assigned_problem(self, problemNumber, languageName):
        self._add_assigned_problem( problemNumber, languageName)
        self._write_datafile()

    def _add_assigned_problem(self, problemNumber, languageName):
        if not (problemNumber, languageName) in self.assignedProblems:
            self.assignedProblems.append((problemNumber, languageName))

    def get_number_assigned_problems(self):
        return len(self.assignedProblems)

    def unassign_all_problems(self):
        self.assignedProblems = []
        self._write_datafile()

    def get_assigned_problems_not_started(self):
        notStarted = []

        for assignedProblem in self.assignedProblems:
            if not assignedProblem[0] in self._solutions:
                notStarted.append(assignedProblem)
                continue

            started = False
            for solution in self._solutions[assignedProblem[0]]:
                if solution.solutionLanguage.name == assignedProblem[1]:
                    started = True
                    break

            if not started:
                notStarted.append(assignedProblem)

        return sorted(notStarted)

    def create(self):
        if self._path is None or self._path == '':
            raise Exception('Cannot create writer without path')

        fileops.make(self._path, fileops.FileType.DIRECTORY)
        fileops.make(self._get_datafile_path(), fileops.FileType.FILE)
        Writers.add_writer(fileops.get_basename(self._path))
        self._write_datafile()

    """
    Updates the currently saved files corresponding to this writer.
    """
    def save_changes(self):
        if self._path is None or self._path == '':
            raise Exception('Cannot save writer without path')

        if not Writers.writer_exists(fileops.get_basename(self._path)):
            self.create()
        else:
            self._write_datafile()

    def delete(self):
        if self._path is None or self._path == '':
            raise Exception('Cannot delete writer without path')

        fileops.remove(self._path, fileops.FileType.DIRECTORY)
        Writers.delete_writer(fileops.get_basename(self._path))

    def _write_datafile(self):
        """
        Writes the datafile for this Writer to the filesystem
        """
        datafileDict = {self.DATAFILE_NAME_FIELD : self.name,
                        self.DATAFILE_EMAIL_FIELD: self.email,
                        self.DATAFILE_LANGS_FIELD: list(self.knownLanguages.keys()),
                        self.DATAFILE_ASSIGNED_PROBLEMS: [[item[0], item[1]] for item in self.assignedProblems]}
        fileops.write_json_dict(self._get_datafile_path(), datafileDict)

    def write_file(self, filename, data):
        """
        Writes the given file to the user's directory, overwriting if exists
        """
        filePath = self._get_sub_path(filename)
        with open(filePath, 'w+') as openFile:
            openFile.write(data)

    def append_file(self, filename, data):
        filePath = self._get_sub_path(filename)
        with open(filePath, 'a+') as openFile:
            openFile.write('{}\n'.format(data))

    def delete_file(self, filename):
        filePath = self._get_sub_path(filename)
        fileops.remove(filePath, fileops.FileType.FILE)

    def _get_datafile_path(self) -> str:
        """
        Return the path of the data file for this writer. 
        """
        return self._get_sub_path(self.DATAFILE_PATH)

    def _get_sub_path(self, path) -> str:
        return fileops.join_path(self._path, path)

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
        if not int(solution.problemNumber) in self._solutions:
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

        # Load languages
        if cls.DATAFILE_LANGS_FIELD in dataDictionary:
            for languageName in dataDictionary[cls.DATAFILE_LANGS_FIELD]:
                loadedWriter._add_known_language_from_name(languageName)

        # Load assigned
        if cls.DATAFILE_ASSIGNED_PROBLEMS in dataDictionary:
            for assignedProblem in dataDictionary[cls.DATAFILE_ASSIGNED_PROBLEMS]:
                loadedWriter._add_assigned_problem(assignedProblem[0], assignedProblem[1])

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

class Writers:
    """
    Handle the .writers.json config file
    """
    JSON_FILE = '.writers.json'
    writers = None

    @classmethod
    def add_writer(cls, writerName):
        if cls.writers is None:
            cls._load_from_config()

        if not writerName in cls.writers:
            cls.writers.append(writerName)

        cls._write_file()

    @classmethod
    def delete_writer(cls, writerName):
        if cls.writers is None:
            cls._load_from_config()

        if writerName in cls.writers:
            cls.writers.remove(writerName)

        cls._write_file()

    @classmethod
    def get_all_writers(cls):
        if cls.writers is None:
            cls._load_from_config()

        writerList = []
        for writerName in cls.writers:
            writer = Writer.load_from_folder(writerName)
            if writer is None:
                raise PyCException('Error: Writer {} does not have a folder'.format(path))
            else:
                writerList.append(writer)

        return writerList

    @classmethod
    def get_all_writer_names(cls):
        if cls.writers is None:
            cls._load_from_config()

        return cls.writers

    @classmethod
    def _write_file(cls):
        if cls.writers is None:
            cls._load_from_config()

        fileops.write_json_dict(cls._get_config_path(), cls.writers)

    @classmethod
    def _get_config_path(cls):
        return fileops.join_path(PathMapper._rootPath, cls.JSON_FILE)

    @classmethod
    def _load_from_config(cls):
        loadedContents = fileops.get_json_dict(cls._get_config_path())
        if isinstance(loadedContents, list):
            cls.writers = loadedContents
        else:
            cls.writers = []

    @classmethod
    def writer_exists(cls, writerName):
        if cls.writers is None:
            cls._load_from_config()

        return writerName in cls.writers
