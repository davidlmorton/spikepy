

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

