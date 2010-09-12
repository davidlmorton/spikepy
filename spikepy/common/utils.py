import traceback
import csv
import sys

import numpy
from numpy.linalg import svd
from scipy.signal import resample

def pool_process(pool, function, args=tuple(), kwargs=dict()):
    if pool is not None:
        try:
            pool_result = pool.apply_async(function, args=args, kwds=kwargs)
            result = pool_result.get()
        except:
            traceback.print_exc()
            sys.exit(1)
    else:
        result = function(*args, **kwargs)
    return result

def upsample_trace_list(trace_list, prev_sample_rate, desired_sample_rate):
    '''
    Upsample voltage traces.
    Inputs:
        trace_list          : a list of voltage traces
        prev_sample_rate    : the sample rate in hz of the traces to be 
                              upsampled
        desired_sample_rate : the target sample rate of the traces
    Returns:
        a list of resampled traces
    '''
    rate_factor = desired_sample_rate/float(prev_sample_rate)
    return [resample(trace, len(trace)*rate_factor)
            for trace in trace_list]

def save_list_txt(filename, array_list, delimiter=' '):
    '''
    Save a list of 1D arrays (of potentially varying lengths) as a single text
    file.
    Inputs:
        array_list      : a list of 1D arrays of any length.
    Returns:
        None
    '''
    with open(filename, 'w') as ofile:
        writer = csv.writer(ofile, delimiter=delimiter)
        for array in array_list:
            writer.writerow(array)

def pca(P):
    """
    Use singular value decomposition to determine the optimal
    rotation of the basis to view data from.

    Input:
    P          : an m x n array of input data
                (m trials, n measurements)
                (m rows  , n columns)

    Return value are
    signals     : rotated view of the data.
    pc          : each row is a principal component
    var         : the variance associated with each pc
                   this is the bias corrected variance using 
                   m-1 instead of m.
    """
    # first we need to zero mean the data
    m,n = P.shape
    column_means = sum(P,0) / m
    zmP = P - column_means

    # generate the Y vector we will decompose
    Y = zmP / numpy.sqrt(m-1)

    # do the singular value decomposition
    u,s,pc = svd(Y)
    # find the variance along each principal axis
    var = s**2

    # The transformed data
    signals = numpy.dot(pc,P.T).T

    return signals, pc, var

