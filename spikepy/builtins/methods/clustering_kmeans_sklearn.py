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
from sklearn.cluster import KMeans
import numpy

from spikepy.developer.methods import ClusteringMethod
from spikepy.common.valid_types import ValidInteger, ValidOption, ValidBoolean
from spikepy.common.config_manager import config_manager

class ClusteringKMeansSKLearn(ClusteringMethod):
    '''
    This class implements a k-means clustering method using the sklearn package.
    '''
    name = 'K-means (sklearn)'
    description = 'K-means clustering algorithm from the sklearn package.'
    is_stochastic = True
    
    restarts = ValidInteger(1, 10000, default=10)
    number_of_clusters = ValidInteger(1, 30, default=2, description=
            'The number of clusters that will be identified.')
    precompute_distances = ValidBoolean(default=True,
            description='Speeds up execution but uses more memory.')
    initialization = ValidOption('k-means++', 'random', default='k-means++', 
            description='How the centroids are initialized.')
    compute_in_parallel = ValidBoolean(default=True,
            description='Use multiple CPUs (based on settings in spikepy.ini)')

    def run(self, features, number_of_clusters=2, restarts=10, 
            precompute_distances=True, initialization='k-means++', 
            compute_in_parallel=True):
        if number_of_clusters == 1:
            result = numpy.zeros(len(features), dtype=numpy.int32)
            return [result]
        if compute_in_parallel:
            num_cpus = config_manager.get_num_workers()
        else:
            num_cpus = 1
        return [KMeans(k=number_of_clusters, init=initialization,
                n_init=restarts, precompute_distances=precompute_distances,
                n_jobs=num_cpus).fit_predict(features)]
