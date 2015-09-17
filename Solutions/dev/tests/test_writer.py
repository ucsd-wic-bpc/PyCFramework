################################################################################
# Filename: test_writer.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     12 September 2015
#
# Contains tests for util/writer.py
################################################################################
import unittest
from util.writer import Writer
from util.solution import Solution
from util.language import Languages
from unittest import mock

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

    def test_add_solution(self):
        """
        Ensure Writer.add_solution works as expected
        """
        # Multiple solutions with the same problem number should be appended
        mockedSolution = mock.MagicMock()
        mockedSolution.problemNumber = 5
        testWriter = Writer()
        testWriter._add_solution(mockedSolution)
        testWriter._add_solution(mockedSolution)
        self.assertEqual(testWriter._solutions, {5: [mockedSolution, mockedSolution]})

        # Different problem numbers should go to different dict sections
        mockedSecondSolution = mock.MagicMock()
        mockedSecondSolution.problemNumber = 7
        testWriter._add_solution(mockedSecondSolution)
        self.assertEqual(testWriter._solutions, {5: [mockedSolution, mockedSolution],
                                                 7: [mockedSecondSolution]})

    @mock.patch.object(Languages, 'is_prevalent_extension')
    @mock.patch.object(Writer, '_add_solution')
    @mock.patch.object(Solution, 'load_from_path')
    @mock.patch.object(Solution, 'is_solution_file')
    @mock.patch.object(Writer, '_get_datafile_path')
    @mock.patch('util.writer.fileops')
    def test_load_from_path(self, mocked_fileops, mocked_writer_get_datafile,
            mocked_solution_is_solution_file, mocked_solution_load_path,
            mocked_writer_add_sol, mocked_lang_is_prevalent_ext):
        """
        Ensure Writer.load_from_path properly assembles a Writer object
        """
        # If the writer dir does not exist, writer should be none
        mocked_fileops.exists.return_value = False
        mocked_fileops.FileType = mock.MagicMock(DIRECTORY='lol')
        self.assertEqual(Writer.load_from_path('badPath'), None)
        mocked_fileops.exists.assert_called_with('badPath', 'lol')

        # If the writer dir does exist, a writer should be created
        mocked_fileops.exists.return_value = True
        mocked_writer_get_datafile.return_value = 'dataPath'
        mocked_fileops.get_json_dict.return_value = {'name' : 'brandon',
                                                     'email': 'brandon@bz.com'}
        mocked_fileops.get_files_in_dir.return_value = ['file1', 'file2']
        mocked_solution_is_solution_file.return_value = True
        mocked_lang_is_prevalent_ext.return_value = True
        mocked_solution_load_path.return_value = 'sol'

        newWriter = Writer.load_from_path('path')
        mocked_fileops.exists.assert_called_with('path', 'lol')
        mocked_writer_get_datafile.assert_called_with()
        mocked_fileops.get_json_dict.assert_called_with('dataPath')
        mocked_fileops.get_files_in_dir.assert_called_with('path')
        mocked_solution_is_solution_file.assert_any_call('file1')
        mocked_solution_is_solution_file.assert_any_call('file2')
        mocked_solution_load_path.assert_any_call('file1')
        mocked_solution_load_path.assert_any_call('file2')
        mocked_writer_add_sol.assert_called_with('sol')
        self.assertEqual(newWriter.name, 'brandon')
        self.assertEqual(newWriter.email, 'brandon@bz.com')
