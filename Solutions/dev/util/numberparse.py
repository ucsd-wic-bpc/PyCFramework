################################################################################
# Filename: util/numberparse.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     15 October 2015
#
# Contains utilities for parsing stringed numbers
################################################################################


def str_to_list_range(string, uBound, lBound):
    if not '-' in string and not '+' in string:
        return [int(string)]

    parsedString = parse_greater_than(string, uBound)
    if isinstance(parsedString, list):
        return parsedString

    parsedString = parse_less_than(string, lBound)
    if isinstance(parsedString, list):
        return parsedString

    parsedString = parse_range(string, lBound, uBound)
    return parsedString

def parse_greater_than(string, uBound):
    if string[-1] == '+':
        begNum = int(string[0:-1])
        return [i for i in range(begNum, uBound + 1)]
    
    return string

def parse_less_than(string, lBound):
    if string[-1] == '-':
        endNum = int(string[0:-1])
        return [i for i in range(lBound, endNum + 1)]

    return string

def parse_range(string, lBound, uBound):
    try:
        dashIndex = string.index('-')
        beg = max(int(string[0:dashIndex]), lBound)
        end = min(int(string[dashIndex + 1:]), uBound)

        return [i for i in range(beg, end + 1)]

    except ValueError:
        return [int(string)]
