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
import csv

import scipy

from spikepy.developer_tools.data_interpreter import DataInterpreter 
from spikepy.common.valid_types import ValidOption

class DetectionInterpreter(DataInterpreter):
    name = 'Detection'
    description = "The results of the detection stage."
    requires = ['event_times']

    file_format = ValidOption('.mat', '.csv', '.txt', '.npz', default='.mat')

    def write_data_file(self, trials, file_format='.mat'):
        self._check_requirements(trials)

        filenames = self.construct_filenames(trials)
        fullpaths = []
        for trial in trials:
            filename = filenames[trial.trial_id]
            fullpath = '%s%s' % (filename, file_format)
            fullpaths.append(fullpath)

            data_dict = {'event_times':trial.event_times.data}
            if file_format == '.mat':
                scipy.io.savemat(fullpath, data_dict)
            elif file_format == '.npz':
                scipy.savez(fullpath, **data_dict)
            elif file_format == '.csv' or file_format == '.txt':
                delimiters = {'.csv':',', '.txt':' '}
                delimiter = delimiters[file_format]
                with open(fullpath, 'wb') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)
                    for channel_data in trial.event_times.data:
                        writer.writerow(channel_data)
        return fullpaths
            
        
