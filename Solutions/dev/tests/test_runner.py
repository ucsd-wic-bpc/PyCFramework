################################################################################
# Filename: test_runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     22 September 2015
#
# Contains tests for runner.py, the main executable script
################################################################################
import unittest
import runner
from io import StringIO

class TestRunner(unittest.TestCase):

    # USER STORY:
    # Mary wants to utilize PyCFramework. She doesnt know where to begin.
    # She types ./runner.py without arguments in hopes of a help message
    def test_can_be_run_directly(self):
        """
        Ensure runner.py can be run without typing `python` first
        """
        with open('runner.py') as openRunner:
            self.assertEquals(openRunner.readline()[:-1], '#!/usr/bin/env python3')

    def test_does_return_help_message_no_args(self):
        """
        Ensure providing no arguments provides a help message
        """
        output = StringIO()
        runner.main([], out=output)
        runnerOutput = output.getvalue().strip()
        self.assertIn('usage:', runnerOutput)

    # Sometimes Mary is advanced and uses the help option
    def test_does_print_help_with_h_option(self):
        """
        Ensure providing --h prints the help message
        """
        output = StringIO()
        runner.main(['--h'], out=output)
        runnerOutput = output.getvalue().strip()
        self.assertIn('usage:', runnerOutput)

    # After learning how to use the software, she wants to see the problems that
    # she has completed. However, she has not yet created her user. 
    # She types: ./runner.py --listWriter Mary
    # She receives: Error: Mary does not exist!
    def test_list_no_user_prints_error(self):
        """
        Ensure --listWriter with an invalid user prints an error
        """
        output = StringIO()
        runner.main(['--listWriter', 'cheesemonster'], out=output)
        runnerOutput = output.getvalue().strip()
        self.assertIn('Error: cheesemonster is an invalid Writer', runnerOutput)

    # She then creates the writer.
    # She types ./runner.py --createWriter Mary
    # She receives: No email specified
    def test_create_writer_needs_email(self):
        """
        Ensure --createWriter prints error if no email is provided
        """
        output = StringIO()
        runner.main(['--createWriter', '19571241'], out=output)
        runnerOutput = output.getvalue().strip()
        self.assertIn('Error: No email specified', runnerOutput)

    # She types ./runner.py --createWriter Mary --email mary@gmail.com
    # She receives: No name specified

    # She types ./runner.py --createWriter Mary --email mary@gmail.com 
    #    --name Mary
    # She receives no output. User created succesfully

    # Note that Mary should later be able to delete herself with
    # ./runner.py --deleteWriter Mary

    # Now Mary wants to test a single problem that she has completed
    # ./runner.py Mary 5
    # The problem is incorrect, so Mary receives a message indicating so
    # $ Incorrect Solution: Mary 5 Corner-Case

    # Mary wants to see the specifics of how she failed, so she runs with the 
    # --diff option
    # ./runner.py Mary 5 --diff
    # $ Incorrect Solution: Mary 5 Corner-Case
    #   <diff output>
