################################################################################
# Filename: conf_definitions.py
# Author:   Brandon Milton
#           http://brandonio21.com
# Date:     July 2, 2015
# 
# Test that verifies that the definitions configuration file is configured 
# properly. If test fails, something is wrong in definition config file.
################################################################################
import json
import os
import re

# Settings
DEFINITIONS_SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../../conf/definitions.json"
proper_fields = ['test_directory' , 'sample_case_extension', 'corner_case_extension',
        'generated_case_extension', 'input_file_ending', 'output_file_ending',
        'writers_directory', 'solution_naming']
required_subfields = {}
proper_fields_min_lens = []

# Tests
def fileExists():
    return os.path.isfile(DEFINITIONS_SETTINGS_FILE)

def containsProperFields(jsonContents):
    for field in proper_fields:
        if not field in jsonContents:
            return False

    return len(jsonContents) == len(proper_fields)

def run_tests():
    if not fileExists():
        return False

    with open(DEFINITIONS_SETTINGS_FILE) as f:
        contents = f.read()

    if len(contents) <= 0:
        return False

    jsonContents = json.loads(contents)
    if not containsProperFields(jsonContents):
        return False

    return True

if __name__ == '__main__':
    assert(fileExists())

    with open(DEFINITIONS_SETTINGS_FILE) as f:
        contents = f.read()

    assert(len(contents) > 0)

    jsonContents = json.loads(contents)
    assert(containsProperFields(jsonContents))

