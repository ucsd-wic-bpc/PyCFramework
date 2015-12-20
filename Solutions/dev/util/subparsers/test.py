################################################################################
# Filename: util/subparsers/test.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     20 December 2015
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py test
################################################################################

SUBPARSER_KEYWORD = "test"

def operate(args):
    writerList = args.writers

def add_to_subparser_object(subparserObject, parentParser):
    testParser = subparserObject.add_parser(SUBPARSER_KEYWORD, parents=[parentParser])
    testParser.add_argument('writers', nargs='*')
    testParser.set_defaults(func=operate)
