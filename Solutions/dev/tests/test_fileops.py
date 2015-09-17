################################################################################
# Filename: test_fileops.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     September 08, 2015
#
# Contains tests for the fileops class at util/fileops.py
################################################################################
import unittest.mock
import util.fileops
from util.fileops import FileType
import unittest
import os


class TestFileOps(unittest.TestCase):

    @unittest.mock.patch('util.fileops.os.path')
    def test_exists(self, mocked_os_path):
        """
        Ensure fileops.exists works as expected
        """
        # Ensure a nonexistent file returns false
        mocked_os_path.exists.return_value = False
        self.assertFalse(util.fileops.exists('path', 0))
        mocked_os_path.exists.assert_called_with('path')

        # Ensure an existing file which is a file returns true
        mocked_os_path.exists.return_value = True
        mocked_os_path.isfile.return_value = True
        self.assertTrue(util.fileops.exists('path', FileType.FILE))
        mocked_os_path.exists.assert_called_with('path')
        mocked_os_path.isfile.assert_called_with('path')

        # Ensure a file that is not a file returns False
        mocked_os_path.isfile.return_value = False
        self.assertFalse(util.fileops.exists('path', FileType.FILE))
        mocked_os_path.exists.assert_called_with('path')
        mocked_os_path.isfile.assert_called_with('path')

        # Ensure an existing file which is a dir returns true
        mocked_os_path.isdir.return_value = True
        self.assertTrue(util.fileops.exists('path', FileType.DIRECTORY))
        mocked_os_path.exists.assert_called_with('path')
        mocked_os_path.isdir.assert_called_with('path')

        # Ensure an existing file which is not a dir returns false
        mocked_os_path.isdir.return_value = False
        self.assertFalse(util.fileops.exists('path', FileType.DIRECTORY))
        mocked_os_path.exists.assert_called_with('path')
        mocked_os_path.isdir.assert_called_with('path')

    @unittest.mock.patch('util.fileops.json')
    @unittest.mock.patch('util.fileops.open', create=True)
    @unittest.mock.patch('util.fileops.exists')
    def test_get_json_dict(self, mocked_fileops_exists, mocked_fileops_open,
            mocked_fileops_json):
        """
        Ensure fileops.get_json_dict works as expected (With mocked json lib)
        """
        # Ensure a nonexistent file returns an empty dict
        mocked_fileops_exists.return_value = False
        self.assertEquals(util.fileops.get_json_dict('path'), {})
        mocked_fileops_exists.assert_called_with('path', FileType.FILE)

        # Ensure an existing file returns a valid dictionary
        mocked_fileops_exists.return_value = True
        mockedFile = unittest.mock.MagicMock()
        mockedFileEnter = unittest.mock.MagicMock()
        mockedFileEnter.read.return_value = 'helloWorld'
        mockedFile.__enter__.return_value = mockedFileEnter
        mocked_fileops_open.return_value = mockedFile
        mocked_fileops_json.loads.return_value = 'babaloo'
        util.fileops.get_json_dict('path')
        self.assertEquals(util.fileops.get_json_dict('path'), 'babaloo')
        mocked_fileops_exists.assert_called_with('path', FileType.FILE)
        mocked_fileops_open.assert_called_with('path')
        mocked_fileops_json.loads.assert_called_with('helloWorld')
    
    @unittest.mock.patch('util.fileops.open', create=True)
    @unittest.mock.patch('util.fileops.exists')
    def test_get_json_dict_unmocked(self, mocked_fileops_exists, mocked_fileops_open):
        """
        Ensure fileops.get_json_dict works as expected (Using json lib)
        """
        mocked_fileops_exists.return_value = True
        mockedFile = unittest.mock.MagicMock()
        mockedFileEnter = unittest.mock.MagicMock()
        mockedFileEnter.read.return_value = '{"entry1" : ["listitem1","listitem2"]}'
        mockedFile.__enter__.return_value = mockedFileEnter
        mocked_fileops_open.return_value = mockedFile
        self.assertEquals(util.fileops.get_json_dict('path'), {'entry1' : 
                                                                [ 'listitem1',
                                                                  'listitem2'
                                                                ]
                                                              })
        mocked_fileops_exists.assert_called_with('path', FileType.FILE)
        mocked_fileops_open.assert_called_with('path')

    @unittest.mock.patch('util.fileops.os.path')
    def test_join_path(self, mocked_fileops_os_path):
        """
        Ensure fileops.join_path works as expected (Using mocked path.join)
        """
        mocked_fileops_os_path.join.return_value = 'ahooby'
        self.assertEquals(util.fileops.join_path('path', 'path1', 'path2'), 'ahooby')
        mocked_fileops_os_path.joinassert_called_with('path', 'path1', 'path2')

    def test_join_path_unmocked(self):
        """
        Ensure fileops.join_path works as expected when os.path.join is not mocked
        """
        self.assertEquals(util.fileops.join_path('path1', 'path2'), 
                os.path.join('path1', 'path2'))
        self.assertEquals(util.fileops.join_path('path1', 'path2', 'path3'),
                os.path.join('path1', 'path2', 'path3'))

    @unittest.mock.patch('util.fileops.os.path')
    @unittest.mock.patch('util.fileops.os')
    def test_get_files_in_dir_nonrecursive(self, mocked_fileops_os, mocked_fileops_os_path):
        """
        Ensure a nonrecursive fileops.get_files_in_dir returns only the files in the parent dir
        """
        mocked_fileops_os.listdir.return_value = ['file1', 'file2', 'file3', 'dir1']
        mocked_fileops_os_path.isfile.side_effect = lambda fileName: False if fileName == 'dir1' else True
        self.assertEquals(util.fileops.get_files_in_dir('path'), ['file1', 'file2', 'file3'])
        mocked_fileops_os.listdir.assert_called_with('path')
        for fileItem in ['file1', 'file2', 'file3', 'dir1']:
            mocked_fileops_os_path.isfile.assert_any_call(fileItem)

    @unittest.mock.patch('util.fileops.os.path')
    @unittest.mock.patch('util.fileops.os')
    def test_get_files_in_dir_recursive(self, mocked_fileops_os, mocked_fileops_os_path):
        """
        Ensure a recursive fileops.get_files_in_dir returns files in top dir and children dirs
        """
        mocked_fileops_os.listdir.side_effect = lambda path: (['file1', 'file2', 'file3', 'dir1'] if path == 'path'
                                                        else ['file4', 'file5', 'file6'])
        mocked_fileops_os_path.isfile.side_effect = lambda fileName: False if fileName == 'dir1' else True
        mocked_fileops_os_path.isdir.side_effect = lambda fileName: True if fileName == 'dir1' or fileName == 'path' else False
        self.assertEquals(util.fileops.get_files_in_dir('path', recursive=True), 
                ['file1', 'file2', 'file3', 'file4', 'file5', 'file6'])
        mocked_fileops_os.listdir.assert_any_call('path')
        mocked_fileops_os.listdir.assert_any_call('dir1')
        for fileItem in ['file1', 'file2', 'file3', 'dir1', 'file4', 'file5', 'file6']:
            mocked_fileops_os_path.isfile.assert_any_call(fileItem)

    def test_get_basename_less_extension(self):
        """
        Ensure fileops.get_basename_less_extension works as intended
        """
        self.assertEquals(util.fileops.get_basename_less_extension('/home/brandon/test/test.py'),
                'test')
        self.assertEquals(util.fileops.get_basename_less_extension('poopies.html'),
                'poopies')
        self.assertEquals(util.fileops.get_basename_less_extension('raw'), 'raw')

    def test_get_basename(self):
        """
        Ensure fileops.get_basename works as intended
        """
        self.assertEquals(util.fileops.get_basename('/home/brandon/test/test.py'),
                'test.py')
        self.assertEquals(util.fileops.get_basename('poopies.html'),
                'poopies.html')
        self.assertEquals(util.fileops.get_basename('raw'), 'raw')
        self.assertEquals(util.fileops.get_basename('home/brandon/test'), 'test')

    def test_get_parent_dir(self):
        """
        Ensure fileops.get_parent_dir works as intended
        """
        self.assertEquals(util.fileops.get_parent_dir('/home/brandon/test/test.py'),
                '/home/brandon/test')
        self.assertEquals(util.fileops.get_parent_dir('test.html'), '')
