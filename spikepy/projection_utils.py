
import itertools

import numpy
from scipy import integrate

def get_projection_combinations(keys):
    pc = list()
    for i, j in itertools.product(keys, keys):
        if i != j:
            s = (i, j)
            st = (j, i)
            if s not in pc and st not in pc:
                pc.append(s)
    return pc

def num_projection_combinations(n):
    assert n > 0
    if n > 2:
        return (n-1) + num_projection_combinations(n-1)
    elif n == 2:
        return 1
    elif n == 1:
        return 0

def center(cluster):
    '''
    Returns a vector pointing to the center of a cluster.
    '''
    return numpy.average(cluster, axis=0)

def get_projection_vector(c1, c2):
    '''
    Returns the normalized vector pointing from
    the center of c1 to the center of c2.
    '''
    pv = center(c2)-center(c1)
    return pv/numpy.linalg.norm(pv)

def projection(c1, c2):
    '''
    Return the projections of the vectors in c1-center(c1) and
    c2-center(c1), onto the vector going from c1 to c2.
    '''
    cc1 = c1-center(c1)
    cc2 = c2-center(c1)
    pv = get_projection_vector(c1, c2)
    p1 = numpy.dot(cc1, pv)
    p2 = numpy.dot(cc2, pv)
    return p1, p2

def gaussian(center,peak,width,x):
    # simple normal distribution function with center offset
    return peak * numpy.exp(-(x-center)**2/width**2)

def normal( mu, std, x ):
    # the normal distribution
    peak = (   1/(std*numpy.sqrt(2*numpy.pi))  ) 
    width = numpy.sqrt(2)*std
    return gaussian( mu, peak, width, x )

def get_gaussian(projection, xs=[-5, 5, 100]):
    '''
    Returns a gaussian that describes the distribution
    of projections provided.
    '''
    mu = numpy.average(projection)
    std  = numpy.std(projection) 
    x_values = numpy.linspace(*xs)
    y_values = normal(mu, std, x_values)
    return x_values, y_values

def get_both_gaussians(p1, p2, num_points):
    '''
    Returns gaussians for the two projection distributions.  The
    larger of the two will have a peak value of 1.0.
    '''
    lb, ub = get_bounds(p1, p2)
    xs = [lb, ub, num_points]
    x, g1y = get_gaussian(p1, xs=xs)
    x, g2y = get_gaussian(p2, xs=xs)
    g1y *= len(p1)
    g2y *= len(p2)
    max_y = numpy.max(numpy.hstack([g1y, g2y]))
    return x, g1y/max_y, g2y/max_y

def get_min_normal(mus, stds):
    return lambda x: min([normal(m, s, x) for m, s in zip(mus, stds)]) 

def get_bounds(*args):
    mus = [numpy.average(p) for p in args]
    stds = [numpy.std(p) for p in args]
    lower_bounds = [m-8*s for m, s in zip(mus, stds)]
    upper_bounds = [m+8*s for m, s in zip(mus, stds)]
    lb = min(lower_bounds)
    ub = max(upper_bounds)
    return lb, ub

def get_overlap(*args):
    '''
    Return the integral of the overlap of the gaussians
    that best describe the supplied data sets.
    '''
    mus = [numpy.average(p) for p in args]
    stds = [numpy.std(p) for p in args]
    lb, ub = get_bounds(*args)
    return integrate.quad(get_min_normal(mus, stds), lb, ub)[0]
