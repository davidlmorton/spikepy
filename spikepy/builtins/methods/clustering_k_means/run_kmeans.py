from scipy.cluster.vq import kmeans, vq
import numpy

def run_kmeans(k, data, threshold=1.000000000001e-8, iterations=30):
    '''
    This will run the kmeans clustering algorithm to determine possible 
        cluster centers in the data.  Initial cluster centers are chosen 
        randomly from the data and the kmeans algorithm is run until a 
        threshold is crossed.
    Inputs:
        k           : the number of clusters to try
        data        : a (n x m) numpy array of floats, where
                        n is the number of observations, or repetitions, 
                        or data points m is the dimensionality of the 
                        observations
        threshold   : the algorithm will stop when the distortion change 
                        between iterations is less than this value.
        iterations  : the number of times kmeans will run with new initial
                        conditions

    Returns:
        codebook     : the kmeans codebook
        distortions  : a list of distortions corresponding the the centers in
                         codebook
    '''
    # whiten the data
    stds = numpy.std(data, axis=0)
    wdata = data / stds 
    
    codebook, distortions = kmeans(wdata, k, iter=iterations, thresh=threshold)
    return codebook*stds, distortions
