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

from scipy.io import loadmat

from spikepy.developer.file_interpreter import FileInterpreter, Trial

class GenericMatlab(FileInterpreter):
    def __init__(self):
        self.name = 'Generic Matlab(tm) File'
        self.extentions = ['.mat']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A Matlab(tm) file.'''

    def read_data_file(self, fullpath):
        mat_obj = loadmat(fullpath)

        # edit so that names match the variables in the .mat file.
        signal_name = 'raw_traces'
        times_name = 'times'
        infer_sampling_freq = True
        sf = None

        # mat_obj[signal_name] should be a 2D array, rows=channels cols=time.
        voltage_traces = mat_obj[signal_name]
        if infer_sampling_freq:
            times = mat_obj[times_name]
            # times are assumed to be in ms.
            sampling_freq = int(len(times)/(times[-1]-times[0]))*1000  
        else:
            sampling_freq = sf

        # display_name can be anything, here we just use the filename.
        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]

        trials = Trial.from_raw_traces(sampling_freq, voltage_traces, 
                origin=fullpath, display_name=display_name)
        return [trial] # need to return a list of trials.

