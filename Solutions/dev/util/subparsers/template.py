###############################################################################
# Filename: template.py
# Author:   Brandon Milton
# Date:     02 Feb 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py template
###############################################################################
"""
The goal of this module is to create a template generator that gets its
information from the case files provided via the commandline. From the
case files, the problem number, language, input types, and output types
can be determined. The only thing that need be provided is the function name.

The prototypes for the functions can be created in a template (for templates
heh)
"""
import json
from util.pathmapper import PathMapper
from util.fileops import join_path, get_json_dict, write_file, make, FileType
from util.case import get_all_cases
from util.definitions import Definitions
from util.language import Languages
from util.templating.jsonstubber.java_stubber import JavaJSONStubber
from util.templating.jsonstubber.cpp_stubber import CppJSONStubber
from util.templating.jsonstubber.python_stubber import PythonJSONStubber
from util.templating.pyjsontypes.parse import resolve_type

SUBPARSER_KEYWORD = 'template'


def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `template` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    generate_templates_from_case_files(args.problems, args.language,
                                       args.output)


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
    defaultTemplateLoc = PathMapper.get_mapped_path_from_parent(
            'Templates', 'Generated')
    templateParser.add_argument('--output', default=defaultTemplateLoc)
    templateParser.set_defaults(func=operate)


def generate_templates_from_case_files(problems: list, languages: list,
                                       outputPath: str):
    """
    Attempts to generate template files for the given case files.
    """
    make(outputPath, FileType.DIRECTORY)
    for problem in problems:
        caseList = get_all_cases(problemNumber=problem)[int(problem)]

        for language in languages or Languages.get_all_language_names():
            language = Languages.get_language_by_name(language)
            generate_template_for_case_collection(
                caseList, language, outputPath, problem
            )


def generate_template_for_case_collection(cases: list, language: list,
                                          outputPath: str, problem):

    stubber_factory_map = {
        "Java": JavaJSONStubber,
        "C++": CppJSONStubber,
        "Python": PythonJSONStubber
    }

    if language.name not in stubber_factory_map:
        raise Exception('Generating templates for {} not supported'.format(
                        language.name))

    outputType = resolve_type([case.outputContents for case in cases])

    if outputType is None:
        raise Exception('Could not deduce output type for problem {}'.format(
                        problem))

    # A list of input groups such that input_groups[0] is a list of all the
    # first inputs
    input_groups = []
    for case in cases:
        for i, input in enumerate(json.loads(case.inputContents)):
            if len(input_groups) <= i:
                input_groups.append([])

            input_groups[i].append(input)

    inputTypes = [resolve_type(inputs) for inputs in input_groups]

    if inputTypes is None:
        raise Exception('Could not deduce input types for problem {}'.format(
                        problem))

    data_folder = Definitions.get_value("template_data_directory")
    datafile_path = PathMapper.get_mapped_path(
        data_folder, "problem{}.json".format(problem)
    )

    stubber = stubber_factory_map[language.name](
        jsonfastparse_path='util/templating/jsonstubber/jsonfastparse',
        unifiedstr_path='util/templating/jsonstubber/unifiedstr'
    )

    template_data = get_json_dict(datafile_path)
    arg_names = template_data["args"]
    method_name = template_data["method"]
    class_name = 'Problem{}'.format(problem)
    userimpl_header = stubber.make_comment_string(template_data["header"])

    do_not_edit_str = [
"------------------------------ DO NOT EDIT BELOW THIS LINE ------------------"
                      ]
    userimpl_footer = stubber.make_comment_string(do_not_edit_str)

    arguments = [(arg_names[name_index], input_type) for
                 name_index, input_type in enumerate(inputTypes)]

    template = stubber.make_stub(
        class_name, method_name, outputType, arguments,
        user_impl_header=userimpl_header,
        user_impl_footer=userimpl_footer
    )

    template_path = join_path(outputPath, 'Problem{}.{}'.format(
        problem, language.get_extension())
    )
    write_file(template_path, template)
