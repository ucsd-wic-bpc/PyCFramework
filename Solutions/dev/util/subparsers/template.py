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
from util.fileops import FileType, get_files_in_dir, join_path, get_json_dict, get_path_with_changed_extension, write_file
from util.case import Case, get_all_cases
from util.definitions import Definitions
from util.language import Languages
from util.templating.jsonstubber.json_stubber import JSONTypes, JSONContainer, JSONType
from util.templating.jsonstubber.java_stubber import JavaJSONStubber

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

        for language in languages or Languages.get_all_language_names():
            language = Languages.get_language_by_name(language)
            generate_template_for_case_collection(caseList, language, outputPath, problem)

def get_jsonstr(jsonstr):
    """
    Return the string associated with the json object. If the json object is
    a list, the list is joined with newlines
    """
    if isinstance(jsonstr, list):
        return '\n'.join(jsonstr)
    else:
        return jsonstr

def get_type_root(jsontype):
    root = jsontype
    while isinstance(root, JSONContainer):
        root = root.subtype

    return root

def get_type_from_many(jsonstrs):
    strtypes = [get_type(jsonstr) for jsonstr in jsonstrs]

    finalized_types = []
    for i in range(1, len(strtypes)):
        if strtypes[i-1] is None or strtypes[i] is None:
            continue

        # What if types dont match?
        if strtypes[i-1] != strtypes[i]:
            left_root_type = get_type_root(strtypes[i-1])
            right_root_type = get_type_root(strtypes[i])
            if left_root_type == JSONTypes.CHAR and right_root_type == JSONTypes.STRING:
                strtypes[i-1] = strtypes[i]
                finalized_types.append(strtypes[i-1])
            elif left_root_type == JSONTypes.STRING and right_root_type == JSONTypes.CHAR:
                strtypes[i] = strtypes[i-1]
                finalized_types.append(strtypes[i-1])
            elif left_root_type == JSONTypes.INT and right_root_type == JSONTypes.FLOAT:
                strtypes[i-1] = strtypes[i]
                finalized_types.append(strtypes[i-1])
            elif left_root_type == JSONTypes.FLOAT and right_root_type == JSONTypes.INT:
                strtypes[i] = strtypes[i-1]
                finalized_types.append(strtypes[i-1])
            else:
                print("ERROR!")
        else:
            finalized_types.append(strtypes[i-1])


    return finalized_types[0]

def get_individual_type(parsed_jsonstr):
    if isinstance(parsed_jsonstr, str) and len(parsed_jsonstr) == 1:
        return JSONTypes.CHAR
    else:
        return JSONType.parse(type(parsed_jsonstr).__name__)

def get_type(jsonstr):
    """
    Return the type of the provided string
    """
    try:
        parsed_jsonstr = json.loads(jsonstr)
    except Exception:
        parsed_jsonstr = jsonstr


    if isinstance(parsed_jsonstr, list):
        list_depth = 0
        while isinstance(parsed_jsonstr, list):
            if len(parsed_jsonstr) <= 0:
                return None

            list_depth += 1
            parsed_jsonstr = parsed_jsonstr[0]

        jsontype = get_individual_type(parsed_jsonstr)

        while list_depth > 0:
            jsontype = JSONContainer(jsontype)
            list_depth -= 1
    else:
        jsontype = get_individual_type(parsed_jsonstr)

    return jsontype


def generate_template_for_case_collection(cases: list, language: list, outputPath: str, problem):
    # First, let's populate a dictionary with all relevant information about
    # the cases. Let's just use the first case.
    if language.name != "Java":
        raise Exception('Generating templates for {} not supported'.format(language.name))

    outputType = get_type_from_many([case.outputContents for case in cases])

    # A list of input groups such that input_groups[0] is a list of all the first inputs
    input_groups = []
    for case in cases:
        for i, input in enumerate(json.loads(case.inputContents)):
            if len(input_groups) <= i:
                input_groups.append([])

            input_groups[i].append(input)

    inputTypes = [get_type_from_many(inputs) for inputs in input_groups]

    data = get_json_dict('data/problem{}.json'.format(problem))
    arg_names = data["args"]
    method_name = data["method"]
    class_name = 'Problem{}'.format(problem)

    arguments = [(arg_names[name_index], input_type) for 
                 name_index, input_type in enumerate(inputTypes)]

    stubber = JavaJSONStubber(jsonfastparse_path='util/templating/jsonstubber/jsonfastparse',
                              unifiedstr_path='util/templating/jsonstubber/unifiedstr')
    template = stubber.make_stub(class_name, method_name, outputType, arguments)

    template_path = join_path(outputPath, 'Problem{}.{}'.format(problem, language.get_extension()))
    write_file(template_path, template)
