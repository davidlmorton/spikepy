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

import numpy

from spikepy.developer_tools.file_interpreter import FileInterpreter, Trial

class Wessel_LabView_text_tetrode(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView plain text tetrode'
        self.extentions = ['.tet']
        self.priority = 10
        self.description = '''A plain text file containing one trial.  Data are organized in columns.  Columns: 0,1,2,3=data(mV) 4=pulse_1 5=pulse_2 6=time(ms).'''

    def read_data_file(self, fullpath):
        data = numpy.loadtxt(fullpath)
        raw_traces = data.T[:4]
        times = data.T[-1]
        sampling_freq = int((len(times)-1)/
                            (times[-1]-times[0])*1000) # 1000 kHz->Hz

        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]
        trial = Trial.from_raw_traces(sampling_freq, raw_traces, 
                origin=fullpath, display_name=display_name)
        return [trial]
