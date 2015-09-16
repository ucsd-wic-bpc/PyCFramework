################################################################################
# Filename: language.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     15 September 2015
#
# Contains the Language object, which corresponds to a single block in 
# languages.json
################################################################################

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

    @staticmethod
    def load_from_dict(languageBlockDict: dict):
        """
        Loads a language object from an individual language block dictionary,
        following the format of languages.json

        :param languageBlockDict: A dictionary containing info for a language
        """
        languageObject = Language(
                languageBlockDict[NAME_KEY] if NAME_KEY in languageBlockDict else None,
                compileExtension=(languageBlockDict[COMPILE_EXTENSION_KEY] 
                    if COMPILE_EXTENSION_KEY in languageBlockDict else None),
                compileCommand=(languageBlockDict[COMPILE_COMMAND_KEY]
                    if COMPILE_COMMAND_KEY in languageBlockDict else None),
                compileArguments=(languageBlockDict[COMPILE_ARGS_KEY]
                    if COMPILE_ARGS_KEY in languageBlockDict else None),
                runExtension=(languageBlockDict[RUN_EXTENSION_KEY]
                    if RUN_EXTENSION_KEY in languageBlockDict else None),
                runCommand=(languageBlockDict[RUN_COMMAND_KEY]
                    if RUN_COMMAND_KEY in languageBlockDict else None),
                runArguments=(languageBlockDict[RUN_ARGS_KEY]
                    if RUN_ARGS_KEY in languageBlockDict else None))

        return languageObject
