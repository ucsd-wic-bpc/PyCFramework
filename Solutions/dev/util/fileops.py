################################################################################
# Filename: fileops.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     30 August 2015
#
# This module contains many useful functions for operating with files
################################################################################
import os
import json

def exists(path, fileType):
    """
    Returns whether the object at the given path exists
    """
    # Check if file exists
    if not os.path.exists(path):
        return False
    # File exists. If type is file, check if path is file
    elif fileType == FileType.FILE:
        return os.path.isfile(path)
    # File exists. Type is dir. Check if path is dir
    else:
        return os.path.isdir(path)

def get_json_dict(path):
    """
    Returns a dictionary for a json file if it exists, else an empty dict
    """
    dictionary = {}
    if exists(path, FileType.FILE):
        with open(path) as openFile:
            dictionary = json.loads(openFile.read())

    return dictionary

def join_path(path, *parts):
    """
    Joins the path with a list of parts
    """
    return os.path.join(path, parts)

def get_files_in_dir(path: str, recursive: bool=False) -> list:
    """
    Returns a list of filepaths within a directory. Also includes child directories if recursive
    """
    if not recursive:
        return [filePath for filePath in os.listdir(path) if os.path.isfile(filePath)]
    else:
        workingFileList = get_files_in_dir(path, recursive=False)
        for filePath in os.listdir(path):
            if os.path.isdir(filePath):
                workingFileList.extend(get_files_in_dir(filePath, recursive=True))

        return workingFileList

def get_basename_less_extension(path: str) -> str:
    """
    Returns the basename of the file given by path without its extension
    """
    return os.path.splitext(os.basename(path))[0]


class FileType:
    FILE = 0
    DIRECTORY = 1
