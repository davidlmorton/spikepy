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

from scipy.cluster.vq import vq
import numpy

from .run_kmeans import run_kmeans

def run(features, iterations=None, threshold=None, 
        number_of_clusters=None):
    # pack into single array
    data = numpy.vstack(features)
    if len(data) <= number_of_clusters:
        membership = range(len(data))
        distortions = [1.0 for i in range(len(data))]
    else:
        codebook, distortions = run_kmeans(number_of_clusters, data, 
                                     threshold=threshold, iterations=iterations)
        membership, distortions = vq(data, codebook)

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

