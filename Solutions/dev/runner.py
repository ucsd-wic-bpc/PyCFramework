#!/usr/bin/env python3

################################################################################
# Filename: runner.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     24 September 2015
#
# Contains the executable logic for PyCFramework
################################################################################
import sys
import os
import argparse
from util.pathmapper import PathMapper
from util.perror import PyCException
from util.pcargparse import PCArgParseFactory
from util.subparsers import writers as writersSubparser
from util.subparsers import test as testSubparser
from util.subparsers import package as packageSubparser

def parse_arguments(arguments, output=sys.stdout):
    argParser = PCArgParseFactory.get_argument_parser(output)
    # Create a base parser to handle all the generic flags
    baseParser = argparse.ArgumentParser(add_help=False)
    baseParser.add_argument('--writer', help='The writer to operate on')
    baseParser.add_argument('--name', help='The name of the writer being operated on')
    baseParser.add_argument('--email', help='The email of the writer being operated on')
    baseParser.add_argument('--language', nargs='+', help='The name of the language being operated on')
    baseParser.add_argument('--problems', nargs='+', help='The number of the problem to operate on')
    baseParser.add_argument('--verbose', action='store_true', help='Display verbose output')
    argParser = argparse.ArgumentParser(parents=[baseParser], add_help=False)
    argParser.add_argument('--help', action='store_true')
    argParser.add_argument('--diff', action='store_true', help='Show the diff of incorrect solutions')
    argParser.add_argument('--file', action='store_true', help='Save outputs to file')
    subparsers = argParser.add_subparsers()
    writersSubparser.add_to_subparser_object(subparsers, baseParser)
    testSubparser.add_to_subparser_object(subparsers, baseParser)
    packageSubparser.add_to_subparser_object(subparsers, baseParser)

    if len(arguments) == 0:
        argParser.print_help()
        return None
    else:
        try:
            args = argParser.parse_args(arguments)
            if args.func:
                args.func(args)
        except Exception as e: 
            print(str(e))
            return None 
        if args.help:
            argParser.print_help()
            return None

        return args

def main(arguments, out=sys.stdout):
    # Set the path
    PathMapper.set_root_path(os.path.dirname(os.path.abspath(__name__)))_root_path(

    try:
        parsedArgs = parse_arguments(arguments, output=out)
    except PyCException as e:
        out.write(e.message)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
