from .two_threshold_spike_find import two_threshold_spike_find

def run(trace_list, sampling_freq, threshold_1=None, 
                                   threshold_2=None,
                                   refractory_time=None,
                                   max_spike_duration=None):
    print 'running'
    if(threshold_1        is None or
       threshold_2        is None or
       refractory_time    is None or
       max_spike_duration is None):
        raise RuntimeError("keyword arguments to run are NOT optional.")
    else:
        print 'else'
        # convert times to samples (times in ms)
        refractory_period = (refractory_time/1000.0)*sampling_freq
        max_spike_width  = (max_spike_duration/1000.0)*sampling_freq
        print refractory_period
        print max_spike_width
        spike_list = []
        for trace in trace_list:
            spike_list.append(two_threshold_spike_find(trace, threshold_1,
                                                              threshold_2,
                                                            refractory_period,
                                                            max_spike_width))
        return spike_list
            
            


