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

class Language:
    _languagesCache = None # A languages cache mapping extension to Language

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
            cls._languagesDict[Languages.get_prevelent_extension_from_block(languageBlock)] = (
                    Language.load_from_dict(languageBlock))

    @staticmethod
    def get_prevelent_extension_from_block(block):
        if Language.COMPILE_EXTENSION_KEY in block:
            return block[Language.COMPILE_EXTENSION_KEY]
        else:
            return block[Language.RUN_EXTENSION_KEY]
    
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
