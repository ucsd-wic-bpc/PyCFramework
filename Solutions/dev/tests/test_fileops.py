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
