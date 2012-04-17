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

import numpy

from spikepy.developer.file_interpreter import FileInterpreter

class Wessel_LabView_text(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView plain text'
        self.extentions = ['.wpt', '', '.gz']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A plain text file containing one trial.  Data are organized in columns.  Columns: 0=data(mV) 1=pulse_1 2=pulse_2 3=time(ms).'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.gz'):
            infile = gzip.open(fullpath)
        else:
            infile = open(fullpath)
        data = numpy.loadtxt(infile)
        raw_trace = data.T[0]
        times = data.T[3]
        sampling_freq = int((len(times)-1)/
                            (times[-1]-times[0])*1000) # 1000 kHz->Hz

        trials = [self.make_trial_object(sampling_freq, [raw_trace], fullpath)]
        return trials
