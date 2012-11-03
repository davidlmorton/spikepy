
import csv

import scipy

from spikepy.developer.data_interpreter import DataInterpreter 
from spikepy.common.valid_types import ValidOption

class ExtractionInterpreter(DataInterpreter):
    name = 'Extraction'
    description = "The results of the extraction stage."
    requires = ['features', 'feature_times']

    file_format = ValidOption('.mat', '.csv', '.txt', '.npz', default='.mat')

    def write_data_file(self, trials, base_path, file_format='.mat'):
        self._check_requirements(trials)

        filenames = self.construct_filenames(trials, base_path)
        fullpaths = []
        for trial in trials:
            filename = filenames[trial.trial_id]
            fullpath = '%s%s' % (filename, file_format)
            fullpaths.append(fullpath)

            data_dict = {'features':trial.features.data,
                         'feature_times':trial.feature_times.data}
            if file_format == '.mat':
                scipy.io.savemat(fullpath, data_dict)
            elif file_format == '.npz':
                scipy.savez(fullpath, **data_dict)
            elif file_format == '.csv' or file_format == '.txt':
                delimiters = {'.csv':',', '.txt':' '}
                delimiter = delimiters[file_format]
                with open(fullpath, 'wb') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)
                    writer.writerow(trial.feature_times.data)
                    writer.writerow([len(trial.features.data)])
                    for feature in trial.features.data:
                        writer.writerow(feature)
        return fullpaths
            
        
