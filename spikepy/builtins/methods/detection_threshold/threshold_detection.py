#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy

from .two_threshold_spike_find import two_threshold_spike_find

def threshold_detection(signal, sampling_freq, threshold_1=None, 
                                   threshold_2=None,
                                   threshold_units=None,
                                   refractory_time=None,
                                   max_spike_duration=None):
    
    
    # convert times to samples (times in ms)
    refractory_period = (refractory_time/1000.0)*sampling_freq
    max_spike_width  = (max_spike_duration/1000.0)*sampling_freq
    if signal.ndim == 2:
        results = []
        for i in range(len(signal)):
            # determine thresholds
            if threshold_units.lower() == 'standard deviation':
                factor = numpy.std(signal[i])
            elif threshold_units.lower() == 'median':
                factor = numpy.median(signal[i])
            else:
                factor = 1.0

            t1 = threshold_1 * factor
            t2 = threshold_2 * factor

            spikes = two_threshold_spike_find(signal[i], t1,
                    threshold_2=t2,
                    refractory_period=refractory_period,
                    max_spike_width=max_spike_width)
            if len(spikes) > 0:
                results.append(spikes/float(sampling_freq))
            else:
                results.append([])
    else:
        # determine thresholds
        if threshold_units.lower() == 'standard deviation':
            factor = numpy.std(signal)
        elif threshold_units.lower() == 'median':
            factor = numpy.median(signal)
        else:
            factor = 1.0

        t1 = threshold_1 * factor
        t2 = threshold_2 * factor

        results = two_threshold_spike_find(signal, t1,
                threshold_2=t2,
                refractory_period=refractory_period,
                max_spike_width=max_spike_width)
        if len(results) > 0:
            results /= float(sampling_freq)
    return [results]

