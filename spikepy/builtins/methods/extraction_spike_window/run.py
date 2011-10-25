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

from collections import defaultdict

import numpy

from .window_spikes import window_spikes
from spikepy.utils.collapse_event_times import collapse_event_times 

def run(signal, sampling_freq, event_times,
            pre_padding=None,
            post_padding=None,
            min_num_channels=None,
            peak_drift=None,
            exclude_overlappers=None):
            # TODO MAKE ACCEPT LIST OF (LIST OF SPIKE TIMES).
    collapsed_event_times = collapse_event_times(signal, sampling_freq, 
            event_times, min_num_channels, peak_drift)
    pre_padding_percent = pre_padding/float(pre_padding+post_padding)
    # from sampling frequency (in Hz) and pre/post_padding (in ms) determine
    #     window_size (in samples)
    window_duration = (pre_padding + post_padding) / 1000.0 # now in secs
    # +1 to account for the sample itself.
    window_size = int(window_duration * sampling_freq) + 1 

    spike_index_list = collapsed_event_times*sampling_freq
    spike_index_list = numpy.array(spike_index_list, dtype=numpy.int32)
    (spike_windows, spike_indexes, excluded_windows, excluded_indexes) =\
            window_spikes(signal, spike_index_list, 
                    window_size=window_size, 
                    pre_padding=pre_padding_percent, 
                    exclude_overlappers=exclude_overlappers)
        
    return [numpy.vstack(spike_windows), 
            numpy.array(spike_indexes)/float(sampling_freq), 
            excluded_windows, 
            numpy.array(excluded_indexes)/float(sampling_freq)]
