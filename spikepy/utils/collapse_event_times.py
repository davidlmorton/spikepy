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
from spikepy.utils.fast_thresh_detect import fast_thresh_detect

def find_between(a, low, high):
    return a[numpy.where(numpy.where(a >= low, a, high+1) <= high)]

def collapse_event_times(signal, sampling_freq, event_times, 
        min_num_channels, peak_drift):
    if len(event_times) <= min_num_channels:
        result = numpy.hstack(event_times)
        result.sort()
        return result
    else:
        all_times = numpy.hstack(event_times)
        all_times.sort()

        peak_drift_samp = int(peak_drift*sampling_freq)
        if signal.ndim == 2:
            scores = numpy.zeros(signal.shape[1], dtype=numpy.int)
        else:
            scores = numpy.zeros(signal.shape, dtype=numpy.int)

        for time in all_times:
            mid = int(time*sampling_freq)
            begin = max(mid-peak_drift_samp, 0)
            end = min(len(scores)-1, mid+peak_drift_samp)
            scores[begin:end] = scores[begin:end] + 1

        scores[0] = 0
        scores[-1] = 0

        crossings = fast_thresh_detect(scores, min_num_channels-0.5)
        collapsed_event_times = []
        for up, down in zip(crossings[::2], crossings[1::2]):
            collapsed_event_times.append( (up+down)/2.0 / sampling_freq )

        return collapsed_event_times

