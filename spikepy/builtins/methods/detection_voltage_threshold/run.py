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

from .two_threshold_spike_find import two_threshold_spike_find

def run(trace_list, sampling_freq, threshold_1=None, 
                                   threshold_2=None,
                                   using_sd_units=None,
                                   refractory_time=None,
                                   max_spike_duration=None):
    
    if(threshold_1        is None or
       threshold_2        is None or
       using_sd_units     is None or
       refractory_time    is None or
       max_spike_duration is None):
        raise RuntimeError("keyword arguments to run are NOT optional.")
    else:
        if using_sd_units:
            std = numpy.std(trace_list)
        else:
            std = 1
        threshold_1 *= std 
        threshold_2 *= std 
        
        # convert times to samples (times in ms)
        refractory_period = (refractory_time/1000.0)*sampling_freq
        max_spike_width  = (max_spike_duration/1000.0)*sampling_freq
        dt = (1.0/sampling_freq)*1000.0 # in ms
        spike_list = []
        for trace in trace_list:
            result = two_threshold_spike_find(trace, threshold_1, 
                                              threshold_2=threshold_2,
                                            refractory_period=refractory_period,
                                            max_spike_width=max_spike_width)
            result = numpy.array(result)*dt
            spike_list.append(result)
        return spike_list


