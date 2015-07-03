################################################################################
# Filename: conf_langauges.py
# Author:   Brandon Milton
#           http://brandonio21.com
# Date:     July 2, 2015
# 
# Test that verifies that the languages configuration file is configured 
# properly. If test fails, something is wrong in language config file.
################################################################################
import json
import os
import re

# Settings
LANGUAGES_SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../../conf/languages.json"
proper_fields = ['variables', 'languages']
required_subfields = {'languages' : ['runCommand', 'runExtension']}
proper_fields_min_lens = [0, 1]
variable_field = 'variables'
variable_pattern = re.compile("{[^{^}]*}")

# Tests
def fileExists():
    return os.path.isfile(LANGUAGES_SETTINGS_FILE)

def containsProperFields(jsonContents):
    for field in proper_fields:
        if not field in jsonContents:
            return False

    return len(jsonContents) == len(proper_fields)

def containsProperContentsAmounts(jsonContents):
    for i in range(0, len(proper_fields_min_lens)):
        if len(jsonContents[proper_fields[i]]) < proper_fields_min_lens[i]:
            return False
    return True

def containsDeclaredVariables(jsonContents):
    for field in proper_fields:
        if field == variable_field:
            continue


        for fieldSet in jsonContents[field]:
            for key, value in fieldSet.items():
                for variable in variable_pattern.findall(value):
                    found = False
                    for possibleVars in jsonContents[variable_field]:
                        for k,v in possibleVars.items():
                            if variable == v:
                                found = True
                    if not found:
                        return False
        return True

def containsAllRequiredSubfields(jsonContents):
    for field, subfields in required_subfields.items():
        for subfield in subfields:
            found = False
            for indivItem in jsonContents[field]:
                for key, value in indivItem.items():
                    if key == subfield:
                        found = True
                if not found:
                    return False
    return True

                
if __name__ == '__main__':
    assert(fileExists())  # Check to make sure languages file exists

    with open(LANGUAGES_SETTINGS_FILE) as f:
        contents = f.read()

    assert(len(contents) > 0) # Check to make sure languages file is not empty

    jsonContents = json.loads(contents) 
    assert(containsProperFields(jsonContents))
    assert(containsProperContentsAmounts(jsonContents))

    # Chcek that all languages have a run command and all variables are real
    assert(containsDeclaredVariables(jsonContents))
    
    # Check that required subfields are there
    assert(containsAllRequiredSubfields(jsonContents))
