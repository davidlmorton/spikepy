
from scipy.cluster.vq import kmeans, vq
import numpy

from spikepy.developer.methods import ClusteringMethod
from spikepy.common.valid_types import ValidInteger, ValidOption

class ClusteringKMeans(ClusteringMethod):
    '''
    This class implements a k-means clustering method.
    '''
    name = 'K-means'
    description = 'K-means clustering algorithm with random initial centroids.'
    is_stochastic = True
    
    restarts = ValidInteger(1, 10000, default=10)
    choices = ['Use BIC'] + map(str, range(1, 21)) 
    number_of_clusters = ValidOption(*choices, default='3', description=
            'The number of clusters, or estimate the number of clusters via minimizing the Baysian Information Criterion.')

    def run(self, features, number_of_clusters='3', restarts=10):
        if number_of_clusters != 'Use BIC':
            k = int(number_of_clusters)
            if k == 1:
                result = numpy.zeros(len(features), dtype=numpy.int32)
                return [result]
            return [vq(features, kmeans(features, k, iter=restarts)[0])[0]]
        else:
            return [vq(features, bic_kmeans(features, iter=restarts)[0])[0]]

def bic_kmeans(features, **kwargs):
    '''
    Run kmeans on features with **kwargs given to scipy.cluster.vq.kmeans for
    different numbers of clusters, k.  Choose, finally, the clustering that
    minimizes the Beysian Information Criterion or BIC.
    '''
    max_k = int(2*numpy.log(len(features)))

    base_distances = vq(features, 
            numpy.array([numpy.average(features, axis=0)]))[1]
    base_std = numpy.std(base_distances)

    centers_list = []
    bic_list = []
    distances_list = []
    for k in range(1, max_k+1):
        centers = kmeans(features, k, **kwargs)[0]
        clusters, distances = vq(features, centers)
        bic = calculate_bic(clusters, distances, base_std)
        centers_list.append(centers)
        distances_list.append(distances)
        bic_list.append(bic)

    best_index = numpy.argmin(bic_list)
    return centers_list[best_index], distances_list[best_index]
            

def calculate_bic(clusters, distances, base_std):
    '''
    Calculates the most naive form of the BIC given the clusters (codebook) and
    the distances from the cluster centroids.
    '''
    cluster_ids = numpy.unique(clusters)

    variance = numpy.average(distances)
    first_term = len(clusters)*numpy.log(variance/base_std)

    k = len(cluster_ids) 
    second_term = k*numpy.log(len(clusters))
    print 'k', k
    print '1', first_term
    print '2', second_term
    return first_term + second_term


def get_clustered_data(clusters, data, cluster_id):
    '''
    Return the data which is part of cluster with cluster_id provided.
    Inputs:
        clusters: 1-d numpy array of integers
        data: n-d numpy array who's first dimension (len) is equal to 
                len(clusters)
        cluster_id: The particular cluster_id you want data for.
    '''
    return numpy.take(data, numpy.nonzero(clusters==cluster_id))
