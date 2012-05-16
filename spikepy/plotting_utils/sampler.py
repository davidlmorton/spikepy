"""
Copyright (C) 2012  David Morton

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
from collections import defaultdict
import random

from scipy.cluster.vq import kmeans, vq
import numpy

def sample_data(data, num_samples):
    '''
        Return a 'representative' sample of the data.
    Inputs:
        data: (samples, features) numpy array
        num_samples: integer > 0
    Returns:
        result: (min(<num_samples>, len(<data>), features) numpy array
    '''
    if num_samples >= len(data):
        return data
    else:
        # determine k
        k = min(25, num_samples)

        # cluster data
        clusters = vq(data, kmeans(data, k, iter=1)[0])[0]
        clustered_index_list = defaultdict(list)
        for i, c in enumerate(clusters):
            clustered_index_list[c].append(i)

        # pull data from clusters randomly.
        result = numpy.empty((num_samples, data.shape[1]), dtype=data.dtype)
        #  -- guarantee at least one element from each cluster --
        sample_index_set = set()
        for index_list in clustered_index_list.values():
            index = random.choice(index_list)
            result[len(sample_index_set)] = data[index]
            sample_index_set.add(index)

        while len(sample_index_set) < num_samples:
            cluster = random.choice(clustered_index_list.keys())
            index = random.choice(clustered_index_list[cluster])
            if index not in sample_index_set:
                result[len(sample_index_set)] = data[index]
                sample_index_set.add(index)
        return result
