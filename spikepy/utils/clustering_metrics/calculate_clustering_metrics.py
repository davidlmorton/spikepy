#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict

from spikepy.utils.cluster_data import cluster_data
from spikepy.utils.clustering_metrics.l_ratio import l_ratio
from spikepy.utils.clustering_metrics.isolation_distance import\
        isolation_distance
from spikepy.utils.clustering_metrics.mahalanobis_distance import\
        mahalanobis_squared


def clustered_mahalanobis_squared(clusters, features):
    clustered_features = cluster_data(clusters, features)

    return_dict = defaultdict(dict)
    for key in clustered_features.keys():
        this_cluster = clustered_features[key]
        for other_key in clustered_features.keys():
            other_cluster = clustered_features[other_key]
            return_dict[key][other_key] = mahalanobis_squared(other_cluster,
                    this_cluster, use_pseudo_inverse=True)
    return return_dict


def calculate_clustering_metrics(clusters, features):
    cmsd = clustered_mahalanobis_squared(clusters,features)
    isolation_distance_dict = isolation_distance(cmsd)
    clustering_metrics_dict = l_ratio(cmsd, features.shape[1])
    for key in clustering_metrics_dict.keys():
        clustering_metrics_dict[key]['mahalanobis_distances_squared'] =\
                cmsd[key]
        clustering_metrics_dict[key]['isolation_distance'] =\
                isolation_distance_dict[key]
    return clustering_metrics_dict
