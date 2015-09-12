################################################################################
# Filename: test_writer.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains tests for util/writer.py
################################################################################
import unittest
from util.writer import Writer

class TestWriter(unittest.TestCase):
    
    def test_init(self):
        """
        Ensure Writer.__init__ sets instance variables properly
        """
        testWriter = Writer(writerEmail='email', writerName='name', writerPath='path')
        self.assertEquals(testWriter.name, 'name')
        self.assertEquals(testWriter.email, 'email')
        self.assertEquals(testWriter._path, 'path')
        self.assertEquals(testWriter._solutions, {})

    @unittest.mock.patch('util.writer.fileops')
    def test_get_datafile_path(self, mock_writer_fileops):
       """
       Ensure Writer._get_datafile_path properly delegates to fileops.join_path
       """
       testWriter = Writer(writerPath='path')
       mock_writer_fileops.join_path.return_value = 'delegation'
       self.assertEquals(testWriter._get_datafile_path(), 'delegation')
       mock_writer_fileops.join_path.assert_called_with('path', Writer.DATAFILE_PATH)

    def test_get_solutions(self):
        """
        Ensure Writer.get_solutions returns a list pertaining to the provided problem number
        """
        testWriter = Writer()
        testWriter._solutions = { 1 : ['sol1', 'sol2', 'sol3'],
                                  2 : ['sol4', 'sol5', 'sol6'],
                                  3 : ['sol7', 'sol8', 'sol9'] 
                                }

        # Ensure correct list is returned
        self.assertEquals(testWriter.get_solutions(2), ['sol4', 'sol5', 'sol6'])
        
        # Ensure invalid number returns an empty list
        self.assertEquals(testWriter.get_solutions(5), [])

    def test_get_all_solutions(self):
        """
        Ensure Writer.get_all_solutions returns a list of all solutions
        """
        testWriter = Writer()

        # Ensure with no solutions an empty list is returned
        self.assertEquals(testWriter.get_all_solutions(), [])

        testWriter._solutions = { 1 : ['sol1', 'sol2', 'sol3'],
                                  2 : ['sol4', 'sol5', 'sol6'],
                                  3 : ['sol7', 'sol8', 'sol9'] 
                                }

        # Ensure all solutions are provided
        self.assertEquals(testWriter.get_all_solutions(), ['sol1', 'sol2', 'sol3',
            'sol4', 'sol5', 'sol6', 'sol7', 'sol8', 'sol9'])

