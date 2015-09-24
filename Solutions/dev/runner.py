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
import os
from util.pathmapper import PathMapper
from util.writer import Writer


def parse_arguments(arguments, output=sys.stdout):
    # Define a custom class that prints help to the output
    class customArgParse(argparse.ArgumentParser):

        def __init__(self, **kwargs):
            super(customArgParse, self).__init__(kwargs, add_help=False)

        # Override to print help to output
        def print_help(self, file=None):
            self._print_message(self.format_help(), output)

        def print_usage(self, file=None):
            self._print_message(self.format_usage(), output)

        # Override to print help if invalid arg is provided
        def error(self, message):
            output.write('Error: {0}\n'.format(message))
            self.print_help()
            return

    argParser = customArgParse(description='An interface for a Programming Competition')
    argParser.add_argument('--name', help='The name of the writer being operated on')
    argParser.add_argument('--email', help='The email of the writer being operated on')
    argParser.add_argument('--listWriter', help='List the problems that a writer has completed')
    argParser.add_argument('--help', action='store_true')

    if len(arguments) == 0:
        argParser.print_help()
        return None
    else:
        args = argParser.parse_args(arguments)
        if args.help:
            argParser.print_help()
            return

        return args

def list_writer(writerFolder, output=sys.stdout):
    writerObject = Writer.load_from_folder(writerFolder)
    if writerObject is None:
        output.write('Error: {} is an invalid Writer\n'.format(writerFolder))
        return 0
    else:
        output.write('Folder: {}\nName: {}\nEmail: {}\nSolutions:\n'.format(
            writerFolder, writerObject.name, writerObject.email))
        for solution in writerObject.get_all_solutions():
            output.write('{}\n'.format(str(solution)))

def main(arguments, out=sys.stdout):
    args = parse_arguments(arguments, output=out)
    if args is None:
        return 0

    PathMapper.set_root_path(os.path.dirname(os.path.abspath(__name__)))
    if args.listWriter:
        list_writer(args.listWriter, output=out)
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
