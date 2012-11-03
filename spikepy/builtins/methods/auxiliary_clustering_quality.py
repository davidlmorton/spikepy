

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

