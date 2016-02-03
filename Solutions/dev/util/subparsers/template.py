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
from util.fileops import FileType
from util.case import Case
from util.definitions import Definitions
from util.language import Languages

SUBPARSER_KEYWORD = 'template'


def operate(args):
    """
    Takes the passed in args and delegates to the proper functionality. This
    is set as the executable function when the `template` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    generate_templates_from_case_files(args.case_files, args.language, 
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
    defaultTemplateLoc = PathMapper.get_mapped_path_from_parent('Templates','Generated')
    templateParser.add_argument('case_files', nargs='*')
    templateParser.add_argument('--output', default=defaultTemplateLoc)
    templateParser.set_defaults(func=operate)


def generate_templates_from_case_files(caseFilePaths:list, languages: list,
        outputPath: str):
    """
    Attempts to generate template files for the given case files.
    """
    for path in caseFilePaths:
        caseList = case.get_cases_from_json_file(path)
        if languages is None or len(languages) == 0:
            languages = Languages.get_all_language_names()
        generate_template_for_case_collection(caseList, languages, outputPath)

def generate_template_for_case_collection(cases: list, languages: list, outputPath: str):
    for (templatePath, templateLanguage) in generate_blank_template_files_for_case_collection(cases, languages, outputPath):
        fill_template_file_for_case_collection(templatePath, templateLanguage,
                cases)

def get_unformatted_template(language):
    """
    Returns the unformatted template text for the given Language object.
    """
    path = 'conf/templates/{}'.format(language.name)
    return fileops.read_file(path)

def generate_blank_template_files_for_case_collection(cases:list, languages:list,
        outputPath: str):
    """
    Creates the template files in the given directory and yields the following 
    tuple:
    (path, Language)
    so that they may be written to.
    """
    if cases is None or len(cases) == 0:
        return []
    else:
        templateFile = Definitions.get_value('solution_naming').format(
                **{'problem':cases[0].problemNumber})
        templateFilePath = fileops.join_path(outputPath, '{}.{{}}'.
                format(templateFile))

        for languageName in languages:
            languageObj = Languages.get_language_by_name(languageName)
            path = templateFilePath.format(languageObj.get_extension())
            fileops.make(path, FileType.FILE)
            yield (path, languageObj)

def fill_template_file_for_case_collection(path: str, language, cases: list):
    formattedTemplate = get_unformatted_template(language).format(**{
        'problem' : cases[0].problemNumber,
        'returnType' : type(json.loads(cases[0].outputContents.lower())).__name__,
        'methodName' : "balalkjfslkafj",
        'argList' : "int poop",
        'defaultReturn' : 0,
        })

    fileops.write_file(path, formattedTemplate)
