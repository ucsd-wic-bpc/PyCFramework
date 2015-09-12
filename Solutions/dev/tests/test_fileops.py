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
        Ensure fileops.get_json_dict works as expected
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

    @unittest.mock.patch('util.fileops.os.path')
    def test_join_path(self, mocked_fileops_os_path):
        """
        Ensure fileops.join_path works as expected
        """
        mocked_fileops_os_path.join.return_value = 'ahooby'
        self.assertEquals(util.fileops.join_path('path', 'path1', 'path2'), 'ahooby')
        mocked_fileops_os_path.joinassert_called_with('path', 'path1', 'path2')

