################################################################################
# Filename: test_language.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     17 September 2015
#
# Tests to ensure the functionality of util/language.py
################################################################################
import unittest
from util.language import Language, Languages
from unittest import mock
from util.pathmapper import PathMapper
import os

class TestLanguage(unittest.TestCase):

    def test_init(self):
        """
        Ensure Language.__init__ sets instance vars properly
        """
        testLanguage = Language('name', compileExtension='ext', 
                compileCommand='cc', compileArguments='ca', runExtension='re',
                runCommand='rc', runArguments='ra')
        self.assertEqual(testLanguage.name, 'name')
        self.assertEqual(testLanguage._compileExtension, 'ext')
        self.assertEqual(testLanguage._compileCommand, 'cc')
        self.assertEqual(testLanguage._compileArguments, 'ca')
        self.assertEqual(testLanguage._runExtension, 're')
        self.assertEqual(testLanguage._runCommand, 'rc')
        self.assertEqual(testLanguage._runArguments, 'ra')

    def test_load_from_dict(self):
        """
        Ensure Language.load_from_dict properly populates information
        """
        languageDictionary = {'language' : 'RUST',
                              'compileExtension' : 'rs',
                              'compileCommand' : 'rustc',
                              'compileArguments' : [],
                              'runExtension' : '',
                              'runCommand' : '{directory}/{fileNameWoExtension}',
                              'runArguments' : []
                             }
        testLanguage = Language.load_from_dict(languageDictionary)
        self.assertEqual(testLanguage.name, 'RUST')
        self.assertEqual(testLanguage._compileExtension, 'rs')
        self.assertEqual(testLanguage._compileCommand, 'rustc')
        self.assertEqual(testLanguage._compileArguments, [])
        self.assertEqual(testLanguage._runExtension, '')
        self.assertEqual(testLanguage._runCommand, '{directory}/{fileNameWoExtension}')
        self.assertEqual(testLanguage._runArguments, [])

class TestLanguages(unittest.TestCase):

    def tearDown(self):
        """
        Relinquish any languagesDict assignments
        """
        Languages._languagesDict = None

    def test_globals(self):
        """
        Ensure Languages globals are not bad
        """
        self.assertNotEqual(Languages.LANGUAGES_FILE, None)
        self.assertEqual(Languages._languagesDict, None)

    @mock.patch.object(Language, 'load_from_dict')
    @mock.patch.object(Languages, 'get_prevalent_extension_from_block')
    @mock.patch.object(Languages, 'get_languages_filepath')
    @mock.patch('util.language.fileops')
    def test_load_languages(self, mocked_language_fileops, 
            mocked_languages_get_filepath, mocked_get_prev_extension,
            mocked_language_load_from_dict):
        """
        Ensure Languages.load_languages properly delegates to Language's load from dict
        """
        mocked_language_fileops.get_json_dict.return_value = {
                                                            'languages' : [
                                                                        { 'block' : 1 },
                                                                        { 'block' : 2 }
                                                                          ]
                                                             }
        mocked_languages_get_filepath.return_value = 'path'
        mocked_get_prev_extension.side_effect = lambda x : 'ext1' if x == { 'block' : 1} else 'ext2'
        mocked_language_load_from_dict.return_value = 'haha'


        Languages.load_languages()
        self.assertEqual(Languages._languagesDict, {'ext1' : 'haha', 'ext2' : 'haha'})
        mocked_language_fileops.get_json_dict.assert_called_with('path')
        mocked_get_prev_extension.assert_called_any({'block' : 1})
        mocked_get_prev_extension.assert_called_any({'block' : 2})
        mocked_language_load_from_dict.assert_called_any({'block' : 1})
        mocked_language_load_from_dict.assert_called_any({'block' : 2})

    def test_get_prev_extension_from_block(self):
        """
        Ensure Languages.get_prevalent_extension_from_block works as intended
        """
        block = {'compileExtension' : 'cpp',
                 'runExtension'     : 'o'}
        self.assertEqual(Languages.get_prevalent_extension_from_block(block), 'cpp')

        block = { 'runExtension'     : 'o'}
        self.assertEqual(Languages.get_prevalent_extension_from_block(block), 'o')

        block = {'compileExtension' : 'cpp'}
        self.assertEqual(Languages.get_prevalent_extension_from_block(block), 'cpp')

    @mock.patch.object(PathMapper, 'get_config_path')
    def test_get_languages_filepath(self, mocked_get_config_path):
        """
        Ensure Languages.get_languages_filepath properly delegates to PathMapper
        """
        mocked_get_config_path.return_value = 'confPath'
        self.assertEqual(Languages.get_languages_filepath(), os.path.join(
            'confPath', Languages.LANGUAGES_FILE))

    @mock.patch.object(Languages, 'load_languages')
    def test_get_language_from_extension(self, mocked_load_languages):
        """
        Ensure Languages.get_language_from_extension properly gets a language from ext
        """
        Languages._languagesDict = None

        def populateDict():
            Languages._languagesDict = {'ext1' : 'lang1', 'ext2' : 'lang2'}
        mocked_load_languages.side_effect = populateDict

        self.assertEqual(Languages.get_language_from_extension('ext1'), 'lang1')
        mocked_load_languages.assert_called_with()

        self.assertEqual(Languages.get_language_from_extension('ext3'), None)
