import random

from scipy.cluster.vq import vq
import numpy

from .run_kmeans import run_kmeans

def run(feature_set_list, iterations=None, threshold=None, 
        number_of_clusters=None):
    if (iterations         is None or
        threshold          is None or
        number_of_clusters is None):
        raise RuntimeError("keyword arguments to run are NOT optional.")
    else:
        data = numpy.array(feature_set_list)
        codebook, distortions = run_kmeans(number_of_clusters, data, 
                                     threshold=threshold, iterations=iterations)
        membership, distortions = vq(data, codebook)
        return membership

