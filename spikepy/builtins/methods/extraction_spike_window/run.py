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

def run(trace_list, sampling_freq, spike_list,
            pre_padding=None,
            post_padding=None,
            exclude_overlappers=None):
            # TODO MAKE ACCEPT LIST OF (LIST OF SPIKE TIMES).
    pre_padding_percent = pre_padding/float(pre_padding+post_padding)
    # from sampling frequency (in Hz) and pre/post_padding (in ms) determine
    #     window_size (in samples)
    window_duration = (pre_padding + post_padding) / 1000.0 # now in secs
    # +1 to account for the sample itself.
    window_size = int(window_duration * sampling_freq) + 1 

    waveforms          = defaultdict(list)
    excluded_waveforms = defaultdict(list)
    dt = (1.0/sampling_freq)*1000.0 # in ms
    spike_index_list = spike_list/dt
    spike_index_list = numpy.array(spike_index_list, dtype=numpy.int32)
    for trace in trace_list:
        results = window_spikes(trace, spike_index_list,
                window_size=window_size,
                pre_padding=pre_padding_percent,
                exclude_overlappers=exclude_overlappers)
        spike_windows    = results[0]
        spike_indexes    = results[1]
        excluded_windows = results[2]
        excluded_indexes = results[3]

        # collect waveforms from (potentially) multiple traces.
        for si, sw in zip(spike_indexes, spike_windows):
            waveforms[si].append(
                    numpy.array(sw, dtype=numpy.float64))
        for ei, ew in zip(excluded_indexes, excluded_windows):
            excluded_waveforms[ei].append(
                    numpy.array(ew, dtype=numpy.float64))

    # generate contents to be returned
    waveform_list  = []
    waveform_times = []
    for spike_index, waveform in waveforms.items():
        waveform_list.append(numpy.hstack(waveform))
        waveform_times.append(spike_index*dt) 

    excluded_waveform_list  = []
    excluded_waveform_times = []
    for spike_index, waveform in excluded_waveforms.items():
        excluded_waveform_list.append(numpy.hstack(waveform))
        excluded_waveform_times.append(spike_index*dt) 
        
    return [numpy.vstack(waveform_list), waveform_times, 
            excluded_waveform_list, excluded_waveform_times]
