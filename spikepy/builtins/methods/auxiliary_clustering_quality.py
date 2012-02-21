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

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.utils.clustering_metrics.calculate_clustering_metrics import\
        calculate_clustering_metrics

class ClusteringQuality(AuxiliaryMethod):
    '''
    This class implements a method to calculate clustering quality.
    '''
    name = "Calculate Clustering Quality"
    description = "Generate clustering quality metrics."
    runs_with_stage = 'auxiliary'
    is_stochastic = False
    is_pooling = True
    silent_pooling = True
    requires = ['clusters', 'features']
    provides = ['cluster_quality_metrics']
    unpool_as = None

    def run(self, clusters, features, **kwargs):
        return [calculate_clustering_metrics(clusters, features)]

