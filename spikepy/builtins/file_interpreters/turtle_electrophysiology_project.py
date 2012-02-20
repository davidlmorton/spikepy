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

from spikepy.developer.file_interpreter import FileInterpreter, Trial

SHANK_CHANNEL_INDEX = [9,   8, 10,  7, 13,  4, 12,  5, 
                       15,  2, 16,  1, 14,  3, 11,  6]

class TurtleElectrophysiologyProject(FileInterpreter):
    def __init__(self):
        self.name = 'Archived TEP file.'
        self.extentions = ['.gz', '.cPickle']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''An archived Turtle Electrophysiology Project file.'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.gz'):
            infile = gzip.open(fullpath, 'rb')
        else:
            infile = open(fullpath, 'rb')
        data = cPickle.load(infile)
        voltage_traces = data['voltage_traces']
        sampling_freq = data['sampling_freq']

        if len(voltage_traces) == 16:
            voltage_traces = voltage_traces[[i-1 for i in SHANK_CHANNEL_INDEX]]

        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]
        trials = [Trial.from_raw_traces(sampling_freq, voltage_traces, 
                                        origin=fullpath, 
                                        display_name=display_name)]
        return trials
