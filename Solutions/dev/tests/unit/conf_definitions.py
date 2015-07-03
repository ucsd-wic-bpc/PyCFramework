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
        'writers_directory']
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


if __name__ == '__main__':
    assert(fileExists())  # Check to make sure definitions file exists

    with open(DEFINITIONS_SETTINGS_FILE) as f:
        contents = f.read()

    assert(len(contents) > 0) # Check to make sure definitions file is not empty

    jsonContents = json.loads(contents) 
    assert(containsProperFields(jsonContents))
