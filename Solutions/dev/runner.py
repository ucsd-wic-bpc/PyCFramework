#!/usr/bin/env python3

################################################################################
# Filename: runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     24 September 2015
#
# Contains the executable logic for PyCFramework
################################################################################

# TODO: Add in 'perr'-like functionality, which makes functions return whether
# or not they errd and set a global message string. Maybe make a separate
# 'perror' like module

import argparse
import sys
import os
from util.pathmapper import PathMapper
from util.writer import Writer
from util.perror import PyCException

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
    argParser.add_argument('--createWriter', help='Create a new writer with specified info')
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

def get_writer_details(writerFolder):
    writerObject = Writer.load_from_folder(writerFolder)
    if writerObject is None:
        raise PyCException('Error: {} is an invalid Writer\n'.format(writerFolder))
    else:
        return str(writerObject)

def create_writer(writerFolder, writerName, writerEmail):
    if writerEmail is None:
        raise PyCException('Error: No email specified')

    if writerName is None:
        raise PyCException('Error: No name specified')

def handle_args(arguments, output=sys.stdout):
    # If arguments is None, only the help flag was provided
    if arguments is None:
        return

    if arguments.listWriter:
        details = get_writer_details(arguments.listWriter)
        for detail in details:
            output.write(detail)

    elif arguments.createWriter:
        create_writer(arguments.createWriter, arguments.name, arguments.email)


def main(arguments, out=sys.stdout):
    # Set the path
    PathMapper.set_root_path(os.path.dirname(os.path.abspath(__name__)))

    try:
        handle_args(parse_arguments(arguments, output=out), output=out)
    except PyCException as e:
        out.write(e.message)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
