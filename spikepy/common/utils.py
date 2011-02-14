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
import gc
import math
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

def get_chunk(signal, chunk_num, window_len, overlap):
    d_chunk = window_len - overlap
    start = chunk_num*d_chunk
    end = start+window_len
    return signal[start:end]

def combine_chunks(signal_chunks, overlap, result):
    f_overlap = overlap/2
    b_overlap = overlap-f_overlap

    i = 0
    tc = signal_chunks[0][:-b_overlap]
    result[i:i+len(tc)] = tc
    i += len(tc)
    for chunk in signal_chunks[1:-1]:
        tc = chunk[f_overlap:-b_overlap]
        result[i:i+len(tc)] = tc
        i += len(tc)
    tc = signal_chunks[-1][f_overlap:]
    result[i:i+len(tc)] = tc
    
def resample_signal(signal, prev_sample_rate, desired_sample_rate,
                     window_len=2**12, overlap=32):
    '''
    Resample the signals.
    Inputs:
        signal              : the signal you want to resample
        prev_sample_rate    : the sample rate in hz of the traces to be 
                              resampled
        desired_sample_rate : the sample rate of the input will be multiplied
                              by the smallest integer that causes it to exceed
                              this number. i.e. prev_sample_rate=10,000 and
                              desired_sample_rate=25,000 then output will be
                              sampled at 30,000 (10,000 * 3) 
        *kwargs*
        window_len          : signal and times will be broken into chunks of 
                              this size.
        overlap             : the chunks will overlap this much.
    Returns:
        resampled signal and times
    '''
    rate_factor = int(math.ceil(desired_sample_rate/float(prev_sample_rate)))
    if rate_factor < 2:
        return signal
    result = numpy.empty(len(signal)*rate_factor, dtype=signal.dtype)

    # find out how many chunks there will be
    d_chunk = window_len - overlap
    rd_chunk = d_chunk*rate_factor
    num_chunks = int(math.ceil(len(signal)/float(d_chunk)))

    ri = 0
    f_overlap = (overlap*rate_factor)/2
    b_overlap = (overlap*rate_factor)-f_overlap

    # first chunk (no front overlap)
    c = get_chunk(signal, 0, window_len, overlap)
    r = scisig.resample(c, len(c)*rate_factor)[:-b_overlap]
    result[ri:ri+len(r)] = r
    ri += len(r)

    for i in range(1, num_chunks-1):
        result[ri:ri+rd_chunk] = scisig.resample(get_chunk(signal, i, 
            window_len, overlap), window_len*rate_factor)[f_overlap:-b_overlap]
        ri += rd_chunk

    # last chunk (no back overlap)
    c = get_chunk(signal, num_chunks-1, window_len, overlap)
    r = scisig.resample(c, len(c)*rate_factor)[f_overlap:]
    result[ri:ri+len(r)] = r

    return result

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

