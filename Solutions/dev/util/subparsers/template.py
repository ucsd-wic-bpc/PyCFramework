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
from util.case import Case
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
    templateParser.add_argument('case_files', nargs='+')
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
    # First, let's populate a dictionary with all relevant information about
    # the cases. Let's just use the first case.
    case = cases[0]
    language = Languages.get_language_by_name(languages[0])

    outputContents = json.loads(case.outputContents)
    inputContents = json.loads(case.inputContents)
    outputType = type(outputContents).__name__
    inputTypes = [type(i).__name__ for i in inputContents]
    data = get_json_dict('data/problem{}.json'.format(case.problemNumber))
    wordNums = data["args"]
    template = get_json_dict('conf/templates/{}.json'.format(language.name))

    info_dictionary = {
        'problem': case.problemNumber,
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
        print('{}{}'.format(gstr(template["main"]["decl"].format(**info)),
                            gstr(template["args"][j].format(**info))))

    outputdict = {'type': info_dictionary["returnType"], 'varName': 'output'}
    print('{}{}'.format(gstr(template["main"]["decl"].format(**outputdict)),
                        gstr(template["main"]["store_output"].format(**info_dictionary))))
    print(gstr(template["main"]["print_output"].format(**info_dictionary)))
    print(gstr(template["main"]["footer"].format(**info_dictionary)))
    print(gstr(template["file"]["footer"].format(**info_dictionary)))
    return


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

def get_language_specific_type(language, typeStr: str):
    global templateDictionary
    if templateDictionary is None:
        dictionaryConfigPath = PathMapper.get_mapped_config_path('templates','dictionary.json')
        templateDictionary = fileops.get_json_dict(dictionaryConfigPath)

    return templateDictionary[language.name][typeStr]

def output_type_to_proper_str(outputStr: str):
    return type(json.loads(outputStr.lower())).__name__

def fill_template_file_for_case_collection(path: str, language, cases: list):
    formattedTemplate = get_unformatted_template(language).format(**{
        'problem' : cases[0].problemNumber,
        'returnType' : get_language_specific_type(language, 
                       output_type_to_proper_str(cases[0].outputContents)),
        'methodName' : "balalkjfslkafj",
        'argList' : "int poop",
        'defaultReturn' : 0,
        })

    fileops.write_file(path, formattedTemplate)
