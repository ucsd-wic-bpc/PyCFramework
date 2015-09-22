################################################################################
# Filename: test_runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     22 September 2015
#
# Contains tests for runner.py, the main executable script
################################################################################
import unittest


class TestRunner(unittest.TestCase):

    # USER STORY:
    # Mary wants to utilize PyCFramework. She doesnt know where to begin.
    # She types ./runner.py without arguments in hopes of a help message
    # Mary may also be advanced on some days, where she types -h for help


    # After learning how to use the software, she wants to see the problems that
    # she has completed. However, she has not yet created her user. 
    # She types: ./runner.py --listWriter Mary
    # She receives: Error: Mary does not exist!

    # She then creates the writer.
    # She types ./runner.py --createWriter Mary
    # She receives: No email specified

    # She types ./runner.py --createWriter Mary --email mary@gmail.com
    # She receives: No name specified

    # She types ./runner.py --createWriter Mary --email mary@gmail.com 
    #    --name Mary
    # She receives no output. User created succesfully

    # Note that Mary should later be able to delete herself with
    # ./runner.py --deleteWriter Mary
