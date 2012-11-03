
import numpy
import scipy
from scipy.stats import chi2
import pylab

from spikepy.utils.mahalanobis_distance import mahalanobis_squared 

def make_test_data(seed_vector, variances, num_samples):
    data = numpy.empty((num_samples, len(seed_vector)), dtype=seed_vector.dtype)
    for i, (mu, var) in enumerate(zip(seed_vector, variances)):
        data[:,i] = numpy.random.normal(mu, var, num_samples)
    return data
    
ndims = 4
seed_vector = numpy.random.normal(0.0, 1.0, 4)
variances = numpy.random.normal(1.0, 0.05, 4)

df = len(seed_vector)

test_data = make_test_data(seed_vector, variances, 10000)

'''
for td in test_data:
    pylab.plot(td, color='k')

pylab.show()
'''

m = mahalanobis_squared(test_data, test_data)
xs = numpy.sort(m)
ys = numpy.arange(len(xs))/float(len(xs))

pylab.plot(xs, ys)

pylab.plot(xs, chi2.cdf(xs, df))

pylab.show()
