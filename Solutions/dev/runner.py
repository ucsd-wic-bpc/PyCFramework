#!/usr/bin/env python3

################################################################################
# Filename: runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     24 September 2015
#
# Contains the executable logic for PyCFramework
################################################################################
import argparse
import sys


def parse_arguments(arguments, output=sys.stdout):
    # Define a custom class that prints help to the output
    class customArgParse(argparse.ArgumentParser):

        # Override to print help to output
        def print_help(self, file=None):
            self._print_message(self.format_help(), output)

        # Override to print help if invalid arg is provided
        def error(self, message):
            output.write('Error: {0}'.format(message))
            self.print_help()
            return

    argParser = customArgParse(description='An interface for a Programming Competition')
    argParser.add_argument('--name', help='The name of the writer being operated on')
    argParser.add_argument('--email', help='The email of the writer being operated on')

    if len(arguments) == 0:
        argParser.print_help()
    else:
        argParser.parse_args()


def main(arguments, out=sys.stdout):
    parse_arguments(arguments, output=out)




if __name__ == '__main__':
    sys.exit(main(sys.argv[-1]))
