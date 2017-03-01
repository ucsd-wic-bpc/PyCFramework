################################################################################
# Filename: template.py
# Author:   Brandon Milton
# Date:     02 Feb 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py template
################################################################################
"""
The goal of this module is to create a template generator that gets its 
information from the case files provided via the commandline. From the
case files, the problem number, language, input types, and output types
can be determined. The only thing that needs to be provided is the function name.

The prototypes for the functions can be created in a template (for templates
heh)
"""
import json
from util.pathmapper import PathMapper
from util import case, fileops
from util.fileops import FileType, get_files_in_dir, join_path, get_json_dict, get_path_with_changed_extension
from util.case import Case, get_all_cases
from util.definitions import Definitions
from util.language import Languages

SUBPARSER_KEYWORD = 'template'
templateDictionary = None

def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `template` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    generate_templates_from_case_files(args.problems, args.language, args.output)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the template subparser to a given subparsers object and delegates
    listing functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to
                      add the template subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    templateParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                                parents=[parentParser])
    defaultTemplateLoc = PathMapper.get_mapped_path_from_parent('Templates','Generated')
    templateParser.add_argument('--output', default=defaultTemplateLoc)
    templateParser.set_defaults(func=operate)


def generate_templates_from_case_files(problems:list, languages: list,
        outputPath: str):
    """
    Attempts to generate template files for the given case files.
    """
    for problem in problems:
        caseList = get_all_cases(problemNumber=problem)[int(problem)]
        if languages is None or len(languages) == 0:
            languages = Languages.get_all_language_names()
        generate_template_for_case_collection(caseList, languages, outputPath, problem)

def get_jsonstr(jsonstr):
    """
    Return the string associated with the json object. If the json object is
    a list, the list is joined with newlines
    """
    if isinstance(jsonstr, list):
        return '\n'.join(jsonstr)
    else:
        return jsonstr

def get_type_from_many(jsonstrs):
    strtypes = [get_type(jsonstr) for jsonstr in jsonstrs]

    finalized_types = []
    for i in range(1, len(strtypes)):
        if strtypes[i-1] == None or strtypes[i] == None:
            continue

        # What if types dont match?
        if strtypes[i-1] != strtypes[i]:
            if "char" in strtypes[i-1] and "str" in strtypes[i]:
                strtypes[i-1] = strtypes[i]
                finalized_types.append(strtypes[i-1])
            elif "str" in strtypes[i-1] and "char" in strtypes[i]:
                strtypes[i] = strtypes[i-1]
                finalized_types.append(strtypes[i-1])
            else:
                print("ERROR!")
        else:
            finalized_types.append(strtypes[i-1])


    return finalized_types[0]

def get_individual_type(parsed_jsonstr):
    if isinstance(parsed_jsonstr, str) and len(parsed_jsonstr) == 1:
        return 'char'
    else:
        return type(parsed_jsonstr).__name__

def get_type(jsonstr):
    """
    Return the type of the provided string
    """
    try:
        parsed_jsonstr = json.loads(jsonstr)
    except Exception:
        parsed_jsonstr = jsonstr

    type_string = get_individual_type(parsed_jsonstr)

    list_depth = 0
    while isinstance(parsed_jsonstr, list):
        if len(parsed_jsonstr) <= 0:
            return None

        list_depth += 1
        parsed_jsonstr = parsed_jsonstr[0]
        type_string = get_individual_type(parsed_jsonstr)

    if list_depth > 0:
        type_string = "_".join((["list"] * list_depth) + [type_string])

    return type_string


def generate_template_for_case_collection(cases: list, languages: list, outputPath: str, problem):
    # First, let's populate a dictionary with all relevant information about
    # the cases. Let's just use the first case.

    language = Languages.get_language_by_name(languages[0])

    outputType = get_type_from_many([case.outputContents for case in cases])

    # A list of input groups such that input_groups[0] is a list of all the first inputs
    input_groups = []
    for case in cases:
        for i, input in enumerate(json.loads(case.inputContents)):
            if len(input_groups) <= i:
                input_groups.append([])

            input_groups[i].append(input)

    inputTypes = [get_type_from_many(inputs) for inputs in input_groups]

    data = get_json_dict('cases/problem{}_data.json'.format(problem))
    wordNums = data["args"]
    template = get_json_dict('conf/templates/{}.json'.format(language.name))

    info_dictionary = {
        'problem': problem,
        'returnType': template["types"][outputType],
        'defaultReturnType': template["default_values"][outputType],
        'methodName': data["method"],
        'formalsList': ', '.join(['{} {}'.format(template["types"][i], wordNums[j])
                                 for j,i in enumerate(inputTypes)]),
        'actualsList': ', '.join(wordNums[i] for i,j in enumerate(inputTypes))
    }

    # Now fill the info dictionary with files we might need
    for f in get_files_in_dir('conf/templates/files', relative_to_path=True):
        full_path = join_path('conf/templates/files', f)
        with open(full_path, 'r') as openf:
            filename_less_ext = get_path_with_changed_extension(f, '')
            info_dictionary['file/{}'.format(filename_less_ext)] = openf.read()


    def gstr(s):
        if isinstance(s, list):
            return '\n'.join(s)
        else:
            return s


    # Now lets print the sample
    print(gstr(template["file"]["header"]).format(**info_dictionary))
    print(gstr(template["user_impl"]["header"]).format(**info_dictionary))
    print(gstr(template["user_impl"]["body"]).format(**info_dictionary))
    print(gstr(template["user_impl"]["footer"]).format(**info_dictionary))
    print(gstr(template["main"]["header"]).format(**info_dictionary))
    print(gstr(template["main"]["parse_input"]).format(**info_dictionary))

    for i, j in enumerate(inputTypes):
        info = {"type": template["types"][j], "varName": wordNums[i], "argNum":i}
        print(gstr(template["args"][j]).format(**info))

    print(gstr(template["main"]["store_output"]).format(**info_dictionary))
    print(gstr(template["main"]["print_output"]).format(**info_dictionary))
    print(gstr(template["main"]["footer"]).format(**info_dictionary))
    print(gstr(template["file"]["footer"]).format(**info_dictionary))
    return
