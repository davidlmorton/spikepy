"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import traceback
import sys
import os

from wx.lib.pubsub import Publisher as pub

from .trial import Trial
from spikepy.common.plugin_utils import get_all_file_interpreters


def open_data_file(fullpath, file_interpreter_name=None):
    """
    Open a datafile given the filename and return a Trial object.
    """
    if file_interpreter_name is None:
        file_interpreters = guess_file_interpreters(fullpath)

    all_e_info = []
    for fi in file_interpreters:
        try:
            return fi.read_data_file(fullpath)
        except:
            all_e_info.append((fi, sys.exc_info()))

    # write exception information to files.
    for fi, exc_info in all_e_info:
        filename = fi.name.lower().replace(' ', '_') + '.error'
        with open(filename, 'w') as ofile:
            traceback.print_exception(exc_info[0], exc_info[1], 
                                      exc_info[2], 100, ofile)

    raise RuntimeError('File Interpretation of %s failed.  Errors in "*.error" files.'
                       % fullpath)

    
def guess_file_interpreters(fullpath):
    """
    Guess the file_interpreter, given a data file's fullpath.
    Returns a list of file_interpreters in descending order of
        applicability.
    """
    filename = os.path.split(fullpath)[-1]
    extention = os.path.splitext(filename)[-1]
    file_interpreters = get_all_file_interpreters()

    candidates = {}
    for fi in  file_interpreters:
        if extention in fi.extentions:
            candidates[fi.priority] = fi

    if candidates:
        return [candidates[key] for key in 
                sorted(candidates.keys(), reverse=True)]
    
    return file_interpreters # try everything!
