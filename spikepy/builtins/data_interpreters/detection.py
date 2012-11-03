
import csv
import cPickle

import scipy

from spikepy.developer.data_interpreter import DataInterpreter 
from spikepy.common.valid_types import ValidOption

class DetectionInterpreter(DataInterpreter):
    name = 'Detection'
    description = "The results of the detection stage."
    requires = ['event_times']

    file_format = ValidOption('.mat', '.csv', '.txt', '.npz', '.cPickle', 
            default='.mat')

    def write_data_file(self, trials, base_path, file_format='.mat'):
        self._check_requirements(trials)

        filenames = self.construct_filenames(trials, base_path)
        fullpaths = []
        for trial in trials:
            filename = filenames[trial.trial_id]
            fullpath = '%s%s' % (filename, file_format)
            fullpaths.append(fullpath)

            data_dict = {}
            for channel_num, channel_data in enumerate(trial.event_times.data):
                data_dict['events_on_channel_%d' % channel_num] = channel_data
            if file_format == '.mat':
                scipy.io.savemat(fullpath, data_dict)
            elif file_format == '.npz':
                scipy.savez(fullpath, **data_dict)
            elif file_format == '.cPickle':
                with open(fullpath, 'wb') as outfile:
                    cPickle.dump(trial.event_times.data, outfile, protocol=-1)
            elif file_format == '.csv' or file_format == '.txt':
                delimiters = {'.csv':',', '.txt':' '}
                delimiter = delimiters[file_format]
                with open(fullpath, 'wb') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)
                    for channel_data in trial.event_times.data:
                        writer.writerow(channel_data)
        return fullpaths
            
        
