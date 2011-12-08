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
import numpy

import bisect

def downsample_for_plot(signal, times, tmin, tmax, num_samples=2000):
    '''
        Downsamples the signal into num_samples.  For each new sample point, 
    the min and max are determined and both are put into the downsampled 
    signal.  This preserves extrema in the downsampled signal.
    Returns:
        new_signal: shape=(signal.shape[0], 2*num_chunks)
            *note* num_chunks is approximately num_samples
        new_times: The time corresponding to each point in new_signal.
    '''
    # slice down to the region of interest
    imin = bisect.bisect_left(times, tmin)
    if imin > 0:
        imin -= 1 # get previous point, even if not plotted
    imax = bisect.bisect_right(times, tmax) + 1

    signal_slice = signal.T[imin:imax].T # .T is in case signal.ndim == 2
    times_slice = times[imin:imax]

    # construct new times
    slice_len = len(signal_slice.T)
    if slice_len < 2*num_samples:
        return signal_slice, times_slice

    chunk_size = slice_len/num_samples
    times_list = times_slice[::chunk_size]
    num_chunks = len(times_list)
    new_times = numpy.empty(num_chunks*2, dtype=times.dtype)
    for i in xrange(num_chunks):
        new_times[2*i]    = times_list[i]
        new_times[2*i+1]  = times_list[i]

    if signal.ndim == 1:
        new_signal = numpy.empty(num_chunks*2, dtype=signal.dtype)
        for i in xrange(num_chunks):
            start = i*chunk_size
            end   = start+chunk_size
            chunk_min = numpy.min(signal_slice[start:end])
            chunk_max = numpy.max(signal_slice[start:end])
            new_signal[2*i]   = chunk_min
            new_signal[2*i+1] = chunk_max
    elif signal.ndim == 2:
        new_signal = numpy.empty((signal.shape[0], num_chunks*2), 
                dtype=signal.dtype)
        for r in xrange(len(signal)):
            for i in xrange(num_chunks):
                start = i*chunk_size
                end   = start+chunk_size
                chunk_min = numpy.min(signal_slice[r, start:end])
                chunk_max = numpy.max(signal_slice[r, start:end])
                new_signal[r, 2*i]   = chunk_min
                new_signal[r, 2*i+1] = chunk_max
    else:
        raise RuntimeError(
                'Cannot downsample signal of more than 2 dimensions.')

    return new_signal, new_times
