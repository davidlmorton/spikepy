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

import traceback
import csv
import sys

import numpy
from numpy.linalg import svd
from scipy import signal as scisig

from spikepy.common.config_manager import config_manager as config

def zero_mean(trace_array):
    return trace_array - numpy.average(trace_array)


def format_traces(trace_list):
    array_trace_list = [zero_mean(numpy.array(trace,dtype=numpy.float64))
                        for trace in trace_list]
    traces = numpy.vstack(array_trace_list)
    return traces

def pool_map(pool, function, iterable):
    if pool is not None:
        try:
            result = pool.map(function, iterable)
        except:
            traceback.print_exc()
            sys.exit(1)
    else:
        result = map(function, iterable)
    return result


def resample_signals(signals, prev_sample_rate, desired_sample_rate):
    '''
    Resample the signals.
    Inputs:
        signals          : a list of signals
        prev_sample_rate    : the sample rate in hz of the traces to be 
                              resampled
        desired_sample_rate : the target sample rate of the traces
    Returns:
        a list of resampled signals
    '''
    rate_factor = desired_sample_rate/float(prev_sample_rate)
    return [scisig.resample(signal, len(signal)*rate_factor)
            for signal in signals]

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

