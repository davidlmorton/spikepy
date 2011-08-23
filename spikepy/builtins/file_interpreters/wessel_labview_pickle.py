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
import gzip
import cPickle
import os

import numpy

from spikepy.developer_tools.file_interpreter import FileInterpreter, Trial

class WesselLabViewText(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView Pickle'
        self.extentions = ['.pgz', '.cPickle']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A pickled version of data acquired in the Wessel lab.'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.pgz'):
            infile = gzip.open(fullpath)
        else:
            infile = open(fullpath)
        data = cPickle.load(infile)
        voltage_trace = data['voltage_trace']
        sampling_freq = data['sampling_freq']

        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]
        trial = Trial.from_raw_traces(sampling_freq, [voltage_trace], 
                origin=fullpath, display_name=display_name)
        return [trial]
