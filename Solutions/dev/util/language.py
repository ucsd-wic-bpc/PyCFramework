################################################################################
# Filename: language.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     15 September 2015
#
# Contains the Language object, which corresponds to a single block in 
# languages.json
################################################################################
from util import fileops
from util.pathmapper import PathMapper
from util.variables import Variables
import subprocess

class ExecutionError(Exception):
    def __init__(self, message):
        self.message = message
        

class Language:
    NAME_KEY = 'language'
    COMPILE_EXTENSION_KEY = 'compileExtension'
    COMPILE_COMMAND_KEY = 'compileCommand'
    COMPILE_ARGS_KEY = 'compileArguments'
    RUN_EXTENSION_KEY = 'runExtension'
    RUN_COMMAND_KEY = 'runCommand'
    RUN_ARGS_KEY = 'runArguments'

    def __init__(self, languageName, compileExtension=None, compileCommand=None,
            compileArguments=None, runExtension=None, runCommand=None, 
            runArguments=None):
        self.name = languageName
        self._compileExtension = compileExtension
        self._compileCommand = compileCommand
        self._compileArguments = compileArguments
        self._runExtension = runExtension
        self._runCommand = runCommand
        self._runArguments = runArguments

    @classmethod
    def load_from_dict(cls, languageBlockDict: dict):
        """
        Loads a language object from an individual language block dictionary,
        following the format of languages.json

        :param languageBlockDict: A dictionary containing info for a language
        """
        languageObject = Language(
                languageBlockDict[cls.NAME_KEY] if cls.NAME_KEY in languageBlockDict else None,
                compileExtension=(languageBlockDict[cls.COMPILE_EXTENSION_KEY] 
                    if cls.COMPILE_EXTENSION_KEY in languageBlockDict else None),
                compileCommand=(languageBlockDict[cls.COMPILE_COMMAND_KEY]
                    if cls.COMPILE_COMMAND_KEY in languageBlockDict else None),
                compileArguments=(languageBlockDict[cls.COMPILE_ARGS_KEY]
                    if cls.COMPILE_ARGS_KEY in languageBlockDict else None),
                runExtension=(languageBlockDict[cls.RUN_EXTENSION_KEY]
                    if cls.RUN_EXTENSION_KEY in languageBlockDict else None),
                runCommand=(languageBlockDict[cls.RUN_COMMAND_KEY]
                    if cls.RUN_COMMAND_KEY in languageBlockDict else None),
                runArguments=(languageBlockDict[cls.RUN_ARGS_KEY]
                    if cls.RUN_ARGS_KEY in languageBlockDict else None))

        return languageObject

    def execute_code(self, codePath, inputContents):
        return AppliedLanguage.get_applied_language(codePath, self).execute_code(inputContents)

class AppliedLanguage(Language):
    # A language that's applied to a specific solution
    _appliedLanguages = {}

    def __init__(self, languageName, compileExtension=None, compileCommand=None,
            compileArguments=None, runExtension=None, runCommand=None, 
            runArguments=None, path=None):
        super().__init__(languageName, compileExtension, compileCommand,
                compileArguments, runExtension, runCommand, runArguments)
        self._path = path

    @classmethod
    def get_applied_language(cls, solutionPath, solutionLanguage):
        if solutionPath in cls._appliedLanguages:
            return cls._appliedLanguages[solutionPath]

        variableDictionary = {
                Variables.get_variable_key_name(Variables.NAME_FILENAME): fileops.get_basename(solutionPath),
                Variables.get_variable_key_name(Variables.NAME_FILENAME_LESS_EXT): fileops.get_basename_less_extension(solutionPath),
                Variables.get_variable_key_name(Variables.NAME_DIRECTORY): fileops.get_parent_dir(solutionPath)
                }

        cls._appliedLanguages[solutionPath] = AppliedLanguage(solutionLanguage.name,
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._compileExtension),
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._compileCommand),
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._compileArguments),
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._runExtension),
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._runCommand),
                cls._get_formatted_str_rec(variableDictionary, solutionLanguage._runArguments),
                solutionPath)

        return cls._appliedLanguages[solutionPath]

                
    @classmethod
    def _get_formatted_str_rec(cls, formatDict, string):
        if isinstance(string, str):
            return string.format(**formatDict)
        elif isinstance(string, list):
            for i in range(0, len(string)):
                string[i] = AppliedLanguage._get_formatted_str_rec(formatDict, string[i])
            return string

    def _compile_code(self):
        """
        Attempts to compile the code found at the given path

        Returns: The path of the compiled code object
        """
        compileCommand = [self._compileCommand]
        compileCommand.extend(self._compileArguments)
        if not subprocess.call(compileCommand) == 0:
            raise ExecutionError('Failed to compile')

        return fileops.get_path_with_changed_extension(self._path, 
                self._runExtension)

    def execute_code(self, inputContents):
        """
        Executes the code by first compiling it (if necessary), then running it,
        then returning the output or an ExecutionError if one occurred
        """
        if not self._compileCommand is None:
            self._path = self._compile_code()

        runCommand = [self._runCommand]
        runCommand.extend(self._runArguments)
        runCommand.append(str(inputContents))
        try:
            output = subprocess.check_output(runCommand).decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise ExecutionError('Error: Runtime Error\n{}'.format(e.output))

        return output[:-1]

class Languages:
    LANGUAGES_FILE = 'languages.json'
    _languagesDict = None

    @classmethod
    def load_languages(cls):
        """
        Loads the languages into cache from the languages file
        """
        if cls._languagesDict is None:
            cls._languagesDict = {}

        languagesItems = fileops.get_json_dict(cls.get_languages_filepath())
        for languageBlock in languagesItems['languages']:
            cls._languagesDict[Languages.get_prevalent_extension_from_block(languageBlock)] = (
                    Language.load_from_dict(languageBlock))

    @staticmethod
    def get_prevalent_extension_from_block(block):
        if Language.COMPILE_EXTENSION_KEY in block:
            return block[Language.COMPILE_EXTENSION_KEY]
        else:
            return block[Language.RUN_EXTENSION_KEY]
    
    @classmethod
    def is_prevalent_extension(cls, extension: str) -> bool:
        """
        Checks to see if a given extension belongs to a source file
        """
        if cls._languagesDict is None:
            cls.load_languages()

        return extension in cls._languagesDict

    @classmethod
    def get_languages_filepath(cls):
        """
        Gets the filepath of the languages file based on the path mapper
        """
        return fileops.join_path(PathMapper.get_config_path(), Languages.LANGUAGES_FILE)

    @classmethod
    def get_language_from_extension(cls, extension: str):
        """
        Gets the language object corresponding to the given extension
        """
        if cls._languagesDict is None:
            cls.load_languages()

        if extension in cls._languagesDict:
            return cls._languagesDict[extension]
        else:
            return None
