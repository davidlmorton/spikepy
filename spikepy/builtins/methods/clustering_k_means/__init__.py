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

from spikepy.developer_tools.methods import ClusteringMethod
from spikepy.common.valid_types import ValidInteger, ValidFloat
from .run import run as runner

class ClusteringKMeans(ClusteringMethod):
    '''
    This class implements a k-means clustering method.
    '''
    name = 'K-means'
    description = 'K-means clustering algorithm with random initial centroids.'
    is_stochastic = True

    iterations = ValidInteger(1, 10000, default=30)
    threshold = ValidFloat(1e-50, 1e10, default=1e-10)
    number_of_clusters = ValidInteger(1, 15, default=2)

    def run(self, feature_set_list, **kwargs):
        return runner(feature_set_list, **kwargs)

