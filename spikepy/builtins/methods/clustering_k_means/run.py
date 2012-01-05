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

import random
from collections import defaultdict

from scipy.cluster.vq import vq
import numpy

from .run_kmeans import run_kmeans
from spikepy.common.errors import FeatureDimensionalityError

def run(features, iterations=None, threshold=None, 
        number_of_clusters=None):
    # remove any trials with no features.
    non_zero_features = []
    for feature in features:
        if len(feature) > 0:
            non_zero_features.append(feature)

    # ensure feature dimensionality is uniform
    num_feature_dimensionalities = set([nzf.shape[-1] 
            for nzf in non_zero_features])
    if len(num_feature_dimensionalities) != 1:
        raise FeatureDimensionalityError('The dimensionality of the features of different trials do not match.  Instead of all being a single dimensionality your trials have features with dimensionality as follows.  %s' %
                str(list(num_feature_dimensionalities)))

    # pack into single array
    data = numpy.vstack(non_zero_features)
    if len(data) <= number_of_clusters:
        membership = range(len(data))
        distortions = [1.0 for i in range(len(data))]
    else:
        codebook, distortions = run_kmeans(number_of_clusters, data, 
                                     threshold=threshold, iterations=iterations)
        membership, distortions = vq(data, codebook)

    # determine the size of the clusters
    sizes = defaultdict(lambda :0)
    for m in membership:
        sizes[m] += 1
    # give new ids based on size
    si = numpy.argsort(sizes.values())
    new_ids = {}
    for i, rsi in enumerate(reversed(si)):
        new_ids[sizes.keys()[rsi]] = i
        
    sorted_membership = []
    for m in membership:
        sorted_membership.append(new_ids[m])
    membership = numpy.array(sorted_membership)

    # unpack results
    start = 0
    unpacked_membership = []
    unpacked_distortion = []
    for num_features in map(len, features):
        end = start + num_features
        unpacked_membership.append(membership[start:end])
        unpacked_distortion.append(distortions[start:end])
        start += num_features

    return [unpacked_membership, unpacked_distortion]

