
import csv

import scipy

from spikepy.developer.data_interpreter import DataInterpreter 
from spikepy.common.valid_types import ValidOption

class DetectionFilterInterpreter(DataInterpreter):
    name = 'Detection Filter'
    description = "The results of the detection filtering stage."
    requires = ['df_traces', 'df_sampling_freq']

    file_format = ValidOption('.mat', '.csv', '.txt', '.npz', default='.mat')

    def write_data_file(self, trials, base_path, file_format='.mat'):
        self._check_requirements(trials)

        filenames = self.construct_filenames(trials, base_path)
        fullpaths = []
        for trial in trials:
            filename = filenames[trial.trial_id]
            fullpath = '%s%s' % (filename, file_format)
            fullpaths.append(fullpath)

            data_dict = {'filtered_data':trial.df_traces.data,
                         'sampling_freq':trial.df_sampling_freq.data} 
            if file_format == '.mat':
                scipy.io.savemat(fullpath, data_dict)
            elif file_format == '.npz':
                scipy.savez(fullpath, **data_dict)
            elif file_format == '.csv' or file_format == '.txt':
                delimiters = {'.csv':',', '.txt':' '}
                delimiter = delimiters[file_format]
                with open(fullpath, 'wb') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)
                    writer.writerow([trial.df_sampling_freq.data])
                    for channel_data in trial.df_traces.data:
                        writer.writerow(channel_data)
        return fullpaths
            
        
