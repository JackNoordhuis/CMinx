################################################################################
#
# File: helpers.py
#
# This file contains functions that are useful throughout the CMinx test suite.
#
################################################################################
import difflib
import sys
import os
import cminx

def quiet_cminx(args):
    """
    Hides CMinx's printing so we get clean test logs.

    :param args: The arguments to pass to the CMinx command.
    :type args: [str]

    :return: None
    """
    sys.stdout = open(os.devnull, 'w')
    cminx.main(args)
    sys.stdout = sys.__stdout__


def diff_files(generated_file, corr_file):
    """
    Returns the difference between two files.

    This function takes as input the full paths to two files and returns the
    difference between the two files in a format akin to the Unix ``diff``
    command.

    :param generated_file: The file we are comparing to ``corr_file``
    :type generated_file: os.path
    :param corr_file: The  file we are compare to ``generated_file``.
    :type corr_file: os.path

    :return: The difference between the input files, in a format akin to the
             ``diff`` command.
    :rtype: str

    .. note::

       The files are treated equivalently by this function so the order does not
       actually matter.
    """
    file_text = []
    for file_name in [generated_file, corr_file]:
        with open(file_name) as f:
            file_text.append(f.readlines())
    diff = ""
    for line in difflib.unified_diff(file_text[0], file_text[1]):
        diff += str(line)
    return diff
