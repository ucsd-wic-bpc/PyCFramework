################################################################################
# Filename: test_pathmapper.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     17 September 2015
#
# Contains tests for util/pathmapper.py
################################################################################
import unittest
from unittest import mock
from util.pathmapper import PathMapper

class TestPathMapper(unittest.TestCase):

    def test_globals(self):
        """
        Ensure PathMapper globals are not misvalued
        """
        self.assertNotEqual(PathMapper.CONFIG_DIR, None)

    def test_set_root_path(self):
        """
        Ensure PathMapper.set_root_path correctly sets root path
        """
        PathMapper.set_root_path('rootPath')
        self.assertEqual(PathMapper._rootPath, 'rootPath')

    @mock.patch('util.pathmapper.fileops')
    def test_get_config_path(self, mocked_pathmapper_fileops):
        """
        Ensure Pathmapper.get_config_path properly delegates to fileops
        """
        mocked_pathmapper_fileops.join_path.return_value = 'hello'
        self.assertEqual(PathMapper.get_config_path(), 'hello')
        mocked_pathmapper_fileops.join_path.assert_called_with(PathMapper._rootPath, 
                PathMapper.CONFIG_DIR)

