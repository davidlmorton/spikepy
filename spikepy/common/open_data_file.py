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

import os

from wx.lib.pubsub import Publisher as pub

from .trial import Trial
from spikepy.common.plugin_utils import get_all_file_interpreters


def open_data_file(fullpath, file_interpreter_name=None):
    """
    Open a datafile given the filename and return a Trial object.
    """
    if file_interpreter_name is None:
        file_interpreter = guess_file_interpreter(fullpath)

    return file_interpreter.read_data_file(fullpath)

    
def guess_file_interpreter(fullpath):
    """
    Guess the file_interpreter, given a data file's fullpath.
    """
    filename = os.path.split(fullpath)[-1]
    extention = os.path.splitext(filename)[-1]
    file_interpreters = get_all_file_interpreters()

    candidates = {}
    for fi in  file_interpreters:
        if extention in fi.extentions:
            candidates[fi.priority] = fi

    if candidates:
        high_priority = sorted(candidates.keys())[-1]
        return candidates[high_priority]
    
    return file_interpreters[0]
