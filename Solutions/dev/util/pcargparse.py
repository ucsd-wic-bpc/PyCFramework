################################################################################
# Filename: util/PCArgParse.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     06 October 2015
#
# Contains a custom ArgParse object for use by PyCFramework
################################################################################
import argparse

class PCArgParseFactory:
    cachedArgParser = None

    @classmethod
    def get_argument_parser(cls, output):
        if cls.cachedArgParser is None or not cls.cachedArgParser.output == output:
            cls.cachedArgParser = PCArgParse(output)

        return cls.cachedArgParser

class PCArgParse(argparse.ArgumentParser):
    def __init__(self, output, **kwargs):
        self.output = output
        super(PCArgParse, self).__init__(kwargs, add_help=False,
            description='An interface for a programming competition')

    # Override to print help to output
    def print_help(self, file=None):
        self._print_message(self.format_help(), self.output)

    def print_usage(self, file=None):
        self._print_message(self.format_usage(), self.output)

    # Override to print help if invalid arg is provided
    def error(self, message):
        output.write('Error: {0}\n'.format(message))
        self.print_help()
        return


