################################################################################
# Filename: util/parse.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     16 October 2015
#
# Contains utilities for parsing things
################################################################################

class NumberParse:
    def __init__(self, lessThanSymbol: str='-', greaterThanSymbol: str='+',
            rangeSymbol: str='-'):
        self._lessThanSymbol = lessThanSymbol
        self._greaterThanSymbol = greaterThanSymbol
        self._toSymbol = rangeSymbol

    def str_to_list_range(self, string, uBound, lBound):
        if not self._lessThanSymbol in string and not self._greaterThanSymbol in string:
            return [int(string)]

        parsedString = parse_greater_than(string, uBound)
        if isinstance(parsedString, list):
            return parsedString

        parsedString = parse_less_than(string, lBound)
        if isinstance(parsedString, list):
            return parsedString

        parsedString = parse_range(string, lBound, uBound)
        return parsedString

    def parse_greater_than(self, string, uBound):
        if string[-1] == self._greaterThanSymbol:
            begNum = int(string[0:-1])
            return [i for i in range(begNum, uBound + 1)]
        
        return string

    def parse_less_than(self, string, lBound):
        if string[-1] == self._lessThanSymbol:
            endNum = int(string[0:-1])
            return [i for i in range(lBound, endNum + 1)]

        return string

    def parse_range(self, string, lBound, uBound):
        try:
            dashIndex = string.index(self._toSymbol)
            beg = max(int(string[0:dashIndex]), lBound)
            end = min(int(string[dashIndex + len(self._toSymbol):]), uBound)

            return [i for i in range(beg, end + 1)]

        except ValueError:
            return [int(string)]
