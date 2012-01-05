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
import gzip
import cPickle

import scipy

from spikepy.developer_tools.data_interpreter import DataInterpreter 
from spikepy.common.valid_types import ValidOption

class ClusteringInterpreter(DataInterpreter):
    name = 'Clustering'
    description = "The results of the clustering stage."
    requires = ['clusters']

    file_format = ValidOption('.mat', '.csv', '.txt', '.npz', 
            '.cPickle', '.cPickle.gz', default='.mat')

    def write_data_file(self, trials, base_path, file_format='.mat'):
        self._check_requirements(trials)

        filenames = self.construct_filenames(trials, base_path)
        fullpaths = []
        for trial in trials:
            filename = filenames[trial.trial_id]
            fullpath = '%s%s' % (filename, file_format)
            fullpaths.append(fullpath)

            if file_format == '.mat' or file_format == '.npz':
                data_dict = {}
                cf = trial.clustered_features
                cft = trial.clustered_feature_times
                for cluster_id in cf.keys():
                    data_dict['features(%s)' % cluster_id] = cf[cluster_id]
                    data_dict['feature_times(%s)' % cluster_id] = \
                            cft[cluster_id]
                    
                if file_format == '.mat':
                    scipy.io.savemat(fullpath, data_dict)
                elif file_format == '.npz':
                    scipy.savez(fullpath, **data_dict)

            elif file_format == 'cPickle' or file_format == 'cPickle.gz':
                data_dict = {'features':trial.clustered_features,
                        'feature_times':trial.clustered_feature_times}
                if file_format == 'cPickle.gz':
                    outfile = gzip.open(fullpath, 'wb')
                    cPickle.dump(data_dict, outfile, protocol=-1)
                    outfile.close()
                else:
                    with open(fullpath, 'wb') as outfile:
                        cPickle.dump(data_dict, outfile, protocol=-1)

            elif file_format == '.csv' or file_format == '.txt':
                cfal = trial.clustered_features_as_list
                cftal = trial.clustered_feature_times_as_list
                # cluster ids
                # nc (Number of clusters)
                # nc rows of feature_times
                # nc sets of:
                #    ne (Number of events within this cluster)
                #    ne rows of feature values (1 row per event)
                delimiters = {'.csv':',', '.txt':' '}
                delimiter = delimiters[file_format]
                nc = len(cfal)
                with open(fullpath, 'wb') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter)
                    writer.writerow(trial.clustered_features.keys())
                    writer.writerow([nc])
                    for clustered_times in cftal:
                        writer.writerow(clustered_times)

                    for clustered_features in cfal:
                        writer.writerow([len(clustered_features)])
                        for feature in clustered_features:
                            writer.writerow(feature)
        return fullpaths
            
        
